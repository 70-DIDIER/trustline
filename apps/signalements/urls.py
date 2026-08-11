from django.urls import path

from apps.signalements.views import CreerSignalementView, MesSignalementsView

app_name = "signalements"

urlpatterns = [
    path("", CreerSignalementView.as_view(), name="creer"),
    path("mes/", MesSignalementsView.as_view(), name="mes"),
]