"""Shared serializers — notably the normalised verdict returned everywhere."""
from rest_framework import serializers

from apps.core.constants import NiveauRisque


class IndiceSerializer(serializers.Serializer):
    """One piece of evidence behind a verdict.

    Every analysis endpoint returns indices in this shape so the mobile app can
    render "why this verdict" identically for a number, a message or a link.
    """

    code = serializers.CharField(help_text="Identifiant stable de la règle déclenchée.")
    libelle = serializers.CharField(help_text="Phrase courte affichée à l'utilisateur.")
    poids = serializers.IntegerField(help_text="Points ajoutés au score par cet indice.")
    detail = serializers.CharField(
        allow_blank=True, help_text="Explication pédagogique du signal."
    )
    categorie = serializers.CharField(
        allow_blank=True, help_text="Catégorie d'arnaque associée, si pertinente."
    )


class VerdictSerializer(serializers.Serializer):
    """Canonical verdict shape returned by every analysis endpoint."""

    score = serializers.IntegerField(min_value=0, max_value=100)
    niveau_risque = serializers.ChoiceField(choices=NiveauRisque.choices)
    indices = IndiceSerializer(many=True)
    recommandation = serializers.CharField()
    explication = serializers.CharField()
    action_recommandee = serializers.CharField()
    categories = serializers.ListField(child=serializers.CharField())
    confiance = serializers.FloatField(
        help_text="Fiabilité du verdict, de 0 à 1 — jamais 1.0."
    )
    duree_ms = serializers.IntegerField(help_text="Durée de l'analyse en millisecondes.")