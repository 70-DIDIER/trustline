"""Admin REST API (JWT + admin only) for the back-office dashboard.

All viewsets require an authenticated staff user (``IsAdminUser``). Obtain a
token via ``POST /api/token/`` with a superuser account, then send
``Authorization: Bearer <token>``.
"""
import csv

from django.db import transaction
from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.core.models import CategorieArnaque, ListeBlanche, LogAnalyse
from apps.messages.models import Message
from apps.moderation.serializers import (
    CategorieArnaqueSerializer,
    ListeBlancheSerializer,
    LogAnalyseSerializer,
    MessageAdminSerializer,
    ModererLotSerializer,
    ModererSerializer,
    NumeroAdminSerializer,
    SignalementAdminSerializer,
)
from apps.numeros.models import Numero
from apps.numeros.services import invalider_cache_numero
from apps.signalements.models import Signalement
from apps.signalements.reputation import mettre_a_jour_numero
from apps.signalements.services import moderer_signalement


@extend_schema_view(
    list=extend_schema(
        tags=["Admin — Signalements"],
        summary="Lister les signalements (filtres: statut, categorie, type_cible)",
    ),
    retrieve=extend_schema(tags=["Admin — Signalements"], summary="Détail d'un signalement"),
)
class SignalementAdminViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste / détail des signalements + modération (unitaire, en lot) + export."""

    permission_classes = [IsAdminUser]
    serializer_class = SignalementAdminSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["cible", "declarant", "commentaire"]
    ordering_fields = ["date_creation", "statut", "type_cible"]
    ordering = ["-date_creation"]

    def get_queryset(self):
        qs = Signalement.objects.select_related("categorie", "numero_cible").all()
        params = self.request.query_params
        if statut := params.get("statut"):
            qs = qs.filter(statut=statut)
        if categorie := params.get("categorie"):
            qs = qs.filter(categorie__code=categorie)
        if type_cible := params.get("type_cible"):
            qs = qs.filter(type_cible=type_cible)
        return qs

    @extend_schema(
        tags=["Admin — Signalements"],
        summary="Modérer un signalement (valider / contester / rejeter)",
        request=ModererSerializer,
        responses={200: SignalementAdminSerializer},
    )
    @action(detail=True, methods=["post"])
    def moderer(self, request, pk=None):
        signalement = self.get_object()
        entree = ModererSerializer(data=request.data)
        entree.is_valid(raise_exception=True)

        moderer_signalement(signalement, entree.validated_data["action"])
        signalement.refresh_from_db()
        return Response(SignalementAdminSerializer(signalement).data)

    @extend_schema(
        tags=["Admin — Signalements"],
        summary="Modérer plusieurs signalements en une fois",
        request=ModererLotSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    @action(detail=False, methods=["post"], url_path="moderer-lot")
    def moderer_lot(self, request):
        entree = ModererLotSerializer(data=request.data)
        entree.is_valid(raise_exception=True)
        action_statut = entree.validated_data["action"]

        signalements = Signalement.objects.filter(id__in=entree.validated_data["ids"])
        for signalement in signalements:
            moderer_signalement(signalement, action_statut)
        return Response({"modifies": signalements.count(), "statut": action_statut})

    @extend_schema(
        tags=["Admin — Signalements"],
        summary="Exporter les signalements en CSV",
        responses={(200, "text/csv"): OpenApiTypes.BINARY},
    )
    @action(detail=False, methods=["get"])
    def export(self, request):
        reponse = HttpResponse(content_type="text/csv")
        reponse["Content-Disposition"] = 'attachment; filename="signalements.csv"'
        writer = csv.writer(reponse)
        writer.writerow(
            ["id", "date_creation", "type_cible", "cible", "categorie",
             "declarant", "statut", "commentaire"]
        )
        for s in self.filter_queryset(self.get_queryset()):
            writer.writerow([
                s.id, s.date_creation.isoformat(), s.type_cible, s.cible,
                s.categorie.code, s.declarant, s.statut, s.commentaire,
            ])
        return reponse


@extend_schema_view(
    list=extend_schema(
        tags=["Admin — Numéros"],
        summary="Lister les numéros suivis (filtre: niveau_risque)",
    ),
    retrieve=extend_schema(tags=["Admin — Numéros"], summary="Détail d'un numéro"),
)
class NumeroAdminViewSet(viewsets.ReadOnlyModelViewSet):
    """Liste / détail des numéros + ajout à la liste blanche + signalements liés."""

    permission_classes = [IsAdminUser]
    serializer_class = NumeroAdminSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["numero"]
    ordering_fields = ["score_risque", "nombre_signalements", "date_dernier_signalement"]
    ordering = ["-score_risque"]

    def get_queryset(self):
        qs = Numero.objects.all()
        niveau = self.request.query_params.get("niveau_risque")
        if niveau:
            qs = qs.filter(niveau_risque=niveau)
        return qs

    @extend_schema(
        tags=["Admin — Numéros"],
        summary="Lister les signalements liés à ce numéro",
        responses={200: SignalementAdminSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def signalements(self, request, pk=None):
        numero = self.get_object()
        qs = numero.signalements.select_related("categorie").all()
        page = self.paginate_queryset(qs)
        serializer = SignalementAdminSerializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @extend_schema(
        tags=["Admin — Numéros"],
        summary="Ajouter ce numéro à la liste blanche (numéro officiel)",
        request=None,
        responses={200: NumeroAdminSerializer},
    )
    @action(detail=True, methods=["post"], url_path="liste-blanche")
    @transaction.atomic
    def liste_blanche(self, request, pk=None):
        numero = self.get_object()
        organisation = request.data.get("organisation", "À compléter")
        source = request.data.get("source", "admin")

        ListeBlanche.objects.get_or_create(
            numero=numero.numero,
            defaults={"organisation": organisation, "source": source},
        )
        numero.est_liste_blanche = True
        numero.save(update_fields=["est_liste_blanche"])
        mettre_a_jour_numero(numero)  # whitelist -> score 0
        invalider_cache_numero(numero.numero)
        numero.refresh_from_db()
        return Response(NumeroAdminSerializer(numero).data)


@extend_schema_view(
    list=extend_schema(tags=["Admin — Liste blanche"], summary="Lister la liste blanche"),
    create=extend_schema(tags=["Admin — Liste blanche"], summary="Ajouter un numéro officiel"),
    retrieve=extend_schema(tags=["Admin — Liste blanche"], summary="Détail"),
    destroy=extend_schema(tags=["Admin — Liste blanche"], summary="Retirer de la liste blanche"),
)
class ListeBlancheViewSet(viewsets.ModelViewSet):
    """CRUD de la liste blanche (numéros officiels protégés)."""

    permission_classes = [IsAdminUser]
    serializer_class = ListeBlancheSerializer
    queryset = ListeBlanche.objects.all()
    http_method_names = ["get", "post", "delete"]  # pas d'update partiel

    def perform_destroy(self, instance):
        numero_str = instance.numero
        super().perform_destroy(instance)
        # Recalculer la réputation du numéro s'il existe (il n'est plus protégé).
        numero_obj = Numero.objects.filter(numero=numero_str).first()
        if numero_obj is not None:
            numero_obj.est_liste_blanche = False
            numero_obj.save(update_fields=["est_liste_blanche"])
            mettre_a_jour_numero(numero_obj)
            invalider_cache_numero(numero_str)


@extend_schema_view(
    list=extend_schema(tags=["Admin — Messages"], summary="Lister les messages analysés (filtre: verdict)"),
    retrieve=extend_schema(tags=["Admin — Messages"], summary="Détail d'un message analysé"),
)
class MessageAdminViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = MessageAdminSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["contenu"]
    ordering_fields = ["date_analyse", "score_risque"]
    ordering = ["-date_analyse"]

    def get_queryset(self):
        qs = Message.objects.all()
        verdict = self.request.query_params.get("verdict")
        if verdict:
            qs = qs.filter(verdict=verdict)
        return qs


@extend_schema_view(
    list=extend_schema(tags=["Admin — Logs"], summary="Lister les logs d'analyse (filtres: type_cible, source)"),
    retrieve=extend_schema(tags=["Admin — Logs"], summary="Détail d'un log"),
)
class LogAnalyseAdminViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = LogAnalyseSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["cible"]
    ordering_fields = ["date_analyse", "score_risque"]
    ordering = ["-date_analyse"]

    def get_queryset(self):
        qs = LogAnalyse.objects.all()
        params = self.request.query_params
        if type_cible := params.get("type_cible"):
            qs = qs.filter(type_cible=type_cible)
        if source := params.get("source"):
            qs = qs.filter(source=source)
        return qs


@extend_schema_view(
    list=extend_schema(tags=["Admin — Catégories"], summary="Lister les catégories d'arnaque"),
)
class CategorieArnaqueViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = CategorieArnaqueSerializer
    queryset = CategorieArnaque.objects.all()
    pagination_class = None  # petit référentiel, pas de pagination
