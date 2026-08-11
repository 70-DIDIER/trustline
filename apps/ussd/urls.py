from django.urls import path

from apps.ussd.views import UssdSimulateView, africastalking_ussd

app_name = "ussd"

urlpatterns = [
    path("simulate/", UssdSimulateView.as_view(), name="simulate"),
    path("africastalking/", africastalking_ussd, name="africastalking"),
]
