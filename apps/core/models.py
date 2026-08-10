"""Shared referential models: scam categories, whitelist, analysis log."""
from django.db import models

from apps.core.constants import CategorieCode, NiveauRisque, TypeCible
from apps.core.utils import normaliser_numero


class CategorieArnaque(models.Model):
    """Referential of scam categories used by the rule engine and reports."""

    code = models.CharField(
        max_length=32,
        unique=True,
        choices=CategorieCode.choices,
        verbose_name="Code catégorie",
    )
    libelle = models.CharField(max_length=120, verbose_name="Libellé")
    description = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Catégorie d'arnaque"
        verbose_name_plural = "Catégories d'arnaque"
        ordering = ["libelle"]

    def __str__(self):
        return self.libelle


class ListeBlanche(models.Model):
    """Official protected numbers (banks, operators, administrations).

    A number on the whitelist is always trusted and short-circuits scoring.
    """

    numero = models.CharField(max_length=20, unique=True, verbose_name="Numéro")
    organisation = models.CharField(max_length=120, verbose_name="Organisation")
    source = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Source / justificatif",
    )
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Numéro liste blanche"
        verbose_name_plural = "Liste blanche"
        ordering = ["organisation", "numero"]

    def save(self, *args, **kwargs):
        self.numero = normaliser_numero(self.numero)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero} — {self.organisation}"


class LogAnalyse(models.Model):
    """Traceability of every analysis performed (dashboard & jury statistics)."""

    type_cible = models.CharField(max_length=16, choices=TypeCible.choices)
    cible = models.CharField(max_length=500, verbose_name="Cible analysée")
    score_risque = models.PositiveSmallIntegerField(default=0)
    niveau_risque = models.CharField(
        max_length=16,
        choices=NiveauRisque.choices,
        default=NiveauRisque.FAIBLE,
    )
    indices = models.JSONField(default=list, blank=True)
    source = models.CharField(
        max_length=32,
        blank=True,
        default="api",
        help_text="Canal d'origine : api, ussd, bot, extension…",
    )
    date_analyse = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log d'analyse"
        verbose_name_plural = "Logs d'analyse"
        ordering = ["-date_analyse"]

    def __str__(self):
        return f"[{self.date_analyse:%Y-%m-%d %H:%M}] {self.type_cible} → {self.niveau_risque}"
