"""Serializers for the message analysis endpoint."""
from rest_framework import serializers

from apps.core.serializers import VerdictSerializer


class AnalyserMessageSerializer(serializers.Serializer):
    """Input for POST /api/messages/analyser/."""

    contenu = serializers.CharField(max_length=5000, trim_whitespace=False)
    expediteur = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        max_length=32,
        help_text="Numéro de l'expéditeur, si connu — sa réputation renforce le verdict.",
    )

    def validate_contenu(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le contenu ne peut pas être vide.")
        return value


class VerdictMessageSerializer(VerdictSerializer):
    """Verdict returned for an analysed message."""

    liens_extraits = serializers.ListField(child=serializers.CharField())
    numeros_extraits = serializers.ListField(child=serializers.CharField())