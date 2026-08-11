"""Endpoints for the anonymous device identity, its profile and the home screen."""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appareils.serializers import (
    AccueilSerializer,
    EnregistrerAppareilSerializer,
    ProfilAppareilSerializer,
)
from apps.appareils.services import exiger_appareil, resoudre_appareil
from apps.appareils.stats import statistiques_appareil, statistiques_communaute
from apps.historique.models import Verification
from apps.historique.serializers import VerificationSerializer
from apps.veille.models import Alerte, Conseil
from apps.veille.serializers import AlerteSerializer, ConseilSerializer


def _profil(appareil) -> dict:
    return {
        "device_id": appareil.device_id,
        "plateforme": appareil.plateforme,
        "version_app": appareil.version_app,
        "membre_depuis": appareil.date_creation,
        "statistiques": statistiques_appareil(appareil),
        "communaute": statistiques_communaute(),
    }


class EnregistrerAppareilView(APIView):
    """POST /api/appareils/ — declare this installation on first launch."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Appareils"],
        summary="Enregistrer l'appareil (identité anonyme)",
        description=(
            "L'application génère un UUID au premier lancement, le stocke "
            "localement et l'envoie dans `X-Device-Id`. Aucune donnée "
            "personnelle n'est demandée : cet identifiant opaque sert "
            "uniquement à rattacher l'historique et les signalements.\n\n"
            "L'appel est idempotent — le relancer met simplement à jour la "
            "plateforme et la version."
        ),
        request=EnregistrerAppareilSerializer,
        responses={200: ProfilAppareilSerializer},
    )
    def post(self, request):
        appareil = exiger_appareil(request)
        entree = EnregistrerAppareilSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        data = entree.validated_data

        appareil.plateforme = data.get("plateforme") or appareil.plateforme
        appareil.version_app = data.get("version_app") or appareil.version_app
        appareil.langue = data.get("langue") or appareil.langue
        appareil.save(update_fields=["plateforme", "version_app", "langue"])

        return Response(
            ProfilAppareilSerializer(_profil(appareil)).data,
            status=status.HTTP_200_OK,
        )


class ProfilAppareilView(APIView):
    """GET /api/appareils/moi/ — profile + personal and community counters."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Appareils"],
        summary="Profil de l'appareil et compteurs",
        responses={200: ProfilAppareilSerializer},
    )
    def get(self, request):
        appareil = exiger_appareil(request)
        return Response(ProfilAppareilSerializer(_profil(appareil)).data)


class AccueilView(APIView):
    """GET /api/accueil/ — everything the home screen needs, in one round-trip."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Accueil"],
        summary="Agrégat de l'écran d'accueil",
        description=(
            "Compteurs de l'appareil, campagnes à la une, dernières "
            "vérifications et conseil du jour — en un seul appel, pour que "
            "l'accueil s'affiche d'un bloc sur une connexion lente.\n\n"
            "`X-Device-Id` est facultatif : sans lui, les compteurs personnels "
            "et l'historique sont vides, le reste est servi normalement."
        ),
        responses={200: AccueilSerializer},
    )
    def get(self, request):
        appareil = resoudre_appareil(request)

        alertes = (
            Alerte.objects.filter(active=True).select_related("categorie")[:3]
        )
        conseils = list(Conseil.objects.filter(actif=True)[:1])

        recentes = []
        if appareil is not None:
            recentes = Verification.objects.filter(appareil=appareil)[:3]

        return Response(
            {
                "statistiques": statistiques_appareil(appareil),
                "communaute": statistiques_communaute(),
                "alertes": AlerteSerializer(alertes, many=True).data,
                "conseil_du_jour": (
                    ConseilSerializer(conseils[0]).data if conseils else None
                ),
                "verifications_recentes": VerificationSerializer(
                    recentes, many=True
                ).data,
            }
        )