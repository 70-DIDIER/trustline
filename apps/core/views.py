"""Cross-cutting views (health check + unified extension endpoint)."""
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import serializers
from rest_framework.decorators import (
    api_view,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.liens.services import analyser_lien
from apps.messages.services import analyser_message
from apps.numeros.services import verifier_numero


@extend_schema(
    tags=["Système"],
    summary="Vérifier que le service tourne",
    responses={200: {"type": "object", "example": {"status": "ok", "service": "trustline"}}},
)
@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([])  # health check must never be rate-limited
def health(request):
    """Simple liveness endpoint used by the front-ends and monitoring."""
    return Response(
        {
            "status": "ok",
            "service": "trustline",
            "time": timezone.now().isoformat(),
        }
    )


class AnalyseExtensionSerializer(serializers.Serializer):
    """Entrée normalisée de l'extension navigateur (POST /api/extension/analyser/)."""

    type = serializers.ChoiceField(choices=["url", "message", "email", "phone"])
    content = serializers.CharField(max_length=5000, trim_whitespace=False)
    context = serializers.ChoiceField(
        choices=["whatsapp", "gmail", "outlook", "web", "popup"],
        required=False,
        default="web",
    )

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le contenu à analyser ne peut pas être vide.")
        return value


class AnalyseExtensionView(APIView):
    """Point d'entrée unique de l'extension : dispatch vers le moteur existant.

    Ne duplique aucune logique de détection : réutilise ``analyser_lien``,
    ``analyser_message`` et ``verifier_numero``. Le format de sortie reste le
    format natif du moteur (``niveau_risque`` en français) — l'extension le
    normalise côté client. On ajoute juste l'écho du ``type`` et du ``context``.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Système"],
        summary="Analyse unifiée pour l'extension (url / message / email / phone)",
        request=AnalyseExtensionSerializer,
        responses={200: {"type": "object"}},
        examples=[
            OpenApiExample(
                "Message WhatsApp suspect",
                value={"type": "message", "content": "Vous avez gagne 250000 FCFA, envoyez votre code", "context": "whatsapp"},
                request_only=True,
            ),
            OpenApiExample(
                "Lien depuis une page web",
                value={"type": "url", "content": "http://ecobank-tg.xyz/login", "context": "web"},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        entree = AnalyseExtensionSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        data = entree.validated_data
        source = f"extension:{data['context']}"

        if data["type"] == "url":
            verdict = analyser_lien(data["content"], source=source)
        elif data["type"] == "phone":
            verdict = verifier_numero(data["content"])
        else:  # message | email
            verdict = analyser_message(data["content"], source=source)

        verdict = {**verdict, "type": data["type"], "context": data["context"]}
        return Response(verdict)
