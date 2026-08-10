from django.urls import path

from apps.messages.views import AnalyserMessageView

app_name = "messages"

urlpatterns = [
    path("analyser/", AnalyserMessageView.as_view(), name="analyser"),
]
