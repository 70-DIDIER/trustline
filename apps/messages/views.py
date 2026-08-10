"""Endpoint for analysing a message / SMS."""
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.messages.serializers import (
    AnalyserMessageSerializer,
    VerdictMessageSerializer,
)
from apps.messages.services import analyser_message


class AnalyserMessageView(APIView):
    """POST /api/messages/analyser/ — verdict for a free-text message."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Messages"],
        summary="Analyser un SMS / message (moteur de règles)",
        request=AnalyserMessageSerializer,
        responses={200: VerdictMessageSerializer},
        examples=[
            OpenApiExample(
                "Faux gain + demande OTP (arnaque)",
                value={"contenu": "Felicitations! Vous avez gagne 500000 FCFA a la loterie MIXX. Envoyez votre code OTP pour retirer"},
                request_only=True,
            ),
            OpenApiExample(
                "Faux agent Mobile Money",
                value={"contenu": "Bonjour je suis agent Flooz, une erreur de depot a ete faite, renvoyez 15000 FCFA au 90112233"},
                request_only=True,
            ),
            OpenApiExample(
                "Message légitime",
                value={"contenu": "Salut, on se voit demain a 15h pour la reunion ?"},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        entree = AnalyserMessageSerializer(data=request.data)
        entree.is_valid(raise_exception=True)

        verdict = analyser_message(entree.validated_data["contenu"], source="api")
        return Response(VerdictMessageSerializer(verdict).data)
