from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.messages"
    # IMPORTANT: avoid clashing with django.contrib.messages (label "messages").
    label = "messages_app"
    verbose_name = "Analyse de messages"
