"""Endpoint for analysing a message / SMS."""
from drf_spectacular.utils import extend_schema
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
    )
    def post(self, request):
        entree = AnalyserMessageSerializer(data=request.data)
        entree.is_valid(raise_exception=True)

        verdict = analyser_message(entree.validated_data["contenu"], source="api")
        return Response(VerdictMessageSerializer(verdict).data)
