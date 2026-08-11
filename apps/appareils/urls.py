from django.urls import path

from apps.appareils.views import EnregistrerAppareilView, ProfilAppareilView

app_name = "appareils"

urlpatterns = [
    path("", EnregistrerAppareilView.as_view(), name="enregistrer"),
    path("moi/", ProfilAppareilView.as_view(), name="profil"),
]