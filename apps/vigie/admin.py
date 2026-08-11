"""Admin view over Mode Vigie sessions (aggregates only — no audio, no words)."""
from django.contrib import admin

from apps.vigie.models import SessionVigie


@admin.register(SessionVigie)
class SessionVigieAdmin(admin.ModelAdmin):
    list_display = (
        "date_session",
        "duree_secondes",
        "score",
        "niveau_risque",
        "numero",
    )
    list_filter = ("niveau_risque", "date_session")
    date_hierarchy = "date_session"
    readonly_fields = ("appareil", "signaux")

    def has_add_permission(self, request):
        return False