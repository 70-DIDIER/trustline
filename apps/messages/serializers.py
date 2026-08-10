"""Serializers for the message analysis endpoint."""
from rest_framework import serializers

from apps.core.constants import NiveauRisque


class AnalyserMessageSerializer(serializers.Serializer):
    """Input for POST /api/messages/analyser/."""

    contenu = serializers.CharField(max_length=5000, trim_whitespace=False)

    def validate_contenu(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le contenu ne peut pas être vide.")
        return value


class VerdictMessageSerializer(serializers.Serializer):
    """Verdict returned for an analysed message."""

    score = serializers.IntegerField(min_value=0, max_value=100)
    niveau_risque = serializers.ChoiceField(choices=NiveauRisque.choices)
    indices = serializers.ListField(child=serializers.CharField())
    recommandation = serializers.CharField()
    categories = serializers.ListField(child=serializers.CharField())
    liens_extraits = serializers.ListField(child=serializers.CharField())
    numeros_extraits = serializers.ListField(child=serializers.CharField())
