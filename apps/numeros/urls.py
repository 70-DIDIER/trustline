from django.urls import path, re_path

from apps.numeros.views import NumeroDetailView, VerifierNumeroView

app_name = "numeros"

urlpatterns = [
    path("verifier/", VerifierNumeroView.as_view(), name="verifier"),
    # Detail accepts a raw or +228 number (digits and a leading +).
    re_path(
        r"^(?P<numero>\+?[0-9]{6,15})/$",
        NumeroDetailView.as_view(),
        name="detail",
    ),
]
