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

from apps.core.views import health

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- Health check ---
    path("api/health/", health, name="health"),

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

    # --- Feature apps ---
    path("api/numeros/", include("apps.numeros.urls")),
    path("api/messages/", include("apps.messages.urls")),
    path("api/liens/", include("apps.liens.urls")),
    path("api/signalements/", include("apps.signalements.urls")),
    path("api/ussd/", include("apps.ussd.urls")),
    path("api/bot/", include("apps.bot.urls")),
    path("api/", include("apps.moderation.urls")),
]
