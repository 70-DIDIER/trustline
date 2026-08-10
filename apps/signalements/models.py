"""The Signalement model: a single community report about a target."""
from django.db import models

from apps.core.constants import StatutSignalement, TypeCible
from apps.numeros.models import Numero


class Signalement(models.Model):
    """One community report. Reputation is computed by aggregating many of these."""

    type_cible = models.CharField(
        max_length=16, choices=TypeCible.choices, verbose_name="Type de cible"
    )
    cible = models.CharField(max_length=500, verbose_name="Cible signalée")
    # For numero-type reports we also link the aggregated Numero (reputation).
    numero_cible = models.ForeignKey(
        Numero,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="signalements",
        verbose_name="Numéro concerné",
    )
    categorie = models.ForeignKey(
        "core.CategorieArnaque",
        on_delete=models.PROTECT,
        related_name="signalements",
        verbose_name="Catégorie",
    )
    # Anonymised reporter identifier (no address-book / personal data collected).
    declarant = models.CharField(
        max_length=64,
        verbose_name="Déclarant (identifiant anonymisé)",
        help_text="Identifiant opaque du déclarant — aucune donnée personnelle.",
    )
    commentaire = models.TextField(blank=True, default="")
    statut = models.CharField(
        max_length=16,
        choices=StatutSignalement.choices,
        default=StatutSignalement.EN_ATTENTE,
        verbose_name="Statut de modération",
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"{self.type_cible}:{self.cible} → {self.categorie} ({self.statut})"
