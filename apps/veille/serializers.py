"""Serializers for alerts and prevention tips."""
from rest_framework import serializers

from apps.veille.models import Alerte, Conseil


class AlerteSerializer(serializers.ModelSerializer):
    """A live scam campaign as shown in the "Alertes" screen."""

    canal_libelle = serializers.CharField(source="get_canal_display", read_only=True)
    categorie_code = serializers.CharField(
        source="categorie.code", read_only=True, default=None
    )
    categorie_libelle = serializers.CharField(
        source="categorie.libelle", read_only=True, default=None
    )

    class Meta:
        model = Alerte
        fields = [
            "id",
            "titre",
            "description",
            "recommandation",
            "niveau_risque",
            "canal",
            "canal_libelle",
            "categorie_code",
            "categorie_libelle",
            "nombre_signalements",
            "epinglee",
            "date_debut",
            "date_maj",
        ]


class ConseilSerializer(serializers.ModelSerializer):
    """A prevention card."""

    categorie_code = serializers.CharField(
        source="categorie.code", read_only=True, default=None
    )

    class Meta:
        model = Conseil
        fields = [
            "id",
            "titre",
            "resume",
            "points",
            "icone",
            "categorie_code",
            "ordre",
        ]