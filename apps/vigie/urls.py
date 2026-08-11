from django.urls import path

from apps.vigie.views import CatalogueVigieView, SessionVigieView

app_name = "vigie"

urlpatterns = [
    path("signaux/", CatalogueVigieView.as_view(), name="signaux"),
    path("sessions/", SessionVigieView.as_view(), name="sessions"),
]