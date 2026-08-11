"""Editorial content served to the mobile app: live campaigns and prevention tips.

Both models are curated from the back-office (Django admin or the admin REST
API). ``Alerte`` describes a scam campaign currently circulating; ``Conseil``
is a prevention card shown in the "Conseils de sécurité" screen.
"""
from django.db import models
from django.utils import timezone

from apps.core.constants import NiveauRisque


class Alerte(models.Model):
    """A scam campaign currently observed on the ground."""

    class Canal(models.TextChoices):
        SMS = "sms", "SMS"
        APPEL = "appel", "Appel"
        LIEN = "lien", "Lien / site"
        MESSAGERIE = "messagerie", "Messagerie (WhatsApp…)"
        RESEAUX = "reseaux", "Réseaux sociaux"
        MIXTE = "mixte", "Multicanal"

    titre = models.CharField(max_length=160)
    description = models.TextField()
    # Optional "what to do" block shown at the bottom of the alert card.
    recommandation = models.TextField(blank=True, default="")
    niveau_risque = models.CharField(
        max_length=16,
        choices=NiveauRisque.choices,
        default=NiveauRisque.SUSPECT,
    )
    canal = models.CharField(max_length=16, choices=Canal.choices, default=Canal.MIXTE)
    categorie = models.ForeignKey(
        "core.CategorieArnaque",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="alertes",
    )
    # Manual counter: campaigns are often confirmed by field reports that are
    # not all in the database yet.
    nombre_signalements = models.PositiveIntegerField(default=0)
    epinglee = models.BooleanField(
        default=False,
        verbose_name="Épinglée",
        help_text="Remonte l'alerte en tête de liste et sur l'écran d'accueil.",
    )
    active = models.BooleanField(default=True)
    date_debut = models.DateTimeField(default=timezone.now)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
        ordering = ["-epinglee", "-date_debut"]

    def __str__(self):
        return self.titre


class Conseil(models.Model):
    """A prevention card ("cinq réflexes essentiels")."""

    titre = models.CharField(max_length=160)
    resume = models.CharField(max_length=400)
    points = models.JSONField(
        default=list,
        blank=True,
        help_text="Liste de phrases courtes affichées en puces.",
    )
    # Material icon name resolved by the mobile app (see IconesConseil).
    icone = models.CharField(max_length=40, blank=True, default="shield")
    categorie = models.ForeignKey(
        "core.CategorieArnaque",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="conseils",
    )
    ordre = models.PositiveSmallIntegerField(default=0)
    actif = models.BooleanField(default=True)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Conseil de sécurité"
        verbose_name_plural = "Conseils de sécurité"
        ordering = ["ordre", "id"]

    def __str__(self):
        return self.titre