"""Aggregated statistics for the dashboard (Web front-end + jury demo)."""
from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

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
