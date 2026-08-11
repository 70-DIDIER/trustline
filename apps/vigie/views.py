"""Mode Vigie endpoints: signal catalogue + session recording."""
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.appareils.services import exiger_appareil
from apps.core.utils import formater_numero, normaliser_numero
from apps.historique.models import TypeVerification
from apps.historique.services import enregistrer_verification
from apps.vigie.models import SessionVigie
from apps.vigie.serializers import (
    CatalogueVigieSerializer,
    CreerSessionVigieSerializer,
    SessionVigieSerializer,
)
from apps.vigie.services import catalogue_signaux, evaluer_session, version_catalogue


class CatalogueVigieView(APIView):
    """GET /api/vigie/signaux/ — the rules the phone applies locally."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Mode Vigie"],
        summary="Catalogue des signaux analysés localement",
        description=(
            "Le Mode Vigie n'envoie **ni audio ni transcription** au serveur. "
            "L'application télécharge ce catalogue (libellés + expressions "
            "régulières) et fait la détection sur le téléphone. Le champ "
            "`version` permet de ne le retélécharger que lorsqu'il change."
        ),
        responses={200: CatalogueVigieSerializer},
    )
    def get(self, request):
        return Response(
            {"version": version_catalogue(), "signaux": catalogue_signaux()}
        )


class SessionVigieView(APIView):
    """POST /api/vigie/sessions/ — store the anonymised outcome of a session."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Mode Vigie"],
        summary="Enregistrer le résultat d'une session d'écoute",
        description=(
            "Seuls les **codes** des signaux détectés remontent, jamais les mots "
            "prononcés. Le backend recalcule le score à partir des poids "
            "officiels et ajoute l'entrée à l'historique de l'appareil."
        ),
        request=CreerSessionVigieSerializer,
        responses={201: SessionVigieSerializer},
    )
    def post(self, request):
        appareil = exiger_appareil(request)
        entree = CreerSessionVigieSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        data = entree.validated_data

        evaluation = evaluer_session(data["signaux"])
        numero = normaliser_numero(data.get("numero", "")) if data.get("numero") else ""

        session = SessionVigie.objects.create(
            appareil=appareil,
            duree_secondes=data["duree_secondes"],
            signaux=evaluation["codes"],
            score=evaluation["score"],
            niveau_risque=evaluation["niveau_risque"],
            numero=numero,
        )

        donnees = SessionVigieSerializer(session).data
        libelle = (
            formater_numero(numero)
            if numero
            else f"Appel analysé — {len(evaluation['codes'])} signal(aux)"
        )
        enregistrer_verification(
            appareil,
            type_verification=TypeVerification.VIGIE,
            cible=libelle,
            verdict=donnees,
        )
        return Response(donnees, status=status.HTTP_201_CREATED)