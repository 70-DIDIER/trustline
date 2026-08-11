from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.moderation.admin_views import (
    CategorieArnaqueViewSet,
    ListeBlancheViewSet,
    LogAnalyseAdminViewSet,
    MessageAdminViewSet,
    NumeroAdminViewSet,
    SignalementAdminViewSet,
)
from apps.moderation.views import AlertesPubliquesView, StatsView

app_name = "moderation"

# Admin REST API (JWT + admin only) under /api/admin/
router = DefaultRouter()
router.register("signalements", SignalementAdminViewSet, basename="admin-signalements")
router.register("numeros", NumeroAdminViewSet, basename="admin-numeros")
router.register("liste-blanche", ListeBlancheViewSet, basename="admin-liste-blanche")
router.register("messages", MessageAdminViewSet, basename="admin-messages")
router.register("logs", LogAnalyseAdminViewSet, basename="admin-logs")
router.register("categories", CategorieArnaqueViewSet, basename="admin-categories")

urlpatterns = [
    # Dashboard summary (public — widget de synthèse).
    path("stats/", StatsView.as_view(), name="stats"),
    # Alertes publiques (catégories actives, dérivées des signalements réels).
    path("alertes/", AlertesPubliquesView.as_view(), name="alertes"),
    # Back-office admin.
    path("admin/", include(router.urls)),
]
