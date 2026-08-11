"""Serializers for the anonymous device identity and its profile."""
from rest_framework import serializers

from apps.appareils.models import Appareil
from apps.historique.serializers import VerificationSerializer
from apps.veille.serializers import AlerteSerializer, ConseilSerializer


class EnregistrerAppareilSerializer(serializers.Serializer):
    """Input for POST /api/appareils/ — called once at first launch."""

    plateforme = serializers.ChoiceField(
        choices=Appareil.Plateforme.choices,
        required=False,
        default=Appareil.Plateforme.AUTRE,
    )
    version_app = serializers.CharField(
        required=False, allow_blank=True, default="", max_length=32
    )
    langue = serializers.CharField(
        required=False, allow_blank=True, default="fr", max_length=8
    )


class StatistiquesAppareilSerializer(serializers.Serializer):
    """Counters shown on the home header and the profile screen."""

    verifications = serializers.IntegerField()
    menaces_detectees = serializers.IntegerField(
        help_text="Vérifications classées « risque élevé »."
    )
    signalements = serializers.IntegerField()
    signalements_valides = serializers.IntegerField()
    sessions_vigie = serializers.IntegerField()


class StatistiquesCommunauteSerializer(serializers.Serializer):
    """Community-wide counters — the "you are not alone" block."""

    signalements = serializers.IntegerField()
    numeros_suivis = serializers.IntegerField()
    analyses = serializers.IntegerField()
    numeros_risque_eleve = serializers.IntegerField()


class ProfilAppareilSerializer(serializers.Serializer):
    """Response of GET /api/appareils/moi/."""

    device_id = serializers.UUIDField()
    plateforme = serializers.CharField()
    version_app = serializers.CharField(allow_blank=True)
    membre_depuis = serializers.DateTimeField()
    statistiques = StatistiquesAppareilSerializer()
    communaute = StatistiquesCommunauteSerializer()


class AccueilSerializer(serializers.Serializer):
    """Response of GET /api/accueil/ — everything the home screen renders."""

    statistiques = StatistiquesAppareilSerializer()
    communaute = StatistiquesCommunauteSerializer()
    alertes = AlerteSerializer(many=True)
    conseil_du_jour = ConseilSerializer(allow_null=True)
    verifications_recentes = VerificationSerializer(many=True)