"""Admin view over per-device verification history."""
from django.contrib import admin

from apps.historique.models import Verification


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = (
        "date_verification",
        "type_verification",
        "resume",
        "score",
        "niveau_risque",
    )
    list_filter = ("type_verification", "niveau_risque", "date_verification")
    search_fields = ("cible", "resume")
    date_hierarchy = "date_verification"
    readonly_fields = ("appareil", "verdict")