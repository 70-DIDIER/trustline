"""Mode Vigie — sessions of locally-analysed calls.

Privacy contract (advertised in the app): **no audio and no transcript ever
leaves the phone**. The backend only serves the *catalogue of signals* to look
for (see :mod:`apps.vigie.services`), and stores the aggregate outcome of a
session: which signal codes fired, how long it lasted, the resulting score.
"""
from django.db import models

from apps.core.constants import NiveauRisque


class SessionVigie(models.Model):
    """The anonymised summary of one Mode Vigie listening session."""

    appareil = models.ForeignKey(
        "appareils.Appareil",
        on_delete=models.CASCADE,
        related_name="sessions_vigie",
    )
    duree_secondes = models.PositiveIntegerField(default=0)
    # Only the rule CODES that fired — never the words that triggered them.
    signaux = models.JSONField(default=list, blank=True)
    score = models.PositiveSmallIntegerField(default=0)
    niveau_risque = models.CharField(
        max_length=16,
        choices=NiveauRisque.choices,
        default=NiveauRisque.FAIBLE,
    )
    numero = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Numéro de l'appel, si l'utilisateur a choisi de le renseigner.",
    )
    date_session = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Session Mode Vigie"
        verbose_name_plural = "Sessions Mode Vigie"
        ordering = ["-date_session"]

    def __str__(self):
        return f"Vigie {self.date_session:%Y-%m-%d %H:%M} — {len(self.signaux)} signaux"