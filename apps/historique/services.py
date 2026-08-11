"""Helpers to record a verification in a device's history."""
from apps.historique.models import TypeVerification, Verification

LONGUEUR_RESUME = 120


def _resumer(texte: str) -> str:
    texte = " ".join((texte or "").split())
    if len(texte) <= LONGUEUR_RESUME:
        return texte
    return texte[: LONGUEUR_RESUME - 1].rstrip() + "…"


def enregistrer_verification(appareil, *, type_verification, cible, verdict):
    """Persist one history entry. No-op (returns None) when there is no device.

    ``verdict`` is the normalised dict produced by the analysis services; the
    whole payload is stored so the mobile app can reopen a past result offline.
    """
    if appareil is None:
        return None

    return Verification.objects.create(
        appareil=appareil,
        type_verification=type_verification,
        cible=str(cible),
        resume=_resumer(str(cible)),
        score=verdict.get("score", 0),
        niveau_risque=verdict.get("niveau_risque", "faible"),
        verdict=verdict,
    )


__all__ = ["enregistrer_verification", "TypeVerification", "Verification"]