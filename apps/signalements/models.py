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
    # Set when the report comes from the mobile app, so a user can follow the
    # moderation status of their own reports.
    appareil = models.ForeignKey(
        "appareils.Appareil",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="signalements",
    )
    # Human-readable receipt shown to the reporter ("Référence TL-2026-000042").
    reference = models.CharField(
        max_length=24,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Référence",
    )
    commentaire = models.TextField(blank=True, default="")
    montant_perdu = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Montant perdu (FCFA)",
        help_text="Facultatif — permet de chiffrer le préjudice des campagnes.",
    )
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

    def generer_reference(self) -> str:
        """Build the public receipt number. Requires the row to be saved."""
        return f"TL-{self.date_creation:%Y}-{self.pk:06d}"
