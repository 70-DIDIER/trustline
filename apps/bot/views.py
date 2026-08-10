"""Generic messaging-bot webhook.

Reuses the same message analysis as /api/messages/analyser/ but formats the
verdict for a conversational display (emoji + short text).
"""
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.constants import NiveauRisque
from apps.messages.services import analyser_message

_EMOJI = {
    NiveauRisque.FAIBLE: "✅",
    NiveauRisque.SUSPECT: "⚠️",
    NiveauRisque.ELEVE: "🚨",
}
_ENTETE = {
    NiveauRisque.FAIBLE: "Aucun danger évident",
    NiveauRisque.SUSPECT: "Message suspect",
    NiveauRisque.ELEVE: "Attention, arnaque probable",
}


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

        verdict = analyser_message(entree.validated_data["texte"], source="bot")
        niveau = verdict["niveau_risque"]

        lignes = [f"{_EMOJI[niveau]} {_ENTETE[niveau]} ({verdict['score']}/100)"]
        if verdict["indices"]:
            lignes.append("")
            lignes.extend(f"• {indice}" for indice in verdict["indices"])
        lignes.append("")
        lignes.append(verdict["recommandation"])

        return Response(
            {
                "reponse": "\n".join(lignes),
                "niveau_risque": niveau,
                "score": verdict["score"],
            }
        )
