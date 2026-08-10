"""Endpoints for verifying and consulting phone numbers."""
from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.constants import TypeCible
from apps.core.services import enregistrer_log
from apps.core.utils import normaliser_numero
from apps.numeros.models import Numero
from apps.numeros.serializers import (
    NumeroModelSerializer,
    VerdictNumeroSerializer,
    VerifierNumeroSerializer,
)
from apps.numeros.services import verifier_numero


class VerifierNumeroView(APIView):
    """POST /api/numeros/verifier/ — full verdict for a phone number."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Numéros"],
        summary="Vérifier un numéro (liste blanche + réputation)",
        request=VerifierNumeroSerializer,
        responses={200: VerdictNumeroSerializer},
    )
    def post(self, request):
        entree = VerifierNumeroSerializer(data=request.data)
        entree.is_valid(raise_exception=True)

        verdict = verifier_numero(entree.validated_data["numero"])
        enregistrer_log(TypeCible.NUMERO, verdict["numero"], verdict, source="api")

        return Response(VerdictNumeroSerializer(verdict).data)


class NumeroDetailView(APIView):
    """GET /api/numeros/{numero}/ — direct read of a stored number."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Numéros"],
        summary="Consulter un numéro déjà en base",
        responses={200: NumeroModelSerializer},
    )
    def get(self, request, numero):
        numero_norm = normaliser_numero(numero)
        obj = Numero.objects.filter(numero=numero_norm).first()
        if obj is None:
            raise Http404("Numéro inconnu de la base.")
        return Response(NumeroModelSerializer(obj).data, status=status.HTTP_200_OK)
