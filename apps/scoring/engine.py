"""Trustline detection engine v1 (rule-based, ML-ready).

``MoteurDetection`` is the single entry point used by every endpoint that needs
a verdict from free text. It combines:

1. a transparent, weighted **rule engine** (see ``rules.py``), and
2. an optional **community reputation** score injected by the caller, and
3. an optional **machine-learning model** (plugged in later by a teammate)
   through the ``ml_model`` argument — without rewriting any endpoint.

The result is a normalised :class:`ResultatAnalyse` (score, niveau_risque,
indices, recommandation) matching the API contract used across the project.
"""
from dataclasses import dataclass, field

from apps.core.utils import clamp_score, niveau_from_score, normaliser_texte
from apps.core.constants import NiveauRisque
from apps.scoring.rules import REGLES


@dataclass
class ResultatAnalyse:
    """Normalised verdict returned by the engine (matches the API contract)."""

    score: int = 0
    niveau_risque: str = NiveauRisque.FAIBLE
    indices: list[str] = field(default_factory=list)
    recommandation: str = ""
    categories: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "score": self.score,
            "niveau_risque": self.niveau_risque,
            "indices": self.indices,
            "recommandation": self.recommandation,
            "categories": self.categories,
        }


# Recommendation text per risk level (kept short for USSD / chat display).
_RECOMMANDATIONS = {
    NiveauRisque.FAIBLE: (
        "Aucun signal d'arnaque évident. Restez néanmoins vigilant et ne "
        "communiquez jamais vos codes."
    ),
    NiveauRisque.SUSPECT: (
        "Interaction suspecte. Ne cliquez sur aucun lien et ne partagez ni code "
        "ni argent avant d'avoir vérifié l'expéditeur par un canal officiel."
    ),
    NiveauRisque.ELEVE: (
        "Danger élevé : très probablement une arnaque. N'envoyez aucun code, "
        "aucun argent, ne cliquez sur aucun lien. Signalez ce contact."
    ),
}


class MoteurDetection:
    """Rule-based (and ML-ready) scam detection engine.

    Parameters
    ----------
    regles:
        Rule set to use. Defaults to the shared :data:`REGLES`.
    ml_model:
        Optional object exposing ``predict_proba([texte]) -> [[p_safe, p_scam]]``
        (scikit-learn convention) or a callable ``ml_model(texte) -> float`` in
        [0, 1]. When provided, its probability is blended with the rule score.
    poids_ml:
        Weight of the ML probability in the blend (0..1). ``0`` disables it.
    """

    def __init__(self, regles=None, ml_model=None, poids_ml: float = 0.5):
        self.regles = regles if regles is not None else REGLES
        self.ml_model = ml_model
        self.poids_ml = poids_ml

    # -- Public API ---------------------------------------------------------
    def analyser(self, texte: str, score_reputation: int = 0) -> ResultatAnalyse:
        """Analyse ``texte`` and return a normalised verdict.

        ``score_reputation`` (0-100) is the community reputation contribution
        computed elsewhere (e.g. from reports on numbers/links in the message).
        """
        texte = texte or ""
        # Rules match on a normalised copy (accent/case/spacing-insensitive);
        # the raw text is kept for the optional ML model.
        texte_norm = normaliser_texte(texte)

        score_regles, indices, categories = self._score_regles(texte_norm)

        # Blend rule score with the optional ML probability.
        score = score_regles
        if self.ml_model is not None and self.poids_ml > 0:
            score_ml = self._score_ml(texte)
            if score_ml is not None:
                score = round(
                    (1 - self.poids_ml) * score_regles + self.poids_ml * score_ml
                )
                indices.append("Score renforcé par le modèle d'apprentissage.")

        # Community reputation can only push the score up (never masks a scam).
        score = max(score, score_reputation)
        if score_reputation >= 1 and score_reputation >= score_regles:
            indices.append(
                "Cible déjà signalée par la communauté (réputation dégradée)."
            )

        score = clamp_score(score)
        niveau = niveau_from_score(score)

        return ResultatAnalyse(
            score=score,
            niveau_risque=niveau,
            indices=indices,
            recommandation=_RECOMMANDATIONS[niveau],
            categories=sorted(set(categories)),
        )

    # -- Rule engine --------------------------------------------------------
    def _score_regles(self, texte: str):
        """Run every rule and accumulate points, indices and categories.

        ``texte`` is expected to be already normalised (see ``analyser``).
        """
        points = 0
        indices: list[str] = []
        categories: list[str] = []
        regles_actives = set()

        for regle in self.regles:
            if regle.correspond(texte):
                regles_actives.add(regle.nom)

        for regle in self.regles:
            if regle.nom not in regles_actives:
                continue
            # Impersonation alone is weak; it only counts when paired with an
            # actual malicious action (OTP request, transfer, urgency, link).
            if regle.nom == "usurpation_service":
                actions = {
                    "demande_otp_pin",
                    "demande_transfert",
                    "urgence_artificielle",
                    "lien_suspect",
                }
                if not (regles_actives & actions):
                    continue
            points += regle.poids
            indices.append(regle.libelle)
            categories.append(str(regle.categorie))

        return clamp_score(points), indices, categories

    # -- ML hook (implemented later by the ML teammate) ---------------------
    def _score_ml(self, texte: str):
        """Return a 0-100 scam probability from ``self.ml_model`` (or None).

        Supports both a scikit-learn classifier (``predict_proba``) and a plain
        callable returning a probability in [0, 1].
        """
        model = self.ml_model
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba([texte])[0][1]
            elif callable(model):
                proba = model(texte)
            else:
                return None
            return clamp_score(float(proba) * 100)
        except Exception:
            # Never let a model error break the verdict — fall back to rules.
            return None


# A ready-to-use default instance (rules only, no ML yet).
moteur_par_defaut = MoteurDetection()
