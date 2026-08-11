"""Shared choices and enumerations used across the Trustline backend.

Field values are kept in French to stay consistent with the project's
functional spec (cahier des charges).
"""
from django.db import models


class NiveauRisque(models.TextChoices):
    """Risk level exposed in every verdict."""

    FAIBLE = "faible", "Faible"
    SUSPECT = "suspect", "Suspect"
    ELEVE = "eleve", "Élevé"


class TypeCible(models.TextChoices):
    """What a report / analysis targets."""

    NUMERO = "numero", "Numéro"
    SMS = "sms", "SMS"
    LIEN = "lien", "Lien"
    SITE = "site", "Site"
    MESSAGE = "message", "Message"


class CategorieCode(models.TextChoices):
    """Canonical scam categories used by the rule engine and reports."""

    FRAUDE_FINANCIERE = "fraude_financiere", "Fraude financière"
    PHISHING = "phishing", "Phishing"
    FAUX_CONCOURS = "faux_concours", "Faux concours / faux gain"
    FAUX_RECRUTEMENT = "faux_recrutement", "Faux recrutement"
    USURPATION_IDENTITE = "usurpation_identite", "Usurpation d'identité"
    FAUX_SERVICE_CLIENT = "faux_service_client", "Faux service client"
    DEMANDE_OTP_PIN = "demande_otp_pin", "Demande de code OTP / PIN"
    AUTRE = "autre", "Autre"


class StatutSignalement(models.TextChoices):
    """Moderation lifecycle of a community report."""

    EN_ATTENTE = "en_attente", "En attente"
    VALIDE = "valide", "Validé"
    CONTESTE = "conteste", "Contesté"
    REJETE = "rejete", "Rejeté"


# The full list of category codes, handy for seeding the referential table.
CATEGORIES_PAR_DEFAUT = [
    (CategorieCode.FRAUDE_FINANCIERE, "Fraude financière"),
    (CategorieCode.PHISHING, "Phishing / hameçonnage"),
    (CategorieCode.FAUX_CONCOURS, "Faux concours ou promesse de gain"),
    (CategorieCode.FAUX_RECRUTEMENT, "Faux recrutement / fausse offre d'emploi"),
    (CategorieCode.USURPATION_IDENTITE, "Usurpation d'identité (service officiel)"),
    (CategorieCode.FAUX_SERVICE_CLIENT, "Faux service client / faux agent"),
    (CategorieCode.DEMANDE_OTP_PIN, "Demande de code OTP / PIN / mot de passe"),
    (CategorieCode.AUTRE, "Autre type d'arnaque"),
]
