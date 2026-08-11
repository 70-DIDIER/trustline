"""Counters shared by the profile and home endpoints."""
from apps.core.constants import NiveauRisque, StatutSignalement
from apps.core.models import LogAnalyse
from apps.historique.models import Verification
from apps.numeros.models import Numero
from apps.signalements.models import Signalement
from apps.vigie.models import SessionVigie


def statistiques_appareil(appareil) -> dict:
    """Per-device counters. An unknown device simply gets zeros."""
    if appareil is None:
        return {
            "verifications": 0,
            "menaces_detectees": 0,
            "signalements": 0,
            "signalements_valides": 0,
            "sessions_vigie": 0,
        }

    verifications = Verification.objects.filter(appareil=appareil)
    signalements = Signalement.objects.filter(appareil=appareil)
    return {
        "verifications": verifications.count(),
        "menaces_detectees": verifications.filter(
            niveau_risque=NiveauRisque.ELEVE
        ).count(),
        "signalements": signalements.count(),
        "signalements_valides": signalements.filter(
            statut=StatutSignalement.VALIDE
        ).count(),
        "sessions_vigie": SessionVigie.objects.filter(appareil=appareil).count(),
    }


def statistiques_communaute() -> dict:
    """Platform-wide counters, identical for every user."""
    return {
        "signalements": Signalement.objects.count(),
        "numeros_suivis": Numero.objects.count(),
        "analyses": LogAnalyse.objects.count(),
        "numeros_risque_eleve": Numero.objects.filter(
            niveau_risque=NiveauRisque.ELEVE
        ).count(),
    }