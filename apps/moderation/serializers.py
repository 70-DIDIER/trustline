"""Serializers for the admin REST API (dashboard back-office)."""
from rest_framework import serializers

from apps.core.constants import StatutSignalement
from apps.core.models import CategorieArnaque, ListeBlanche, LogAnalyse
from apps.messages.models import Message
from apps.numeros.models import Numero
from apps.signalements.models import Signalement


class SignalementAdminSerializer(serializers.ModelSerializer):
    categorie_code = serializers.CharField(source="categorie.code", read_only=True)
    categorie_libelle = serializers.CharField(source="categorie.libelle", read_only=True)
    numero = serializers.CharField(source="numero_cible.numero", read_only=True, default=None)

    class Meta:
        model = Signalement
        fields = [
            "id",
            "type_cible",
            "cible",
            "numero",
            "categorie_code",
            "categorie_libelle",
            "declarant",
            "commentaire",
            "statut",
            "date_creation",
        ]


class ModererSerializer(serializers.Serializer):
    """Input for the moderation action."""

    action = serializers.ChoiceField(
        choices=[
            (StatutSignalement.VALIDE, "Valider"),
            (StatutSignalement.CONTESTE, "Contester"),
            (StatutSignalement.REJETE, "Rejeter"),
        ]
    )


class NumeroAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Numero
        fields = [
            "id",
            "numero",
            "score_risque",
            "niveau_risque",
            "nombre_signalements",
            "date_dernier_signalement",
            "est_liste_blanche",
            "date_creation",
        ]


class ListeBlancheSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeBlanche
        fields = ["id", "numero", "organisation", "source", "date_ajout"]
        read_only_fields = ["date_ajout"]


class MessageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "contenu",
            "verdict",
            "score_risque",
            "indices_detectes",
            "liens_extraits",
            "numeros_extraits",
            "date_analyse",
        ]


class LogAnalyseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogAnalyse
        fields = [
            "id",
            "type_cible",
            "cible",
            "score_risque",
            "niveau_risque",
            "indices",
            "source",
            "date_analyse",
        ]


class CategorieArnaqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorieArnaque
        fields = ["id", "code", "libelle", "description"]
