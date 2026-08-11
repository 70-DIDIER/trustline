"""Admin view over anonymous devices (read-only by design)."""
from django.contrib import admin

from apps.appareils.models import Appareil


@admin.register(Appareil)
class AppareilAdmin(admin.ModelAdmin):
    list_display = (
        "device_id",
        "plateforme",
        "version_app",
        "date_creation",
        "derniere_activite",
    )
    list_filter = ("plateforme", "date_creation")
    search_fields = ("device_id",)
    readonly_fields = ("device_id", "date_creation", "derniere_activite")

    def has_add_permission(self, request):
        # Devices register themselves through the API, never from the back-office.
        return False