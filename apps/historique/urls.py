from django.urls import path

from apps.historique.views import (
    HistoriqueDetailView,
    HistoriqueListView,
    HistoriqueViderView,
)

app_name = "historique"

urlpatterns = [
    path("", HistoriqueListView.as_view(), name="liste"),
    # Declared before the <int:pk> route so "vider" is never read as an id.
    path("vider/", HistoriqueViderView.as_view(), name="vider"),
    path("<int:pk>/", HistoriqueDetailView.as_view(), name="detail"),
]