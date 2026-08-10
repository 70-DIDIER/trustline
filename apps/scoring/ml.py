"""Optional ML model loading for the detection engine.

The model is a scikit-learn pipeline serialised with joblib (see
``ml/train_model.py``). Loading is lazy and defensive:

* ``joblib`` is imported only when a model path is configured, so the API
  server does not need scikit-learn/joblib installed unless ML is used;
* any failure (missing file, missing dependency, corrupt model) returns
  ``None`` → the engine simply stays in rule-only mode.
"""
import logging

from django.conf import settings

logger = logging.getLogger("trustline.ml")


def charger_modele():
    """Return a loaded ML model (sklearn pipeline) or ``None``.

    Reads ``settings.ML_MODEL_PATH``. Empty path → ML disabled (returns None).
    """
    chemin = getattr(settings, "ML_MODEL_PATH", "") or ""
    if not chemin:
        logger.info("[ml] ML_MODEL_PATH non défini → moteur en mode règles.")
        return None
    try:
        import joblib  # imported lazily on purpose

        modele = joblib.load(chemin)
        logger.info("[ml] modèle chargé depuis %s", chemin)
        return modele
    except Exception as exc:  # noqa: BLE001 — never break startup on ML issues
        logger.warning("[ml] échec du chargement du modèle (%s) : %s", chemin, exc)
        return None
