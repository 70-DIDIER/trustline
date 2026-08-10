"""Unit tests for the rule-based detection engine (no DB needed)."""
import pytest

from apps.core.utils import normaliser_texte
from apps.scoring.engine import MoteurDetection

pytestmark = pytest.mark.django_db  # settings access (thresholds) needs Django


def test_message_arnaque_detecte_otp_et_gain():
    moteur = MoteurDetection()
    texte = (
        "Felicitations vous avez gagne 1000000 FCFA. Envoyez votre code OTP "
        "immediatement sinon votre compte sera bloque."
    )
    resultat = moteur.analyser(texte)
    assert resultat.niveau_risque == "eleve"
    assert resultat.score >= 70
    # The main scam signals must be surfaced as indices.
    joint = " ".join(resultat.indices).lower()
    assert "otp" in joint or "code" in joint
    assert "gain" in joint or "concours" in joint


def test_message_benin_reste_faible():
    moteur = MoteurDetection()
    resultat = moteur.analyser("Salut, on se voit demain a 15h pour le cafe ?")
    assert resultat.niveau_risque == "faible"
    assert resultat.score == 0


def test_reputation_communautaire_ne_masque_pas_un_texte_sain():
    moteur = MoteurDetection()
    # An injected reputation score should push the verdict up.
    resultat = moteur.analyser("Bonjour", score_reputation=80)
    assert resultat.score >= 80
    assert resultat.niveau_risque == "eleve"


def test_modele_ml_branchable_sans_toucher_aux_regles():
    # A dummy ML callable returning a high scam probability.
    moteur = MoteurDetection(ml_model=lambda texte: 0.9, poids_ml=1.0)
    resultat = moteur.analyser("texte neutre")
    assert resultat.score >= 70  # driven entirely by the ML hook


# --- Robustesse face aux SMS réels (normalisation) -----------------------

def test_normaliser_texte_accents_casse_espaces():
    # Accents removed, lower-cased, exotic spaces collapsed.
    brut = "FÉLICITATIONS !  Votre  CODE​ OTP"
    assert normaliser_texte(brut) == "felicitations ! votre code otp"


@pytest.mark.parametrize(
    "texte",
    [
        # Avec accents (référence)
        "Félicitations, envoyez votre code OTP immédiatement",
        # Sans accents (cas très fréquent au Togo)
        "Felicitations, envoyez votre code OTP immediatement",
        # Tout en majuscules
        "FELICITATIONS ENVOYEZ VOTRE CODE OTP IMMEDIATEMENT",
        # Espaces insécables / zero-width (copier-coller)
        "Felicitations, envoyez votre code​ OTP immediatement",
    ],
)
def test_detection_robuste_variantes_ecriture(texte):
    """Toutes ces variantes du même SMS doivent donner un verdict élevé."""
    resultat = MoteurDetection().analyser(texte)
    assert resultat.niveau_risque == "eleve"
    assert resultat.score >= 70


def test_nouvelles_formulations_verbales_detectees():
    # Verb forms / phrasings added to the ruleset.
    moteur = MoteurDetection()
    r1 = moteur.analyser("Verifiez votre compte Ecobank sans tarder")
    assert "verif" in " ".join(r1.indices).lower() or r1.score >= 30
    r2 = moteur.analyser("Vous etes selectionne pour une recompense de 100000 FCFA")
    assert r2.niveau_risque in {"suspect", "eleve"}


def test_montant_avec_accents_et_espaces_toujours_detecte():
    moteur = MoteurDetection()
    resultat = moteur.analyser("Transférez 2.000.000 FCFA sur ce compte")
    joint = " ".join(resultat.indices).lower()
    assert "transfert" in joint or "argent" in joint
