"""Business logic for verifying a phone number.

The whitelist is always checked first. Results are cached so a repeat lookup
stays well under the 500 ms performance target.
"""
import time

from django.core.cache import cache

from apps.core.constants import NiveauRisque, StatutSignalement
from apps.core.models import ListeBlanche
from apps.core.utils import formater_numero, normaliser_numero
from apps.numeros.models import Numero

CACHE_PREFIX = "numero_verdict:v2:"
CACHE_TTL = 300  # seconds

_RECO = {
    NiveauRisque.FAIBLE: "Aucun signalement préoccupant. Restez tout de même vigilant.",
    NiveauRisque.SUSPECT: (
        "Numéro suspect : plusieurs signaux négatifs. Ne partagez ni code ni argent "
        "sans vérifier l'identité par un canal officiel."
    ),
    NiveauRisque.ELEVE: (
        "Numéro à haut risque : signalé par la communauté. N'envoyez aucun code ni "
        "argent et ne rappelez pas."
    ),
}

_ACTIONS = {
    NiveauRisque.FAIBLE: (
        "Aucune action particulière. Ne communiquez jamais un code reçu par SMS, "
        "même à un interlocuteur qui semble légitime."
    ),
    NiveauRisque.SUSPECT: (
        "Prudence : ne transmettez aucune information personnelle. Si l'appelant "
        "se réclame d'un service, rappelez ce service par son numéro officiel."
    ),
    NiveauRisque.ELEVE: (
        "Ne rappelez pas. Ne communiquez aucun code. Bloquez le numéro et "
        "signalez-le pour protéger les autres utilisateurs."
    ),
}


def _indice(code, libelle, poids=0, detail="", categorie=""):
    return {
        "code": code,
        "libelle": libelle,
        "poids": poids,
        "detail": detail,
        "categorie": categorie,
    }


def _verdict_liste_blanche(numero, entree, debut):
    return {
        "numero": numero,
        "numero_formate": formater_numero(numero),
        "score": 0,
        "niveau_risque": NiveauRisque.FAIBLE,
        "est_liste_blanche": True,
        "organisation": entree.organisation,
        "nombre_signalements": 0,
        "nombre_declarants": 0,
        "date_dernier_signalement": None,
        "categories": [],
        "indices": [
            _indice(
                "liste_blanche",
                f"Numéro officiel vérifié : {entree.organisation}.",
                detail=(
                    "Ce numéro figure dans la liste blanche des numéros publiés "
                    "par les opérateurs et institutions. Il ne peut pas être "
                    "dégradé par des signalements."
                ),
            )
        ],
        "recommandation": (
            f"Numéro officiel de {entree.organisation}. Vous pouvez lui faire confiance, "
            "mais ne communiquez jamais un code OTP même à un service officiel."
        ),
        "explication": (
            f"Ce numéro appartient à {entree.organisation} et figure dans la liste "
            "blanche officielle. Attention : un escroc peut afficher un numéro "
            "falsifié, donc un appel « officiel » ne vous demandera jamais votre code."
        ),
        "action_recommandee": (
            "Vous pouvez répondre. Ne communiquez jamais votre code PIN ou OTP, "
            "même à un service officiel : aucun ne vous le demandera."
        ),
        "confiance": 0.95,
        "duree_ms": int((time.perf_counter() - debut) * 1000),
    }


def _statistiques_signalements(numero_obj):
    """Distinct scam categories and distinct reporters from non-rejected reports."""
    lignes = numero_obj.signalements.exclude(
        statut=StatutSignalement.REJETE
    ).values_list("categorie__code", "declarant")
    categories = sorted({code for code, _ in lignes if code})
    declarants = {declarant for _, declarant in lignes if declarant}
    return categories, len(declarants)


def verifier_numero(numero_brut: str) -> dict:
    """Return the full verdict for a phone number (whitelist-aware, cached)."""
    debut = time.perf_counter()
    numero = normaliser_numero(numero_brut)

    cache_key = CACHE_PREFIX + numero
    cached = cache.get(cache_key)
    if cached is not None:
        # Timing is per-request, never cached.
        return {**cached, "duree_ms": int((time.perf_counter() - debut) * 1000)}

    # 1) Whitelist has absolute priority.
    entree = ListeBlanche.objects.filter(numero=numero).first()
    if entree is not None:
        verdict = _verdict_liste_blanche(numero, entree, debut)
        cache.set(cache_key, verdict, CACHE_TTL)
        return verdict

    # 2) Known number -> use its stored reputation.
    numero_obj = Numero.objects.filter(numero=numero).first()
    if numero_obj is not None:
        niveau = numero_obj.niveau_risque
        categories, nombre_declarants = _statistiques_signalements(numero_obj)

        indices = []
        if numero_obj.nombre_signalements:
            indices.append(_indice(
                "signalements_communautaires",
                f"{numero_obj.nombre_signalements} signalement(s) de la communauté.",
                detail=(
                    f"Ce numéro a été signalé par {nombre_declarants} personne(s) "
                    "distincte(s). Un seul déclarant ne suffit jamais à classer un "
                    "numéro en risque élevé."
                ),
            ))
        if nombre_declarants >= 3:
            indices.append(_indice(
                "declarants_multiples",
                "Signalé par plusieurs personnes indépendantes.",
                detail=(
                    "Des déclarants distincts qui ne se connaissent pas rapportent "
                    "le même comportement : le signal est solide."
                ),
            ))
        if len(categories) >= 2:
            indices.append(_indice(
                "categories_multiples",
                "Signalé pour plusieurs types d'arnaque.",
                detail=(
                    "Ce numéro est utilisé pour des scénarios variés, ce qui est "
                    "typique d'un numéro dédié à la fraude."
                ),
            ))
        if not indices:
            indices.append(_indice(
                "aucun_signalement",
                "Aucun signalement enregistré pour ce numéro.",
                detail=(
                    "Le numéro est connu de la base mais aucun signalement actif "
                    "ne pèse actuellement sur lui."
                ),
            ))

        verdict = {
            "numero": numero,
            "numero_formate": formater_numero(numero),
            "score": numero_obj.score_risque,
            "niveau_risque": niveau,
            "est_liste_blanche": False,
            "organisation": None,
            "nombre_signalements": numero_obj.nombre_signalements,
            "nombre_declarants": nombre_declarants,
            "date_dernier_signalement": numero_obj.date_dernier_signalement,
            "categories": categories,
            "indices": indices,
            "recommandation": _RECO[niveau],
            "explication": _explication_reputation(
                niveau, numero_obj.nombre_signalements, nombre_declarants
            ),
            "action_recommandee": _ACTIONS[niveau],
            "confiance": _confiance_reputation(nombre_declarants),
            "duree_ms": int((time.perf_counter() - debut) * 1000),
        }
        cache.set(cache_key, verdict, CACHE_TTL)
        return verdict

    # 3) Unknown number -> neutral verdict.
    verdict = {
        "numero": numero,
        "numero_formate": formater_numero(numero),
        "score": 0,
        "niveau_risque": NiveauRisque.FAIBLE,
        "est_liste_blanche": False,
        "organisation": None,
        "nombre_signalements": 0,
        "nombre_declarants": 0,
        "date_dernier_signalement": None,
        "categories": [],
        "indices": [
            _indice(
                "numero_inconnu",
                "Numéro inconnu de la base : aucun signalement à ce jour.",
                detail=(
                    "Personne n'a signalé ce numéro. Les numéros frauduleux "
                    "changent souvent : un numéro neuf est simplement un numéro "
                    "sur lequel nous n'avons encore rien."
                ),
            )
        ],
        "recommandation": (
            "Numéro inconnu de notre base. Absence de signalement ne garantit pas "
            "la sécurité : restez vigilant."
        ),
        "explication": (
            "Ce numéro n'est pas répertorié dans notre base de signalements. "
            "L'absence de signalement ne signifie pas l'absence de risque : les "
            "escrocs changent de numéro en permanence."
        ),
        "action_recommandee": (
            "Ne communiquez jamais un code reçu par SMS. Si l'interlocuteur se "
            "réclame d'un service, raccrochez et rappelez son numéro officiel."
        ),
        "confiance": 0.6,
        "duree_ms": int((time.perf_counter() - debut) * 1000),
    }
    cache.set(cache_key, verdict, CACHE_TTL)
    return verdict


def _explication_reputation(niveau, nombre_signalements, nombre_declarants) -> str:
    if niveau == NiveauRisque.ELEVE:
        return (
            f"Ce numéro a été signalé {nombre_signalements} fois par "
            f"{nombre_declarants} personnes distinctes. La convergence de "
            "déclarants indépendants sur un même numéro est le signal le plus "
            "fiable dont nous disposons."
        )
    if niveau == NiveauRisque.SUSPECT:
        return (
            f"Ce numéro fait l'objet de {nombre_signalements} signalement(s) "
            f"provenant de {nombre_declarants} déclarant(s). Le volume reste trop "
            "faible pour conclure : il est signalé comme suspect, pas comme "
            "frauduleux."
        )
    return (
        "Aucun signalement actif ne pèse sur ce numéro. Restez néanmoins vigilant : "
        "la réputation se construit avec le temps et les signalements."
    )


def _confiance_reputation(nombre_declarants: int) -> float:
    """More independent reporters → more confidence in the reputation verdict."""
    return round(min(0.55 + 0.1 * nombre_declarants, 0.95), 2)


def invalider_cache_numero(numero_brut: str):
    """Drop the cached verdict for a number (called after a new report)."""
    cache.delete(CACHE_PREFIX + normaliser_numero(numero_brut))