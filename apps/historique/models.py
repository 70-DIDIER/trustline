"""Per-device verification history.

Every analysis run from the mobile app (number, message, link, incoming call,
Mode Vigie) is stored here so the phone never has to keep its own copy: the
history survives a reinstall as long as the device keeps its anonymous UUID,
and the "Historique" screen simply reads this table.
"""
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from apps.core.constants import NiveauRisque


class TypeVerification(models.TextChoices):
    """What the user checked — mirrors the icons used by the mobile app."""

    NUMERO = "numero", "Numéro"
    MESSAGE = "message", "Message"
    LIEN = "lien", "Lien"
    APPEL = "appel", "Appel entrant"
    VIGIE = "vigie", "Mode Vigie"


class Verification(models.Model):
    """One entry of a device's verification history."""

    appareil = models.ForeignKey(
        "appareils.Appareil",
        on_delete=models.CASCADE,
        related_name="verifications",
    )
    type_verification = models.CharField(max_length=16, choices=TypeVerification.choices)
    cible = models.TextField(verbose_name="Contenu ou numéro vérifié")
    # Short label shown in the list (a message is truncated, a number formatted).
    resume = models.CharField(max_length=160, blank=True, default="")
    score = models.PositiveSmallIntegerField(default=0)
    niveau_risque = models.CharField(
        max_length=16,
        choices=NiveauRisque.choices,
        default=NiveauRisque.FAIBLE,
    )
    # Full verdict payload, so the detail screen can be reopened without
    # re-running the analysis. DjangoJSONEncoder handles the datetimes that
    # appear in number verdicts (date_dernier_signalement).
    verdict = models.JSONField(default=dict, blank=True, encoder=DjangoJSONEncoder)
    date_verification = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vérification"
        verbose_name_plural = "Vérifications"
        ordering = ["-date_verification"]
        indexes = [
            models.Index(fields=["appareil", "-date_verification"]),
        ]

    def __str__(self):
        return f"{self.type_verification}:{self.resume or self.cible[:40]}"