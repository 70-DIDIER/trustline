"""Community reputation & anti-abuse weighting.

A single isolated report must NEVER be enough to flag a number as high-risk.
The reputation score combines three signals:

* **volume & recency** — each non-rejected report contributes points that decay
  with age (half-life ~30 days), so stale reports weigh less;
* **distinct reporters** — a hard cap keyed on the number of *distinct* reporters
  prevents one person (or a small coordinated group) from pushing a number to
  "élevé" on their own;
* **category diversity** — reports spread across several scam categories are a
  stronger signal than many identical ones.
"""
import math

from django.utils import timezone

from apps.core.constants import StatutSignalement
from apps.core.utils import clamp_score, niveau_from_score

# --- Tunable constants (easy to justify / adjust for the jury) ---
DEMI_VIE_JOURS = 30          # recency half-life
POINTS_PAR_SIGNALEMENT = 18  # points for one fresh, validated report
BONUS_DIVERSITE = 8          # points per extra distinct category

# Weight of a report depending on its moderation status.
POIDS_STATUT = {
    StatutSignalement.VALIDE: 1.0,
    StatutSignalement.EN_ATTENTE: 0.6,
    StatutSignalement.CONTESTE: 0.3,
    StatutSignalement.REJETE: 0.0,
}

# Anti-abuse ceiling by number of DISTINCT reporters.
# 1 reporter -> at most "suspect" (never "élevé"); more reporters raise the cap.
PLAFOND_PAR_DECLARANTS = {0: 0, 1: 45, 2: 65}
PLAFOND_MAX = 100


def _facteur_recence(date_creation, maintenant) -> float:
    """Exponential decay factor in [0, 1] based on the report age."""
    age_jours = max(0.0, (maintenant - date_creation).total_seconds() / 86400)
    return 0.5 ** (age_jours / DEMI_VIE_JOURS)


def calculer_score_reputation(signalements) -> int:
    """Compute a 0-100 reputation score from an iterable of Signalement rows."""
    signalements = list(signalements)
    if not signalements:
        return 0

    maintenant = timezone.now()
    points = 0.0
    declarants = set()
    categories = set()

    for s in signalements:
        poids_statut = POIDS_STATUT.get(s.statut, 0.0)
        if poids_statut == 0.0:
            continue
        points += POINTS_PAR_SIGNALEMENT * poids_statut * _facteur_recence(
            s.date_creation, maintenant
        )
        declarants.add(s.declarant)
        categories.add(s.categorie_id)

    if not declarants:
        return 0

    # Diversity bonus for distinct categories beyond the first.
    score = points + BONUS_DIVERSITE * max(0, len(categories) - 1)

    # Anti-abuse ceiling based on the number of distinct reporters.
    plafond = PLAFOND_PAR_DECLARANTS.get(len(declarants), PLAFOND_MAX)
    score = min(score, plafond)

    return clamp_score(score)


def mettre_a_jour_numero(numero):
    """Recompute and persist the reputation of a Numero from its reports.

    Returns the refreshed Numero instance.
    """
    signalements = list(numero.signalements.all())
    non_rejetes = [s for s in signalements if s.statut != StatutSignalement.REJETE]

    if numero.est_liste_blanche:
        # Whitelisted numbers are always trusted regardless of reports.
        numero.score_risque = 0
        numero.niveau_risque = niveau_from_score(0)
    else:
        score = calculer_score_reputation(non_rejetes)
        numero.score_risque = score
        numero.niveau_risque = niveau_from_score(score)

    numero.nombre_signalements = len(non_rejetes)
    numero.date_dernier_signalement = (
        max((s.date_creation for s in non_rejetes), default=None)
    )
    numero.save(
        update_fields=[
            "score_risque",
            "niveau_risque",
            "nombre_signalements",
            "date_dernier_signalement",
        ]
    )
    return numero
