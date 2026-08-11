"""Root URL configuration for the Trustline backend.

All API endpoints live under ``/api/``. Interactive documentation is served
by drf-spectacular at ``/api/docs/`` (Swagger UI).
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.appareils.views import AccueilView
from apps.bot.webhooks import GupshupWebhookView
from apps.core.views import health

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- Health check ---
    path("api/health/", health, name="health"),

    # --- Webhook WhatsApp (Gupshup Sandbox) ---
    path("api/webhook/gupshup/", GupshupWebhookView.as_view(), name="webhook-gupshup"),

    # --- Auth JWT (endpoints admin / modération) ---
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # --- OpenAPI schema + Swagger UI ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # --- Application mobile : identité anonyme + écran d'accueil ---
    path("api/appareils/", include("apps.appareils.urls")),
    path("api/accueil/", AccueilView.as_view(), name="accueil"),

    # --- Feature apps ---
    path("api/numeros/", include("apps.numeros.urls")),
    path("api/messages/", include("apps.messages.urls")),
    path("api/liens/", include("apps.liens.urls")),
    path("api/signalements/", include("apps.signalements.urls")),
    path("api/historique/", include("apps.historique.urls")),
    path("api/vigie/", include("apps.vigie.urls")),
    path("api/", include("apps.veille.urls")),
    path("api/ussd/", include("apps.ussd.urls")),
    path("api/bot/", include("apps.bot.urls")),
    path("api/", include("apps.moderation.urls")),
]
