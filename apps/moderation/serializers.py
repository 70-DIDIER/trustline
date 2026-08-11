"""Serializers for the admin REST API (dashboard back-office)."""
from rest_framework import serializers

from apps.core.constants import StatutSignalement
from apps.core.models import CategorieArnaque, ListeBlanche, LogAnalyse
from apps.messages.models import Message
from apps.numeros.models import Numero
from apps.signalements.models import Signalement
from apps.veille.models import Alerte, Conseil


class SignalementAdminSerializer(serializers.ModelSerializer):
    categorie_code = serializers.CharField(source="categorie.code", read_only=True)
    categorie_libelle = serializers.CharField(source="categorie.libelle", read_only=True)
    numero = serializers.CharField(source="numero_cible.numero", read_only=True, default=None)

    class Meta:
        model = Signalement
        fields = [
            "id",
            "reference",
            "type_cible",
            "cible",
            "numero",
            "categorie_code",
            "categorie_libelle",
            "declarant",
            "commentaire",
            "montant_perdu",
            "statut",
            "date_creation",
        ]


_ACTIONS_MODERATION = [
    (StatutSignalement.VALIDE, "Valider"),
    (StatutSignalement.CONTESTE, "Contester"),
    (StatutSignalement.REJETE, "Rejeter"),
]


class ModererSerializer(serializers.Serializer):
    """Input for the single moderation action."""

    action = serializers.ChoiceField(choices=_ACTIONS_MODERATION)


class ModererLotSerializer(serializers.Serializer):
    """Input for bulk moderation."""

    ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False,
        help_text="IDs des signalements à modérer.",
    )
    action = serializers.ChoiceField(choices=_ACTIONS_MODERATION)


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


class AlerteAdminSerializer(serializers.ModelSerializer):
    """Full write access to campaigns from the back-office."""

    class Meta:
        model = Alerte
        fields = [
            "id",
            "titre",
            "description",
            "recommandation",
            "niveau_risque",
            "canal",
            "categorie",
            "nombre_signalements",
            "epinglee",
            "active",
            "date_debut",
            "date_maj",
        ]
        read_only_fields = ["date_maj"]


class ConseilAdminSerializer(serializers.ModelSerializer):
    """Full write access to prevention cards from the back-office."""

    class Meta:
        model = Conseil
        fields = [
            "id",
            "titre",
            "resume",
            "points",
            "icone",
            "categorie",
            "ordre",
            "actif",
            "date_maj",
        ]
        read_only_fields = ["date_maj"]
