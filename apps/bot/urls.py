from django.urls import path

from apps.bot.views import BotVerifierView

app_name = "bot"

urlpatterns = [
    path("verifier/", BotVerifierView.as_view(), name="verifier"),
]
