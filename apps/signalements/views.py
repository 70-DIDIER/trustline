"""Endpoint for creating community reports."""
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.signalements.serializers import (
    CreerSignalementSerializer,
    SignalementSerializer,
)
from apps.signalements.services import creer_signalement


class CreerSignalementView(APIView):
    """POST /api/signalements/ — record a report and update reputation."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Signalements"],
        summary="Signaler un numéro / SMS / lien / site / message",
        request=CreerSignalementSerializer,
        responses={201: SignalementSerializer},
        examples=[
            OpenApiExample(
                "Signaler un numéro (demande OTP)",
                value={
                    "type_cible": "numero",
                    "cible": "90112233",
                    "categorie": "demande_otp_pin",
                    "declarant_id": "user-42",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Signaler un lien de phishing",
                value={
                    "type_cible": "lien",
                    "cible": "http://ecobank-tg.xyz/login",
                    "categorie": "phishing",
                    "declarant_id": "user-77",
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

        signalement, numero = creer_signalement(
            type_cible=data["type_cible"],
            cible=data["cible"],
            categorie_code=data["categorie"],
            declarant=data["declarant_id"],
            commentaire=data.get("commentaire", ""),
        )

        corps = SignalementSerializer(signalement).data
        corps["message"] = "Merci, votre signalement a bien été enregistré."
        if numero is not None:
            corps["reputation_cible"] = {
                "numero": numero.numero,
                "score_risque": numero.score_risque,
                "niveau_risque": numero.niveau_risque,
                "nombre_signalements": numero.nombre_signalements,
            }
        return Response(corps, status=status.HTTP_201_CREATED)
