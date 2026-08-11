"""Aggregated statistics for the dashboard (Web front-end + jury demo)."""
from django.db.models import Count, Max
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.constants import NiveauRisque
from apps.core.models import LogAnalyse
from apps.numeros.models import Numero
from apps.signalements.models import Signalement


class StatsResponseSerializer(serializers.Serializer):
    """Documents the shape of the /api/stats/ response."""

    total_signalements = serializers.IntegerField()
    total_numeros_suivis = serializers.IntegerField()
    total_analyses = serializers.IntegerField()
    signalements_par_categorie = serializers.ListField(child=serializers.DictField())
    signalements_par_statut = serializers.ListField(child=serializers.DictField())
    top_numeros_signales = serializers.ListField(child=serializers.DictField())


class StatsView(APIView):
    """GET /api/stats/ — headline metrics for the dashboard."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Statistiques"],
        summary="Statistiques agrégées (signalements, catégories, top numéros)",
        responses={200: StatsResponseSerializer},
    )
    def get(self, request):
        par_categorie = list(
            Signalement.objects.values("categorie__code", "categorie__libelle")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        par_statut = list(
            Signalement.objects.values("statut")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        top_numeros = list(
            Numero.objects.filter(nombre_signalements__gt=0)
            .order_by("-score_risque", "-nombre_signalements")
            .values("numero", "score_risque", "niveau_risque", "nombre_signalements")[:10]
        )

        return Response(
            {
                "total_signalements": Signalement.objects.count(),
                "total_numeros_suivis": Numero.objects.count(),
                "total_analyses": LogAnalyse.objects.count(),
                "signalements_par_categorie": par_categorie,
                "signalements_par_statut": par_statut,
                "top_numeros_signales": top_numeros,
            }
        )


class AlerteSerializer(serializers.Serializer):
    """Documents the shape of one entry in /api/alertes/."""

    categorie = serializers.CharField()
    libelle = serializers.CharField()
    nombre_signalements = serializers.IntegerField()
    niveau_risque = serializers.ChoiceField(choices=NiveauRisque.choices)
    derniere_activite = serializers.DateTimeField(allow_null=True)
    types_cibles = serializers.DictField(child=serializers.IntegerField())


class AlertesPubliquesView(APIView):
    """GET /api/alertes/ — public "active alerts" derived from real reports.

    There is no separate Campagne model: an "alert" here is simply a scam
    category with recent community reports, aggregated live from
    ``Signalement``. Nothing is fabricated — a category with zero reports
    simply does not appear. ``niveau_risque`` is the highest risk level among
    the ``Numero`` linked to that category's reports (falls back to
    "suspect" when reports exist but no linked number carries a computed
    score yet, e.g. link/message-only reports).
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Statistiques"],
        summary="Alertes publiques (catégories d'arnaque actives, dérivées des signalements réels)",
        responses={200: AlerteSerializer(many=True)},
    )
    def get(self, request):
        ordre_risque = {NiveauRisque.ELEVE: 2, NiveauRisque.SUSPECT: 1, NiveauRisque.FAIBLE: 0}

        lignes = (
            Signalement.objects.values("categorie__code", "categorie__libelle")
            .annotate(total=Count("id"), derniere=Max("date_creation"))
            .order_by("-derniere")
        )

        alertes = []
        for ligne in lignes:
            code = ligne["categorie__code"]
            reports = Signalement.objects.filter(categorie__code=code)

            types_cibles: dict[str, int] = {}
            for row in reports.values("type_cible").annotate(total=Count("id")):
                types_cibles[row["type_cible"]] = row["total"]

            niveaux_numeros = list(
                reports.filter(numero_cible__isnull=False)
                .values_list("numero_cible__niveau_risque", flat=True)
                .distinct()
            )
            niveau = max(niveaux_numeros, key=lambda n: ordre_risque.get(n, 0)) if niveaux_numeros else NiveauRisque.SUSPECT

            alertes.append(
                {
                    "categorie": code,
                    "libelle": ligne["categorie__libelle"],
                    "nombre_signalements": ligne["total"],
                    "niveau_risque": niveau,
                    "derniere_activite": ligne["derniere"],
                    "types_cibles": types_cibles,
                }
            )

        alertes.sort(key=lambda a: (ordre_risque.get(a["niveau_risque"], 0), a["nombre_signalements"]), reverse=True)
        return Response(AlerteSerializer(alertes, many=True).data)
