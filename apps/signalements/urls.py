from django.urls import path

from apps.signalements.views import CreerSignalementView

app_name = "signalements"

urlpatterns = [
    path("", CreerSignalementView.as_view(), name="creer"),
]
