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
        required=False,
        allow_blank=True,
        default="",
        help_text=(
            "Identifiant anonymisé du déclarant. Facultatif depuis l'application "
            "mobile : l'en-tête X-Device-Id fait foi."
        ),
    )
    commentaire = serializers.CharField(
        required=False, allow_blank=True, default="", max_length=1000
    )
    montant_perdu = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=1_000_000_000,
        help_text="Préjudice en FCFA, facultatif.",
    )

    def validate_cible(self, value):
        if not value.strip():
            raise serializers.ValidationError("La cible ne peut pas être vide.")
        return value.strip()


class SignalementSerializer(serializers.ModelSerializer):
    """Read representation of a stored report."""

    categorie = serializers.CharField(source="categorie.code", read_only=True)
    categorie_libelle = serializers.CharField(
        source="categorie.libelle", read_only=True
    )
    statut_libelle = serializers.CharField(
        source="get_statut_display", read_only=True
    )

    class Meta:
        model = Signalement
        fields = [
            "id",
            "reference",
            "type_cible",
            "cible",
            "categorie",
            "categorie_libelle",
            "declarant",
            "commentaire",
            "montant_perdu",
            "statut",
            "statut_libelle",
            "date_creation",
        ]


class ReputationCibleSerializer(serializers.Serializer):
    """Reputation of the reported number, returned right after a report."""

    numero = serializers.CharField()
    numero_formate = serializers.CharField()
    score_risque = serializers.IntegerField()
    niveau_risque = serializers.CharField()
    nombre_signalements = serializers.IntegerField()


class SignalementCreeSerializer(SignalementSerializer):
    """Response body of POST /api/signalements/."""

    message = serializers.CharField(read_only=True)
    reputation_cible = ReputationCibleSerializer(read_only=True, allow_null=True)

    class Meta(SignalementSerializer.Meta):
        fields = SignalementSerializer.Meta.fields + ["message", "reputation_cible"]