"""Admin for Numero — includes 'add to whitelist' action."""
from django.contrib import admin

from apps.core.models import ListeBlanche
from apps.numeros.models import Numero


@admin.register(Numero)
class NumeroAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "score_risque",
        "niveau_risque",
        "nombre_signalements",
        "date_dernier_signalement",
        "est_liste_blanche",
    )
    list_filter = ("niveau_risque", "est_liste_blanche")
    search_fields = ("numero",)
    ordering = ("-score_risque",)
    actions = ["ajouter_liste_blanche"]

    @admin.action(description="Ajouter à la liste blanche (numéros officiels)")
    def ajouter_liste_blanche(self, request, queryset):
        crees = 0
        for numero in queryset:
            _, created = ListeBlanche.objects.get_or_create(
                numero=numero.numero,
                defaults={"organisation": "À compléter", "source": "admin"},
            )
            numero.est_liste_blanche = True
            numero.score_risque = 0
            numero.niveau_risque = "faible"
            numero.save(
                update_fields=["est_liste_blanche", "score_risque", "niveau_risque"]
            )
            crees += int(created)
        self.message_user(
            request, f"{queryset.count()} numéro(s) ajouté(s) à la liste blanche."
        )
