"""Endpoint for analysing a URL / website (Chrome extension)."""
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.liens.serializers import AnalyserLienSerializer, VerdictLienSerializer
from apps.liens.services import analyser_lien


class AnalyserLienView(APIView):
    """POST /api/liens/analyser/ — verdict for a URL."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Liens"],
        summary="Analyser un lien / site (heuristiques + réputation)",
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

        verdict = analyser_lien(entree.validated_data["url"], source="extension")
        return Response(VerdictLienSerializer(verdict).data)
