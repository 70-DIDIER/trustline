"""Serializers for community reports."""
from rest_framework import serializers

from apps.core.constants import CategorieCode, TypeCible
from apps.signalements.models import Signalement


class CreerSignalementSerializer(serializers.Serializer):
    """Input for POST /api/signalements/."""

    type_cible = serializers.ChoiceField(choices=TypeCible.choices)
    cible = serializers.CharField(max_length=500)
    categorie = serializers.ChoiceField(
        choices=CategorieCode.choices,
        help_text="Code de la catégorie d'arnaque.",
    )
    declarant_id = serializers.CharField(
        max_length=64,
        help_text="Identifiant anonymisé du déclarant.",
    )
    commentaire = serializers.CharField(
        required=False, allow_blank=True, default="", max_length=1000
    )


class SignalementSerializer(serializers.ModelSerializer):
    """Read representation of a stored report."""

    categorie = serializers.CharField(source="categorie.code", read_only=True)

    class Meta:
        model = Signalement
        fields = [
            "id",
            "type_cible",
            "cible",
            "categorie",
            "declarant",
            "commentaire",
            "statut",
            "date_creation",
        ]
