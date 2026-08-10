"""Generic messaging-bot webhook.

Reuses the same message analysis as /api/messages/analyser/ but formats the
verdict for a conversational display (emoji + short text). The formatting logic
lives in apps/bot/services.py so it can be shared with the WhatsApp webhook.
"""
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bot.services import analyser_pour_bot
from apps.core.constants import NiveauRisque


class BotRequestSerializer(serializers.Serializer):
    texte = serializers.CharField(max_length=5000, trim_whitespace=False)
    utilisateur = serializers.CharField(required=False, default="bot-anonyme")


class BotResponseSerializer(serializers.Serializer):
    reponse = serializers.CharField()
    niveau_risque = serializers.ChoiceField(choices=NiveauRisque.choices)
    score = serializers.IntegerField()


class BotVerifierView(APIView):
    """POST /api/bot/verifier/ — analyse free text and reply conversationally."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Bot"],
        summary="Webhook bot : vérifier un texte libre",
        request=BotRequestSerializer,
        responses={200: BotResponseSerializer},
    )
    def post(self, request):
        entree = BotRequestSerializer(data=request.data)
        entree.is_valid(raise_exception=True)

        resultat = analyser_pour_bot(entree.validated_data["texte"], source="bot")
        return Response(resultat)
