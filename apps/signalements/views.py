"""Endpoints for creating and following community reports."""
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appareils.services import exiger_appareil, resoudre_appareil
from apps.core.utils import formater_numero
from apps.signalements.models import Signalement
from apps.signalements.serializers import (
    CreerSignalementSerializer,
    SignalementCreeSerializer,
    SignalementSerializer,
)
from apps.signalements.services import creer_signalement


class CreerSignalementView(APIView):
    """POST /api/signalements/ — record a report and update reputation."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Signalements"],
        summary="Signaler un numéro / SMS / lien / site / message",
        description=(
            "L'application mobile s'identifie par l'en-tête `X-Device-Id` : le "
            "signalement est alors rattaché à l'appareil et visible dans "
            "`/api/signalements/mes/`. Les autres canaux (USSD, bot) passent "
            "`declarant_id`.\n\n"
            "La réponse contient une **référence** lisible et la réputation "
            "recalculée de la cible."
        ),
        request=CreerSignalementSerializer,
        responses={201: SignalementCreeSerializer},
        examples=[
            OpenApiExample(
                "Signaler un numéro (demande OTP)",
                value={
                    "type_cible": "numero",
                    "cible": "90112233",
                    "categorie": "demande_otp_pin",
                    "montant_perdu": 15000,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Signaler un lien de phishing",
                value={
                    "type_cible": "lien",
                    "cible": "http://ecobank-tg.xyz/login",
                    "categorie": "phishing",
                    "commentaire": "Reçu par SMS ce matin",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        entree = CreerSignalementSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        data = entree.validated_data

        # The device UUID is the reporter identity for the mobile app; other
        # channels (USSD, bot) keep passing an explicit declarant_id.
        appareil = resoudre_appareil(request)
        declarant = data.get("declarant_id") or ""
        if appareil is not None:
            declarant = appareil.declarant
        if not declarant:
            return Response(
                {
                    "declarant_id": [
                        "Fournissez declarant_id ou l'en-tête X-Device-Id."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        signalement, numero = creer_signalement(
            type_cible=data["type_cible"],
            cible=data["cible"],
            categorie_code=data["categorie"],
            declarant=declarant,
            commentaire=data.get("commentaire", ""),
            montant_perdu=data.get("montant_perdu"),
            appareil=appareil,
        )

        corps = SignalementSerializer(signalement).data
        corps["message"] = (
            "Merci, votre signalement a bien été enregistré. Il sera pondéré par "
            "la modération et par le nombre de déclarants distincts."
        )
        corps["reputation_cible"] = None
        if numero is not None:
            corps["reputation_cible"] = {
                "numero": numero.numero,
                "numero_formate": formater_numero(numero.numero),
                "score_risque": numero.score_risque,
                "niveau_risque": numero.niveau_risque,
                "nombre_signalements": numero.nombre_signalements,
            }
        return Response(corps, status=status.HTTP_201_CREATED)


class MesSignalementsView(ListAPIView):
    """GET /api/signalements/mes/ — reports sent by this device."""

    permission_classes = [AllowAny]
    serializer_class = SignalementSerializer

    @extend_schema(
        tags=["Signalements"],
        summary="Mes signalements (par appareil)",
        description=(
            "Liste paginée des signalements envoyés depuis cet appareil, avec "
            "leur statut de modération. Nécessite l'en-tête `X-Device-Id`."
        ),
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        appareil = exiger_appareil(self.request)
        return (
            Signalement.objects.filter(appareil=appareil)
            .select_related("categorie")
            .order_by("-date_creation")
        )