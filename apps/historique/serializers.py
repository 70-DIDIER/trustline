"""Serializers for the per-device verification history."""
from rest_framework import serializers

from apps.historique.models import Verification


class VerificationSerializer(serializers.ModelSerializer):
    """One history entry as consumed by the mobile app."""

    type_libelle = serializers.CharField(
        source="get_type_verification_display", read_only=True
    )

    class Meta:
        model = Verification
        fields = [
            "id",
            "type_verification",
            "type_libelle",
            "cible",
            "resume",
            "score",
            "niveau_risque",
            "verdict",
            "date_verification",
        ]