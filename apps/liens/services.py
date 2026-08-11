"""Heuristic analysis of a URL / website (mobile app + Chrome extension)."""
import re
import time
from urllib.parse import urlparse

from apps.core.constants import NiveauRisque, StatutSignalement, TypeCible
from apps.core.services import enregistrer_log
from apps.core.utils import clamp_score, niveau_from_score

RACCOURCISSEURS = {
    "bit.ly", "tinyurl.com", "cutt.ly", "is.gd", "t.co", "goo.gl",
    "rb.gy", "ow.ly", "buff.ly", "shorturl.at",
}

TLD_SUSPECTS = {
    "xyz", "top", "tk", "ml", "ga", "cf", "gq", "club", "online",
    "work", "click", "link", "loan", "zip", "review",
}

# Well-known brands often impersonated (typosquat detection in host/path).
MARQUES = [
    "mixx", "flooz", "moov", "togocom", "tmoney", "yas",
    "ecobank", "orabank", "boa", "coris", "orange", "mtn", "paypal",
    "visa", "western", "moneygram",
]

# Vocabulaire de mise en confiance qu'un escroc accole au nom d'une marque pour
# fabriquer un domaine crédible ("mixx-verification-tg", "flooz-securite").
_MOTS_APPAT = re.compile(
    r"verif|secur|login|connexion|compte|account|confirm|update|"
    r"support|service|client|officiel|recharge|paiement|payment",
    re.IGNORECASE,
)

_RECO = {
    NiveauRisque.FAIBLE: "Lien sans signal suspect évident. Vérifiez tout de même le domaine.",
    NiveauRisque.SUSPECT: "Lien suspect : ne saisissez aucun identifiant ni code sur ce site.",
    NiveauRisque.ELEVE: "Lien dangereux : n'ouvrez pas ce site, ne saisissez rien.",
}

_EXPLICATIONS = {
    NiveauRisque.FAIBLE: (
        "Aucun signal de phishing connu n'a été détecté sur cette adresse. Restez "
        "néanmoins attentif si le site vous demande vos identifiants ou un code."
    ),
    NiveauRisque.SUSPECT: (
        "Cette adresse présente des caractéristiques que l'on retrouve sur les "
        "pages de collecte d'identifiants. Elle peut être légitime, mais ne "
        "saisissez rien avant d'avoir vérifié le domaine caractère par caractère."
    ),
    NiveauRisque.ELEVE: (
        "Cette adresse cumule plusieurs marqueurs des pages frauduleuses : elle "
        "imite l'apparence d'un service légitime pour vous faire saisir vos "
        "identifiants, votre code ou vos données bancaires."
    ),
}

_ACTIONS = {
    NiveauRisque.FAIBLE: (
        "Vérifiez tout de même l'adresse dans la barre du navigateur avant toute saisie."
    ),
    NiveauRisque.SUSPECT: (
        "N'entrez ni identifiant ni code sur ce site. Accédez au service par son "
        "adresse officielle, que vous saisissez vous-même."
    ),
    NiveauRisque.ELEVE: (
        "N'entrez aucun identifiant, aucun code, aucune donnée bancaire sur ce "
        "site. Fermez la page et signalez le lien."
    ),
}


def _indice(code, libelle, poids, detail, categorie=""):
    return {
        "code": code,
        "libelle": libelle,
        "poids": poids,
        "detail": detail,
        "categorie": categorie,
    }


def _normaliser_url(url: str) -> str:
    url = (url or "").strip()
    if url and not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "http://" + url
    return url


# Suffixes publics en deux parties : "gouv.tg" n'est pas un sous-domaine de
# plus, c'est la racine du domaine. Sans cela, tout site institutionnel serait
# signalé à tort.
SUFFIXES_COMPOSES = {
    "gouv.tg", "gov.tg", "com.tg", "org.tg", "net.tg", "edu.tg",
    "co.uk", "com.ng", "com.gh", "co.ci", "com.bj",
}


def _profondeur_sous_domaines(host: str) -> int:
    """Nombre de niveaux au-dessus du domaine enregistré, hors « www. »."""
    if host.startswith("www."):
        host = host[4:]
    labels = host.split(".")
    if len(labels) >= 2 and ".".join(labels[-2:]) in SUFFIXES_COMPOSES:
        labels = labels[:-1]  # le suffixe composé compte pour un seul niveau
    return len(labels) - 1


def _reputation_lien(url: str, host: str) -> int:
    """Highest reputation contribution from reports on this URL / domain."""
    from apps.signalements.models import Signalement

    signalements = Signalement.objects.filter(
        type_cible__in=[TypeCible.LIEN, TypeCible.SITE]
    ).exclude(statut=StatutSignalement.REJETE)
    hits = 0
    for s in signalements:
        cible = (s.cible or "").lower()
        if host and host in cible:
            hits += 1
        elif url and url.lower() in cible:
            hits += 1
    if hits >= 3:
        return 80
    if hits == 2:
        return 55
    if hits == 1:
        return 35
    return 0


def analyser_lien(url_brute: str, source: str = "api") -> dict:
    """Analyse a URL and return a normalised verdict."""
    debut = time.perf_counter()
    url = _normaliser_url(url_brute)
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    chemin = (parsed.path or "") + (("?" + parsed.query) if parsed.query else "")

    points = 0
    indices = []

    if not host:
        return {
            "url": url_brute,
            "domaine": "",
            "score": 0,
            "niveau_risque": NiveauRisque.FAIBLE,
            "indices": [],
            "recommandation": "Lien invalide ou incomplet.",
            "explication": "Cette adresse n'a pas pu être analysée : elle est incomplète ou mal formée.",
            "action_recommandee": "Vérifiez l'adresse saisie, puis relancez l'analyse.",
            "categories": [],
            "confiance": 0.0,
            "duree_ms": int((time.perf_counter() - debut) * 1000),
        }

    # 1) Raw IP address instead of a domain.
    est_adresse_ip = bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host))
    if est_adresse_ip:
        points += 40
        indices.append(_indice(
            "adresse_ip_brute",
            "Adresse IP brute au lieu d'un nom de domaine.",
            40,
            "Les services légitimes publient un nom de domaine, pas une adresse "
            "IP. Une IP brute sert à échapper aux listes de blocage.",
            "phishing",
        ))

    # 2) URL shortener (hides the real destination).
    if host in RACCOURCISSEURS:
        points += 35
        indices.append(_indice(
            "url_raccourcie",
            "Lien raccourci : la destination réelle est masquée.",
            35,
            "Vous ne pouvez pas voir où ce lien mène avant de l'ouvrir. C'est le "
            "moyen le plus courant de faire passer une page frauduleuse.",
            "phishing",
        ))

    # 3) Suspicious / free TLD.
    tld = host.rsplit(".", 1)[-1] if "." in host else ""
    if tld in TLD_SUSPECTS:
        points += 25
        indices.append(_indice(
            "tld_suspect",
            f"Extension de domaine peu fiable (.{tld}).",
            25,
            "Cette extension est gratuite ou très bon marché : elle est "
            "massivement utilisée pour les campagnes de phishing jetables.",
            "phishing",
        ))

    # 4) No HTTPS.
    if parsed.scheme == "http":
        points += 10
        indices.append(_indice(
            "absence_https",
            "Connexion non sécurisée (http, pas https).",
            10,
            "Les données que vous saisiriez sur ce site circuleraient en clair "
            "sur le réseau.",
            "phishing",
        ))

    # 5) '@' in URL or many subdomains (obfuscation).
    if "@" in url:
        points += 25
        indices.append(_indice(
            "arobase_dans_url",
            "Caractère « @ » dans l'URL (technique de tromperie).",
            25,
            "Tout ce qui précède le « @ » est ignoré par le navigateur : le vrai "
            "domaine est celui qui suit, souvent très différent.",
            "phishing",
        ))
    # Les points d'une adresse IP ne sont pas des sous-domaines.
    if not est_adresse_ip and _profondeur_sous_domaines(host) >= 3:
        points += 15
        indices.append(_indice(
            "sous_domaines_multiples",
            "Nombre inhabituel de sous-domaines.",
            15,
            "Empiler les sous-domaines permet d'afficher un nom rassurant à "
            "gauche pendant que le vrai domaine, à droite, reste inconnu.",
            "phishing",
        ))

    # 6) Punycode (homograph attack).
    if "xn--" in host:
        points += 20
        indices.append(_indice(
            "domaine_punycode",
            "Domaine en punycode (risque d'usurpation visuelle).",
            20,
            "Le domaine contient des caractères non latins choisis pour "
            "ressembler visuellement à ceux d'un site connu.",
            "usurpation_identite",
        ))

    # 7) Brand impersonation, in two distinct shapes.
    partie_domaine = ".".join(host.split(".")[-2:])
    for marque in MARQUES:
        if marque not in host and marque not in chemin.lower():
            continue

        if marque not in partie_domaine:
            # 7a) The brand only appears in a subdomain or the path — the
            # registered domain belongs to someone else entirely.
            points += 25
            indices.append(_indice(
                "usurpation_marque",
                f"Marque « {marque} » utilisée hors du domaine officiel.",
                25,
                "Le nom de la marque apparaît dans l'adresse, mais pas dans "
                "le domaine réellement enregistré : c'est une imitation.",
                "usurpation_identite",
            ))
            break

        # 7b) The brand IS in the registered domain — the typosquat case, où
        # l'escroc achète « marque-verification.xyz ». Un domaine de marque
        # légitime ne cumule ni extension jetable ni vocabulaire de mise en
        # confiance : ces deux marqueurs font la différence.
        appat = _MOTS_APPAT.search(partie_domaine)
        if tld in TLD_SUSPECTS or appat:
            points += 35
            motif = (
                f"l'extension .{tld}, très utilisée pour le phishing"
                if tld in TLD_SUSPECTS
                else f"le mot « {appat.group(0)} » accolé au nom de la marque"
            )
            indices.append(_indice(
                "typosquat_marque",
                f"Domaine imitant « {marque} » ({partie_domaine}).",
                35,
                f"Le domaine reprend le nom de la marque mais y ajoute {motif}. "
                "Les vrais services financiers n'utilisent pas ce genre "
                "d'adresse : accédez au service par son adresse officielle, "
                "que vous saisissez vous-même.",
                "usurpation_identite",
            ))
        break

    # 8) Community reputation on this URL / domain.
    score_reputation = _reputation_lien(url, host)
    if score_reputation:
        indices.append(_indice(
            "reputation_communautaire",
            "Lien ou domaine déjà signalé par la communauté.",
            0,
            "D'autres utilisateurs ont signalé cette adresse comme frauduleuse.",
            "",
        ))

    score = clamp_score(max(points, score_reputation))
    niveau = niveau_from_score(score)

    categories = sorted({i["categorie"] for i in indices if i["categorie"]})
    confiance = round(min(0.55 + 0.09 * len(indices), 0.95), 2) if indices else 0.6

    verdict = {
        "url": url_brute,
        "domaine": host,
        "score": score,
        "niveau_risque": niveau,
        "indices": indices,
        "recommandation": _RECO[niveau],
        "explication": _EXPLICATIONS[niveau],
        "action_recommandee": _ACTIONS[niveau],
        "categories": categories,
        "confiance": confiance,
        "duree_ms": int((time.perf_counter() - debut) * 1000),
    }
    enregistrer_log(TypeCible.LIEN, url, verdict, source=source)
    return verdict