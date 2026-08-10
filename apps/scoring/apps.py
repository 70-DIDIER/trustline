from django.apps import AppConfig


class ScoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.scoring"
    verbose_name = "Moteur de détection"

    def ready(self):
        """Attach the optional ML model to the default engine, if available.

        If no model is configured/loadable, the engine stays in rule-only mode.
        """
        from django.conf import settings

        from apps.scoring import engine, ml

        modele = ml.charger_modele()
        if modele is not None:
            engine.moteur_par_defaut.ml_model = modele
            engine.moteur_par_defaut.poids_ml = getattr(settings, "ML_POIDS", 0.5)
