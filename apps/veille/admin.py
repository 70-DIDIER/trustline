"""Back-office curation of alerts and prevention tips."""
from django.contrib import admin

from apps.veille.models import Alerte, Conseil


@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = (
        "titre",
        "niveau_risque",
        "canal",
        "nombre_signalements",
        "epinglee",
        "active",
        "date_debut",
    )
    list_filter = ("niveau_risque", "canal", "active", "epinglee")
    search_fields = ("titre", "description")
    list_editable = ("epinglee", "active")
    date_hierarchy = "date_debut"


@admin.register(Conseil)
class ConseilAdmin(admin.ModelAdmin):
    list_display = ("ordre", "titre", "actif")
    list_filter = ("actif",)
    search_fields = ("titre", "resume")
    list_editable = ("actif",)
    ordering = ("ordre",)