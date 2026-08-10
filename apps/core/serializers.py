"""Shared serializers — notably the normalised verdict returned everywhere."""
from rest_framework import serializers

from apps.core.constants import NiveauRisque


class VerdictSerializer(serializers.Serializer):
    """Canonical verdict shape returned by every analysis endpoint.

    Used mainly to document responses consistently in Swagger.
    """

    score = serializers.IntegerField(min_value=0, max_value=100)
    niveau_risque = serializers.ChoiceField(choices=NiveauRisque.choices)
    indices = serializers.ListField(child=serializers.CharField())
    recommandation = serializers.CharField()
