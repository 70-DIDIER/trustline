"""Endpoint for analysing a URL / website (mobile app + Chrome extension)."""
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appareils.services import resoudre_appareil
from apps.historique.models import TypeVerification
from apps.historique.services import enregistrer_verification
from apps.liens.serializers import AnalyserLienSerializer, VerdictLienSerializer
from apps.liens.services import analyser_lien


class AnalyserLienView(APIView):
    """POST /api/liens/analyser/ — verdict for a URL."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Liens"],
        summary="Analyser un lien / site (heuristiques + réputation)",
        description=(
            "Même format de verdict que l'analyse de message : `indices` structurés, "
            "`explication` et `action_recommandee`.\n\n"
            "Envoyez `X-Device-Id` pour historiser l'analyse."
        ),
        request=AnalyserLienSerializer,
        responses={200: VerdictLienSerializer},
        examples=[
            OpenApiExample(
                "Lien raccourci (suspect)",
                value={"url": "http://bit.ly/gagnez-argent"},
                request_only=True,
            ),
            OpenApiExample(
                "Usurpation de banque (typosquat)",
                value={"url": "http://ecobank-tg.xyz/login"},
                request_only=True,
            ),
            OpenApiExample(
                "Site normal",
                value={"url": "https://www.togocom.tg"},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        entree = AnalyserLienSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        url = entree.validated_data["url"]

        # ``source`` distinguishes the mobile app from the browser extension.
        source = "mobile" if request.headers.get("X-Device-Id") else "extension"
        verdict = analyser_lien(url, source=source)

        donnees = VerdictLienSerializer(verdict).data
        enregistrer_verification(
            resoudre_appareil(request),
            type_verification=TypeVerification.LIEN,
            cible=url,
            verdict=donnees,
        )
        return Response(donnees)