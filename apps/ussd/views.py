"""USSD endpoints.

* ``/api/ussd/simulate/`` — endpoint JSON pour le simulateur du front-end.
* ``/api/ussd/africastalking/`` — webhook pour la vraie passerelle Africa's Talking
  (form-urlencoded en entrée, texte brut ``CON``/``END`` en sortie).

Les deux partagent la même logique métier : ``apps.ussd.services.traiter_ussd``.
"""
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ussd.services import traiter_ussd

logger = logging.getLogger("trustline.ussd")


class UssdRequestSerializer(serializers.Serializer):
    """Input mimicking a USSD gateway callback."""

    texte = serializers.CharField(
        allow_blank=True,
        required=False,
        default="",
        help_text="Chaîne USSD cumulée, ex. '2*90112233*6'. Vide = menu principal.",
    )
    session_id = serializers.CharField(required=False, default="demo")


class UssdResponseSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["CON", "END"])
    message = serializers.CharField()


class UssdSimulateView(APIView):
    """POST /api/ussd/simulate/ — drive the simplified USSD menu."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["USSD"],
        summary="Simuler un parcours USSD",
        request=UssdRequestSerializer,
        responses={200: UssdResponseSerializer},
        examples=[
            OpenApiExample("Menu principal (composition initiale)", value={"texte": ""}, request_only=True),
            OpenApiExample("1 → vérifier un numéro", value={"texte": "1*90112233"}, request_only=True),
            OpenApiExample("2 → signaler (numéro + catégorie OTP)", value={"texte": "2*79887766*6"}, request_only=True),
            OpenApiExample("3 → conseils sécurité", value={"texte": "3"}, request_only=True),
        ],
    )
    def post(self, request):
        entree = UssdRequestSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        session = entree.validated_data.get("session_id", "demo")
        reponse = traiter_ussd(
            entree.validated_data.get("texte", ""),
            declarant=f"ussd:{session}",
        )
        return Response(UssdResponseSerializer(reponse).data)


@csrf_exempt
@require_POST
def africastalking_ussd(request):
    """Webhook pour la passerelle USSD Africa's Talking.

    Entrée : POST form-urlencoded (sessionId, serviceCode, phoneNumber, text).
    Sortie : texte brut préfixé ``CON `` (continuer) ou ``END `` (terminer).
    On répond TOUJOURS 200 en texte (jamais de 500 vers la passerelle).
    """
    texte = request.POST.get("text", "")
    phone = request.POST.get("phoneNumber") or request.POST.get("sessionId", "at")
    logger.info("[ussd-at] phone=%s text=%r", phone, texte)
    try:
        res = traiter_ussd(texte, declarant=f"ussd:{phone}")
        corps = f"{res['type']} {res['message']}"
    except Exception as exc:  # noqa: BLE001 — ne jamais renvoyer 500 au gateway
        logger.exception("[ussd-at] erreur gérée: %s", exc)
        corps = "END Service momentanément indisponible. Réessayez plus tard."
    return HttpResponse(corps, content_type="text/plain; charset=utf-8")
