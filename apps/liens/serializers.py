"""Serializers for the link analysis endpoint."""
from rest_framework import serializers

from apps.core.serializers import VerdictSerializer


class AnalyserLienSerializer(serializers.Serializer):
    """Input for POST /api/liens/analyser/."""

    url = serializers.CharField(max_length=2000)

    def validate_url(self, value):
        if not value.strip():
            raise serializers.ValidationError("L'URL ne peut pas être vide.")
        return value


class VerdictLienSerializer(VerdictSerializer):
    """Verdict returned for a URL."""

    url = serializers.CharField()
    domaine = serializers.CharField(allow_blank=True)