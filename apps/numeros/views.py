"""Endpoints for verifying and consulting phone numbers."""
from django.http import Http404
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appareils.services import resoudre_appareil
from apps.core.constants import TypeCible
from apps.core.services import enregistrer_log
from apps.core.utils import normaliser_numero
from apps.historique.models import TypeVerification
from apps.historique.services import enregistrer_verification
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
        description=(
            "Envoyez l'en-tête `X-Device-Id` pour que la vérification soit ajoutée "
            "à l'historique de l'appareil. Sans cet en-tête, le verdict est rendu "
            "mais rien n'est historisé.\n\n"
            "`contexte=appel` marque l'entrée d'historique comme un appel entrant."
        ),
        request=VerifierNumeroSerializer,
        responses={200: VerdictNumeroSerializer},
        examples=[
            OpenApiExample(
                "Numéro signalé (haut risque)",
                value={"numero": "+22890112233"},
                request_only=True,
            ),
            OpenApiExample(
                "Numéro officiel (liste blanche)",
                value={"numero": "+22890000002"},
                request_only=True,
            ),
            OpenApiExample(
                "Format local (sans indicatif)",
                value={"numero": "90 11 22 33"},
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        entree = VerifierNumeroSerializer(data=request.data)
        entree.is_valid(raise_exception=True)

        verdict = verifier_numero(entree.validated_data["numero"])
        enregistrer_log(TypeCible.NUMERO, verdict["numero"], verdict, source="api")

        donnees = VerdictNumeroSerializer(verdict).data
        est_appel = request.query_params.get("contexte") == "appel"
        enregistrer_verification(
            resoudre_appareil(request),
            type_verification=(
                TypeVerification.APPEL if est_appel else TypeVerification.NUMERO
            ),
            cible=verdict["numero_formate"],
            verdict=donnees,
        )
        return Response(donnees)


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