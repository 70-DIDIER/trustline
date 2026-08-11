"""Resolve the anonymous device behind a request."""
import uuid

from apps.appareils.models import Appareil

ENTETE_DEVICE = "HTTP_X_DEVICE_ID"
ENTETE_VERSION = "HTTP_X_APP_VERSION"


def lire_device_id(request):
    """Return the ``X-Device-Id`` header as a UUID, or None when absent/invalid."""
    brut = request.META.get(ENTETE_DEVICE) or request.headers.get("X-Device-Id")
    if not brut:
        return None
    try:
        return uuid.UUID(str(brut).strip())
    except (ValueError, AttributeError, TypeError):
        return None


def resoudre_appareil(request, creer: bool = True):
    """Return the :class:`Appareil` for this request (creating it on first sight).

    Returns ``None`` when the client sent no usable ``X-Device-Id`` — callers
    that need an identity raise 400 through
    :func:`apps.appareils.services.exiger_appareil`.
    """
    device_id = lire_device_id(request)
    if device_id is None:
        return None

    version = (request.META.get(ENTETE_VERSION) or "")[:32]

    if not creer:
        return Appareil.objects.filter(device_id=device_id).first()

    appareil, cree = Appareil.objects.get_or_create(
        device_id=device_id,
        defaults={"version_app": version},
    )
    # ``derniere_activite`` uses auto_now, so a plain save refreshes it.
    champs = ["derniere_activite"]
    if version and appareil.version_app != version:
        appareil.version_app = version
        champs.append("version_app")
    if not cree:
        appareil.save(update_fields=champs)
    return appareil


def exiger_appareil(request):
    """Like :func:`resoudre_appareil` but raises DRF ``ValidationError`` if absent."""
    from rest_framework.exceptions import ValidationError

    appareil = resoudre_appareil(request)
    if appareil is None:
        raise ValidationError(
            {
                "device_id": (
                    "En-tête X-Device-Id manquant ou invalide. L'application doit "
                    "envoyer l'UUID anonyme généré au premier lancement."
                )
            }
        )
    return appareil