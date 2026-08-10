"""Admin dashboard for reports: filters + moderation actions (jury dashboard)."""
from django.contrib import admin

from apps.core.constants import StatutSignalement
from apps.numeros.services import invalider_cache_numero
from apps.signalements.models import Signalement
from apps.signalements.reputation import mettre_a_jour_numero


@admin.register(Signalement)
class SignalementAdmin(admin.ModelAdmin):
    list_display = (
        "date_creation",
        "type_cible",
        "cible",
        "categorie",
        "declarant",
        "statut",
    )
    list_filter = ("statut", "categorie", "type_cible", "date_creation")
    search_fields = ("cible", "declarant", "commentaire")
    date_hierarchy = "date_creation"
    actions = ["marquer_valide", "marquer_conteste", "marquer_rejete"]

    # -- Helpers ---------------------------------------------------------
    def _appliquer_statut(self, request, queryset, statut, libelle):
        numeros = set()
        for signalement in queryset:
            signalement.statut = statut
            signalement.save(update_fields=["statut"])
            if signalement.numero_cible_id:
                numeros.add(signalement.numero_cible)
        # Recompute reputation once per impacted number.
        for numero in numeros:
            mettre_a_jour_numero(numero)
            invalider_cache_numero(numero.numero)
        self.message_user(
            request, f"{queryset.count()} signalement(s) marqué(s) « {libelle} »."
        )

    @admin.action(description="Valider les signalements sélectionnés")
    def marquer_valide(self, request, queryset):
        self._appliquer_statut(request, queryset, StatutSignalement.VALIDE, "validé")

    @admin.action(description="Contester les signalements sélectionnés")
    def marquer_conteste(self, request, queryset):
        self._appliquer_statut(
            request, queryset, StatutSignalement.CONTESTE, "contesté"
        )

    @admin.action(description="Rejeter les signalements sélectionnés")
    def marquer_rejete(self, request, queryset):
        self._appliquer_statut(request, queryset, StatutSignalement.REJETE, "rejeté")
