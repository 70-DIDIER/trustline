"""Admin registrations for core referential models."""
from django.contrib import admin

from apps.core.models import CategorieArnaque, ListeBlanche, LogAnalyse


@admin.register(CategorieArnaque)
class CategorieArnaqueAdmin(admin.ModelAdmin):
    list_display = ("libelle", "code")
    search_fields = ("libelle", "code")


@admin.register(ListeBlanche)
class ListeBlancheAdmin(admin.ModelAdmin):
    list_display = ("numero", "organisation", "source", "date_ajout")
    search_fields = ("numero", "organisation")
    list_filter = ("organisation",)


@admin.register(LogAnalyse)
class LogAnalyseAdmin(admin.ModelAdmin):
    list_display = (
        "date_analyse",
        "type_cible",
        "cible",
        "score_risque",
        "niveau_risque",
        "source",
    )
    list_filter = ("type_cible", "niveau_risque", "source", "date_analyse")
    search_fields = ("cible",)
    date_hierarchy = "date_analyse"
