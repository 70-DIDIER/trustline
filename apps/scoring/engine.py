"""Trustline detection engine v1 (rule-based, ML-ready).

``MoteurDetection`` is the single entry point used by every endpoint that needs
a verdict from free text. It combines:

1. a transparent, weighted **rule engine** (see ``rules.py``), and
2. an optional **community reputation** score injected by the caller, and
3. an optional **machine-learning model** (plugged in later by a teammate)
   through the ``ml_model`` argument — without rewriting any endpoint.

The result is a normalised :class:`ResultatAnalyse`. Every verdict carries the
*structured* evidence that produced it (``indices``: code, libellé, poids,
detail, catégorie) so the mobile app can explain each signal to the user
instead of showing an opaque score.
"""
import time
from dataclasses import dataclass, field

from apps.core.constants import NiveauRisque
from apps.core.utils import clamp_score, niveau_from_score, normaliser_texte
from apps.scoring.rules import REGLES


@dataclass
class Indice:
    """One piece of evidence behind a verdict, ready to be shown to the user."""

    code: str
    libelle: str
    poids: int = 0
    detail: str = ""
    categorie: str = ""

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "libelle": self.libelle,
            "poids": self.poids,
            "detail": self.detail,
            "categorie": self.categorie,
        }


@dataclass
class ResultatAnalyse:
    """Normalised verdict returned by the engine (matches the API contract)."""

    score: int = 0
    niveau_risque: str = NiveauRisque.FAIBLE
    indices: list[Indice] = field(default_factory=list)
    recommandation: str = ""
    categories: list[str] = field(default_factory=list)
    explication: str = ""
    action_recommandee: str = ""
    confiance: float = 0.0
    duree_ms: int = 0

    def as_dict(self) -> dict:
        return {
            "score": self.score,
            "niveau_risque": self.niveau_risque,
            "indices": [i.as_dict() for i in self.indices],
            "recommandation": self.recommandation,
            "categories": self.categories,
            "explication": self.explication,
            "action_recommandee": self.action_recommandee,
            "confiance": round(self.confiance, 2),
            "duree_ms": self.duree_ms,
        }

    @property
    def libelles_indices(self) -> list[str]:
        """Flat list of headlines — used by the plain-text channels (USSD, bot)."""
        return [i.libelle for i in self.indices]


# Short "what to do now" line per risk level (kept short for USSD / chat display).
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

# Longer narrative shown on the result screen ("Pourquoi ce verdict ?").
_EXPLICATIONS = {
    NiveauRisque.FAIBLE: (
        "Aucun motif d'arnaque connu n'a été identifié dans ce contenu. Cela ne "
        "garantit pas son authenticité : restez prudent si on vous demande un "
        "code, un paiement ou des données personnelles."
    ),
    NiveauRisque.SUSPECT: (
        "Ce contenu présente des signaux partiellement associés à des arnaques "
        "connues. Il peut être légitime, mais il mérite une vérification auprès "
        "du service concerné, par un canal officiel que vous choisissez vous-même."
    ),
    NiveauRisque.ELEVE: (
        "Ce contenu combine plusieurs techniques de manipulation observées dans "
        "les campagnes frauduleuses au Togo. Le mécanisme consiste à créer un "
        "sentiment d'urgence ou d'aubaine pour vous pousser à agir avant d'avoir "
        "vérifié."
    ),
}

# The single concrete gesture to perform right now.
_ACTIONS = {
    NiveauRisque.FAIBLE: (
        "Aucune action particulière. Restez vigilant si on vous demande un code, "
        "un paiement ou vos identifiants."
    ),
    NiveauRisque.SUSPECT: (
        "Ne transmettez aucun code. Contactez le service concerné via un numéro "
        "officiel que vous avez trouvé vous-même, pas celui du message."
    ),
    NiveauRisque.ELEVE: (
        "Ne répondez pas, ne composez aucun code, ne cliquez sur aucun lien. "
        "Supprimez le message et signalez-le pour protéger les autres."
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
        debut = time.perf_counter()
        texte = texte or ""
        # Rules match on a normalised copy (accent/case/spacing-insensitive);
        # the raw text is kept for the optional ML model.
        texte_norm = normaliser_texte(texte)

        score_regles, indices, categories = self._score_regles(texte_norm)

        # Blend rule score with the optional ML probability.
        score = score_regles
        renfort_ml = False
        if self.ml_model is not None and self.poids_ml > 0:
            score_ml = self._score_ml(texte)
            if score_ml is not None:
                score = round(
                    (1 - self.poids_ml) * score_regles + self.poids_ml * score_ml
                )
                renfort_ml = True
                indices.append(
                    Indice(
                        code="modele_ml",
                        libelle="Score confirmé par le modèle d'apprentissage.",
                        poids=0,
                        detail=(
                            "Un classifieur entraîné sur des messages frauduleux "
                            f"réels estime le risque à {score_ml}/100."
                        ),
                        categorie="",
                    )
                )

        # Community reputation can only push the score up (never masks a scam).
        score = max(score, score_reputation)
        if score_reputation >= 1 and score_reputation >= score_regles:
            indices.append(
                Indice(
                    code="reputation_communautaire",
                    libelle="Cible déjà signalée par la communauté.",
                    poids=0,
                    detail=(
                        "Un numéro ou un lien présent dans ce contenu a déjà fait "
                        "l'objet de signalements validés par d'autres utilisateurs."
                    ),
                    categorie="",
                )
            )

        score = clamp_score(score)
        niveau = niveau_from_score(score)
        duree_ms = int((time.perf_counter() - debut) * 1000)

        return ResultatAnalyse(
            score=score,
            niveau_risque=niveau,
            indices=indices,
            recommandation=_RECOMMANDATIONS[niveau],
            categories=sorted({c for c in categories if c}),
            explication=_EXPLICATIONS[niveau],
            action_recommandee=_ACTIONS[niveau],
            confiance=self._confiance(indices, renfort_ml),
            duree_ms=duree_ms,
        )

    # -- Rule engine --------------------------------------------------------
    def _score_regles(self, texte: str):
        """Run every rule and accumulate points, indices and categories.

        ``texte`` is expected to be already normalised (see ``analyser``).
        """
        points = 0
        indices: list[Indice] = []
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
            indices.append(
                Indice(
                    code=regle.nom,
                    libelle=regle.libelle,
                    poids=regle.poids,
                    detail=regle.detail,
                    categorie=str(regle.categorie),
                )
            )
            categories.append(str(regle.categorie))

        return clamp_score(points), indices, categories

    # -- Confidence ---------------------------------------------------------
    @staticmethod
    def _confiance(indices, renfort_ml: bool) -> float:
        """How sure the engine is about its own verdict, in [0, 1].

        A verdict backed by several independent rules is more trustworthy than
        one resting on a single keyword; the ML model adds a further boost.
        The value is *never* 1.0 — the engine assists a human decision, it does
        not replace it.
        """
        base = 0.55 + 0.09 * len({i.code for i in indices})
        if renfort_ml:
            base += 0.08
        return round(min(base, 0.95), 2)

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