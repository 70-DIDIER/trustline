"""Anonymous device identity.

The mobile application collects **no personal data**: on first launch it
generates a random UUID, stores it locally and sends it on every request in the
``X-Device-Id`` header. That opaque identifier is the only thing linking a
history entry or a report to "someone" — it carries no phone number, no
account, no address book.
"""
import uuid

from django.db import models


class Appareil(models.Model):
    """An anonymous installation of the mobile app."""

    class Plateforme(models.TextChoices):
        ANDROID = "android", "Android"
        IOS = "ios", "iOS"
        WEB = "web", "Web"
        AUTRE = "autre", "Autre"

    device_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Identifiant anonyme",
        help_text="UUID généré par l'application, sans lien avec l'identité réelle.",
    )
    plateforme = models.CharField(
        max_length=16,
        choices=Plateforme.choices,
        default=Plateforme.AUTRE,
    )
    version_app = models.CharField(max_length=32, blank=True, default="")
    langue = models.CharField(max_length=8, blank=True, default="fr")
    date_creation = models.DateTimeField(auto_now_add=True)
    derniere_activite = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Appareil"
        verbose_name_plural = "Appareils"
        ordering = ["-derniere_activite"]

    def __str__(self):
        return f"{self.plateforme}:{self.device_id}"

    @property
    def declarant(self) -> str:
        """Opaque reporter identifier used by the reputation engine."""
        return f"app-{self.device_id}"