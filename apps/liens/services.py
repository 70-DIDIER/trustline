"""Heuristic analysis of a URL / website (used by the Chrome extension)."""
import re
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

_RECO = {
    NiveauRisque.FAIBLE: "Lien sans signal suspect évident. Vérifiez tout de même le domaine.",
    NiveauRisque.SUSPECT: "Lien suspect : ne saisissez aucun identifiant ni code sur ce site.",
    NiveauRisque.ELEVE: "Lien dangereux : n'ouvrez pas ce site, ne saisissez rien.",
}


def _normaliser_url(url: str) -> str:
    url = (url or "").strip()
    if url and not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "http://" + url
    return url


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
    url = _normaliser_url(url_brute)
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    chemin = (parsed.path or "") + (("?" + parsed.query) if parsed.query else "")

    points = 0
    indices = []

    if not host:
        return {
            "url": url_brute,
            "score": 0,
            "niveau_risque": NiveauRisque.FAIBLE,
            "indices": ["URL non analysable."],
            "recommandation": "Lien invalide ou incomplet.",
            "domaine": "",
        }

    # 1) Raw IP address instead of a domain.
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
        points += 40
        indices.append("Adresse IP brute au lieu d'un nom de domaine.")

    # 2) URL shortener (hides the real destination).
    if host in RACCOURCISSEURS:
        points += 35
        indices.append("Lien raccourci : la destination réelle est masquée.")

    # 3) Suspicious / free TLD.
    tld = host.rsplit(".", 1)[-1] if "." in host else ""
    if tld in TLD_SUSPECTS:
        points += 25
        indices.append(f"Extension de domaine peu fiable (.{tld}).")

    # 4) No HTTPS.
    if parsed.scheme == "http":
        points += 10
        indices.append("Connexion non sécurisée (http, pas https).")

    # 5) '@' in URL or many subdomains (obfuscation).
    if "@" in url:
        points += 25
        indices.append("Caractère « @ » dans l'URL (technique de tromperie).")
    if host.count(".") >= 3:
        points += 15
        indices.append("Nombre inhabituel de sous-domaines.")

    # 6) Punycode (homograph attack).
    if "xn--" in host:
        points += 20
        indices.append("Domaine en punycode (risque d'usurpation visuelle).")

    # 7) Brand name in subdomain/path but not the registered domain (typosquat).
    partie_domaine = ".".join(host.split(".")[-2:])
    for marque in MARQUES:
        if marque in host or marque in chemin.lower():
            if marque not in partie_domaine:
                points += 25
                indices.append(
                    f"Marque « {marque} » utilisée hors du domaine officiel (usurpation possible)."
                )
                break

    # 8) Community reputation on this URL / domain.
    score_reputation = _reputation_lien(url, host)
    if score_reputation:
        indices.append("Lien/domaine déjà signalé par la communauté.")

    score = clamp_score(max(points, score_reputation))
    niveau = niveau_from_score(score)
    if not indices:
        indices.append("Aucun signal suspect détecté sur ce lien.")

    verdict = {
        "url": url_brute,
        "score": score,
        "niveau_risque": niveau,
        "indices": indices,
        "recommandation": _RECO[niveau],
        "domaine": host,
    }
    enregistrer_log(TypeCible.LIEN, url, verdict, source=source)
    return verdict
