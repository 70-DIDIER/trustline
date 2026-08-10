"""Shared service helpers used across feature apps."""
from apps.core.models import LogAnalyse


def enregistrer_log(type_cible, cible, resultat, source="api"):
    """Persist a LogAnalyse row from a ResultatAnalyse-like object.

    ``resultat`` only needs ``score``, ``niveau_risque`` and ``indices``
    attributes, so both the scoring dataclass and plain dicts work.
    """
    score = getattr(resultat, "score", None)
    niveau = getattr(resultat, "niveau_risque", None)
    indices = getattr(resultat, "indices", None)
    if isinstance(resultat, dict):  # allow plain dicts too
        score = resultat.get("score", score)
        niveau = resultat.get("niveau_risque", niveau)
        indices = resultat.get("indices", indices)

    return LogAnalyse.objects.create(
        type_cible=type_cible,
        cible=str(cible)[:500],
        score_risque=score or 0,
        niveau_risque=niveau or "faible",
        indices=indices or [],
        source=source,
    )
