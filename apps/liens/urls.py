from django.urls import path

from apps.liens.views import AnalyserLienView

app_name = "liens"

urlpatterns = [
    path("analyser/", AnalyserLienView.as_view(), name="analyser"),
]
