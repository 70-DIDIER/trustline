"""Serializers for the link analysis endpoint."""
from rest_framework import serializers

from apps.core.constants import NiveauRisque


class AnalyserLienSerializer(serializers.Serializer):
    """Input for POST /api/liens/analyser/."""

    url = serializers.CharField(max_length=2000)

    def validate_url(self, value):
        if not value.strip():
            raise serializers.ValidationError("L'URL ne peut pas être vide.")
        return value


class VerdictLienSerializer(serializers.Serializer):
    """Verdict returned for a URL."""

    url = serializers.CharField()
    domaine = serializers.CharField(allow_blank=True)
    score = serializers.IntegerField(min_value=0, max_value=100)
    niveau_risque = serializers.ChoiceField(choices=NiveauRisque.choices)
    indices = serializers.ListField(child=serializers.CharField())
    recommandation = serializers.CharField()
