"""Serializers for Mode Vigie."""
from rest_framework import serializers

from apps.vigie.models import SessionVigie


class SignalVigieSerializer(serializers.Serializer):
    """One signal the phone looks for in the local transcription."""

    code = serializers.CharField()
    libelle = serializers.CharField()
    poids = serializers.IntegerField()
    detail = serializers.CharField(allow_blank=True)
    categorie = serializers.CharField(allow_blank=True)
    motifs = serializers.ListField(
        child=serializers.CharField(),
        help_text="Expressions régulières appliquées localement, jamais envoyées.",
    )


class CatalogueVigieSerializer(serializers.Serializer):
    """Response of GET /api/vigie/signaux/."""

    version = serializers.CharField(
        help_text="Empreinte du catalogue — l'app ne le retélécharge que si elle change."
    )
    signaux = SignalVigieSerializer(many=True)


class CreerSessionVigieSerializer(serializers.Serializer):
    """Input for POST /api/vigie/sessions/."""

    duree_secondes = serializers.IntegerField(min_value=0, max_value=86400)
    signaux = serializers.ListField(
        child=serializers.CharField(max_length=64),
        allow_empty=True,
        help_text="Codes des signaux détectés localement — jamais les mots entendus.",
    )
    numero = serializers.CharField(
        required=False, allow_blank=True, default="", max_length=20
    )


class SessionVigieSerializer(serializers.ModelSerializer):
    """Stored summary of a listening session."""

    class Meta:
        model = SessionVigie
        fields = [
            "id",
            "duree_secondes",
            "signaux",
            "score",
            "niveau_risque",
            "numero",
            "date_session",
        ]