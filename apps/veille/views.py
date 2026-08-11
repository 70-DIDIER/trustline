"""Public read endpoints for alerts and prevention tips."""
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.veille.models import Alerte, Conseil
from apps.veille.serializers import AlerteSerializer, ConseilSerializer


@extend_schema(
    tags=["Alertes"],
    summary="Campagnes d'arnaque en cours",
    description=(
        "Alertes actives, les épinglées d'abord puis les plus récentes. "
        "Alimente l'onglet « Alertes » et le bloc d'accueil de l'application."
    ),
)
class AlerteListView(ListAPIView):
    """GET /api/alertes/"""

    permission_classes = [AllowAny]
    serializer_class = AlerteSerializer
    queryset = Alerte.objects.filter(active=True).select_related("categorie")


@extend_schema(tags=["Alertes"], summary="Détail d'une alerte")
class AlerteDetailView(RetrieveAPIView):
    """GET /api/alertes/{id}/"""

    permission_classes = [AllowAny]
    serializer_class = AlerteSerializer
    queryset = Alerte.objects.filter(active=True).select_related("categorie")


@extend_schema(
    tags=["Conseils"],
    summary="Fiches de prévention",
    description="Conseils de sécurité ordonnés, servis à l'écran « Conseils ».",
)
class ConseilListView(ListAPIView):
    """GET /api/conseils/"""

    permission_classes = [AllowAny]
    serializer_class = ConseilSerializer
    queryset = Conseil.objects.filter(actif=True).select_related("categorie")
    # The list is short and read on every app launch — no pagination.
    pagination_class = None