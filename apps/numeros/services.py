"""Business logic for verifying a phone number.

The whitelist is always checked first. Results are cached so a repeat lookup
stays well under the 500 ms performance target.
"""
from django.core.cache import cache

from apps.core.constants import NiveauRisque, StatutSignalement
from apps.core.models import ListeBlanche
from apps.core.utils import normaliser_numero
from apps.numeros.models import Numero

CACHE_PREFIX = "numero_verdict:"
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


def _verdict_liste_blanche(numero, entree):
    return {
        "numero": numero,
        "score": 0,
        "niveau_risque": NiveauRisque.FAIBLE,
        "est_liste_blanche": True,
        "organisation": entree.organisation,
        "nombre_signalements": 0,
        "date_dernier_signalement": None,
        "categories": [],
        "indices": [f"Numéro officiel vérifié : {entree.organisation}."],
        "recommandation": (
            f"Numéro officiel de {entree.organisation}. Vous pouvez lui faire confiance, "
            "mais ne communiquez jamais un code OTP même à un service officiel."
        ),
    }


def _categories_du_numero(numero_obj):
    """Distinct scam category codes from a number's non-rejected reports."""
    codes = (
        numero_obj.signalements.exclude(statut=StatutSignalement.REJETE)
        .values_list("categorie__code", flat=True)
        .distinct()
    )
    return sorted(set(codes))


def verifier_numero(numero_brut: str) -> dict:
    """Return the full verdict for a phone number (whitelist-aware, cached)."""
    numero = normaliser_numero(numero_brut)

    cache_key = CACHE_PREFIX + numero
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # 1) Whitelist has absolute priority.
    entree = ListeBlanche.objects.filter(numero=numero).first()
    if entree is not None:
        verdict = _verdict_liste_blanche(numero, entree)
        cache.set(cache_key, verdict, CACHE_TTL)
        return verdict

    # 2) Known number -> use its stored reputation.
    numero_obj = Numero.objects.filter(numero=numero).first()
    if numero_obj is not None:
        niveau = numero_obj.niveau_risque
        indices = []
        if numero_obj.nombre_signalements:
            indices.append(
                f"{numero_obj.nombre_signalements} signalement(s) communautaire(s)."
            )
        verdict = {
            "numero": numero,
            "score": numero_obj.score_risque,
            "niveau_risque": niveau,
            "est_liste_blanche": False,
            "organisation": None,
            "nombre_signalements": numero_obj.nombre_signalements,
            "date_dernier_signalement": numero_obj.date_dernier_signalement,
            "categories": _categories_du_numero(numero_obj),
            "indices": indices or ["Aucun signalement enregistré."],
            "recommandation": _RECO[niveau],
        }
        cache.set(cache_key, verdict, CACHE_TTL)
        return verdict

    # 3) Unknown number -> neutral verdict.
    verdict = {
        "numero": numero,
        "score": 0,
        "niveau_risque": NiveauRisque.FAIBLE,
        "est_liste_blanche": False,
        "organisation": None,
        "nombre_signalements": 0,
        "date_dernier_signalement": None,
        "categories": [],
        "indices": ["Numéro inconnu de la base : aucun signalement à ce jour."],
        "recommandation": (
            "Numéro inconnu de notre base. Absence de signalement ne garantit pas "
            "la sécurité : restez vigilant."
        ),
    }
    cache.set(cache_key, verdict, CACHE_TTL)
    return verdict


def invalider_cache_numero(numero_brut: str):
    """Drop the cached verdict for a number (called after a new report)."""
    cache.delete(CACHE_PREFIX + normaliser_numero(numero_brut))
