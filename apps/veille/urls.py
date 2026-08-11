from django.urls import path

from apps.veille.views import AlerteDetailView, AlerteListView, ConseilListView

app_name = "veille"

urlpatterns = [
    path("alertes/", AlerteListView.as_view(), name="alertes"),
    path("alertes/<int:pk>/", AlerteDetailView.as_view(), name="alerte-detail"),
    path("conseils/", ConseilListView.as_view(), name="conseils"),
]