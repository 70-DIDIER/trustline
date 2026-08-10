from django.urls import path

from apps.moderation.views import StatsView

app_name = "moderation"

urlpatterns = [
    path("stats/", StatsView.as_view(), name="stats"),
]
