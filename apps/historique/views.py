"""Endpoints exposing a device's own verification history."""
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appareils.services import exiger_appareil
from apps.historique.models import TypeVerification, Verification
from apps.historique.serializers import VerificationSerializer


@extend_schema(
    tags=["Historique"],
    summary="Historique des vérifications de l'appareil",
    description=(
        "Liste paginée, la plus récente d'abord. Nécessite l'en-tête "
        "`X-Device-Id`. Filtrable par type de vérification."
    ),
    parameters=[
        OpenApiParameter(
            name="type",
            description="Filtrer : numero, message, lien, appel, vigie.",
            required=False,
            type=str,
            enum=[c.value for c in TypeVerification],
        ),
        OpenApiParameter(
            name="niveau",
            description="Filtrer par niveau de risque : faible, suspect, eleve.",
            required=False,
            type=str,
        ),
    ],
)
class HistoriqueListView(ListAPIView):
    """GET /api/historique/ — this device's past verifications."""

    permission_classes = [AllowAny]
    serializer_class = VerificationSerializer

    def get_queryset(self):
        appareil = exiger_appareil(self.request)
        queryset = Verification.objects.filter(appareil=appareil)

        type_demande = self.request.query_params.get("type")
        if type_demande in TypeVerification.values:
            queryset = queryset.filter(type_verification=type_demande)

        niveau = self.request.query_params.get("niveau")
        if niveau:
            queryset = queryset.filter(niveau_risque=niveau)

        return queryset


class HistoriqueDetailView(APIView):
    """DELETE /api/historique/{id}/ — remove one entry."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Historique"],
        summary="Supprimer une entrée d'historique",
        responses={204: None},
    )
    def delete(self, request, pk):
        appareil = exiger_appareil(request)
        supprimes, _ = Verification.objects.filter(
            pk=pk, appareil=appareil
        ).delete()
        if not supprimes:
            return Response(
                {"detail": "Entrée introuvable pour cet appareil."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class HistoriqueViderView(APIView):
    """DELETE /api/historique/vider/ — wipe the device's whole history."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Historique"],
        summary="Vider tout l'historique de l'appareil",
        description="Action irréversible, déclenchée depuis l'écran Profil.",
        responses={200: None},
    )
    def delete(self, request):
        appareil = exiger_appareil(request)
        supprimes, _ = Verification.objects.filter(appareil=appareil).delete()
        return Response({"supprimes": supprimes})