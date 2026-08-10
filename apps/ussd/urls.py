from django.urls import path

from apps.ussd.views import UssdSimulateView

app_name = "ussd"

urlpatterns = [
    path("simulate/", UssdSimulateView.as_view(), name="simulate"),
]
