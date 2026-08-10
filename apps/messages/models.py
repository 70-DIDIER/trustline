"""The Message model: an analysed SMS / message and its verdict."""
from django.db import models

from apps.core.constants import NiveauRisque


class Message(models.Model):
    """A message submitted for analysis, with its stored verdict."""

    contenu = models.TextField(verbose_name="Contenu du message")
    liens_extraits = models.JSONField(default=list, blank=True)
    numeros_extraits = models.JSONField(default=list, blank=True)
    score_risque = models.PositiveSmallIntegerField(default=0)
    verdict = models.CharField(
        max_length=16,
        choices=NiveauRisque.choices,
        default=NiveauRisque.FAIBLE,
    )
    indices_detectes = models.JSONField(default=list, blank=True)
    date_analyse = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "messages_app"
        verbose_name = "Message analysé"
        verbose_name_plural = "Messages analysés"
        ordering = ["-date_analyse"]

    def __str__(self):
        return f"[{self.verdict}] {self.contenu[:50]}"
