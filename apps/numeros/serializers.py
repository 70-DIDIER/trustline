"""Serializers for the numeros endpoints."""
from rest_framework import serializers

from apps.core.constants import NiveauRisque
from apps.numeros.models import Numero


class VerifierNumeroSerializer(serializers.Serializer):
    """Input for POST /api/numeros/verifier/."""

    numero = serializers.CharField(max_length=20)

    def validate_numero(self, value):
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("Le numéro doit contenir des chiffres.")
        return value


class VerdictNumeroSerializer(serializers.Serializer):
    """Full verdict returned for a phone number."""

    numero = serializers.CharField()
    score = serializers.IntegerField(min_value=0, max_value=100)
    niveau_risque = serializers.ChoiceField(choices=NiveauRisque.choices)
    est_liste_blanche = serializers.BooleanField()
    organisation = serializers.CharField(allow_null=True)
    nombre_signalements = serializers.IntegerField()
    date_dernier_signalement = serializers.DateTimeField(allow_null=True)
    categories = serializers.ListField(child=serializers.CharField())
    indices = serializers.ListField(child=serializers.CharField())
    recommandation = serializers.CharField()


class NumeroModelSerializer(serializers.ModelSerializer):
    """Direct read of a stored Numero (GET /api/numeros/{numero}/)."""

    class Meta:
        model = Numero
        fields = [
            "numero",
            "score_risque",
            "niveau_risque",
            "nombre_signalements",
            "date_dernier_signalement",
            "est_liste_blanche",
            "date_creation",
        ]
