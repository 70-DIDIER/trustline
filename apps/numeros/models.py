"""The Numero model: a phone number with its community reputation."""
from django.db import models

from apps.core.constants import NiveauRisque
from apps.core.utils import normaliser_numero


class Numero(models.Model):
    """A phone number tracked by Trustline and its aggregated reputation."""

    numero = models.CharField(max_length=20, unique=True, verbose_name="Numéro")
    score_risque = models.PositiveSmallIntegerField(
        default=0, verbose_name="Score de risque (0-100)"
    )
    niveau_risque = models.CharField(
        max_length=16,
        choices=NiveauRisque.choices,
        default=NiveauRisque.FAIBLE,
        verbose_name="Niveau de risque",
    )
    nombre_signalements = models.PositiveIntegerField(
        default=0, verbose_name="Nombre de signalements"
    )
    date_dernier_signalement = models.DateTimeField(
        null=True, blank=True, verbose_name="Date du dernier signalement"
    )
    est_liste_blanche = models.BooleanField(
        default=False, verbose_name="Sur liste blanche"
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Numéro"
        verbose_name_plural = "Numéros"
        ordering = ["-score_risque", "-nombre_signalements"]

    def save(self, *args, **kwargs):
        self.numero = normaliser_numero(self.numero)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero} ({self.niveau_risque}, {self.score_risque})"
