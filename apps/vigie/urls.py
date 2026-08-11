from django.urls import path

from apps.vigie.views import (
    AnalyserTranscriptionView,
    CatalogueVigieView,
    SessionVigieView,
)

app_name = "vigie"

urlpatterns = [
    path("signaux/", CatalogueVigieView.as_view(), name="signaux"),
    path("analyser/", AnalyserTranscriptionView.as_view(), name="analyser"),
    path("sessions/", SessionVigieView.as_view(), name="sessions"),
]