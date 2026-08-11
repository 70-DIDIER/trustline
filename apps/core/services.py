"""Shared service helpers used across feature apps."""
from apps.core.models import LogAnalyse


def _serialiser_indices(indices):
    """Normalise indices to plain JSON-serialisable dicts.

    Callers pass either a :class:`~apps.scoring.engine.ResultatAnalyse` (whose
    indices are dataclasses), an already-serialised verdict dict, or the plain
    string list still used by a few legacy call sites.
    """
    if not indices:
        return []
    serialises = []
    for indice in indices:
        if hasattr(indice, "as_dict"):
            serialises.append(indice.as_dict())
        elif isinstance(indice, dict):
            serialises.append(indice)
        else:
            serialises.append({"code": "", "libelle": str(indice), "poids": 0})
    return serialises


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
        indices=_serialiser_indices(indices),
        source=source,
    )