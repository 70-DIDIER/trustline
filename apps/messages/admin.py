"""Admin for analysed messages."""
from django.contrib import admin

from apps.messages.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("date_analyse", "verdict", "score_risque", "apercu")
    list_filter = ("verdict", "date_analyse")
    search_fields = ("contenu",)
    date_hierarchy = "date_analyse"

    @admin.display(description="Aperçu")
    def apercu(self, obj):
        return obj.contenu[:60]
