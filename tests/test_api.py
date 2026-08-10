"""End-to-end tests for the main API endpoints."""
import pytest
from rest_framework.test import APIClient

from apps.core.constants import CategorieCode, TypeCible
from apps.core.models import CategorieArnaque, ListeBlanche

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def categories():
    for code, libelle in [
        (CategorieCode.FRAUDE_FINANCIERE, "Fraude financière"),
        (CategorieCode.DEMANDE_OTP_PIN, "Demande OTP/PIN"),
        (CategorieCode.PHISHING, "Phishing"),
    ]:
        CategorieArnaque.objects.get_or_create(code=code, defaults={"libelle": libelle})


def test_health(client):
    reponse = client.get("/api/health/")
    assert reponse.status_code == 200
    assert reponse.json()["status"] == "ok"


def test_verifier_numero_liste_blanche_prioritaire(client):
    ListeBlanche.objects.create(numero="+22890000002", organisation="Mixx by Yas")
    reponse = client.post(
        "/api/numeros/verifier/", {"numero": "90000002"}, format="json"
    )
    assert reponse.status_code == 200
    data = reponse.json()
    assert data["est_liste_blanche"] is True
    assert data["niveau_risque"] == "faible"
    assert data["numero"] == "+22890000002"


@pytest.mark.parametrize(
    "saisie",
    ["90000002", "90 00 00 02", "90-00-00-02", "+228 90000002", "0022890000002"],
)
def test_verifier_numero_robuste_aux_formats(client, saisie):
    """Peu importe le format saisi par le citoyen, on retrouve le même numéro."""
    ListeBlanche.objects.get_or_create(
        numero="+22890000002", defaults={"organisation": "Mixx by Yas"}
    )
    reponse = client.post("/api/numeros/verifier/", {"numero": saisie}, format="json")
    assert reponse.status_code == 200
    assert reponse.json()["numero"] == "+22890000002"


def test_analyser_message_arnaque(client):
    contenu = (
        "Felicitations! Vous avez gagne 500000 FCFA. Envoyez votre code OTP "
        "immediatement pour recevoir votre prix."
    )
    reponse = client.post(
        "/api/messages/analyser/", {"contenu": contenu}, format="json"
    )
    assert reponse.status_code == 200
    data = reponse.json()
    assert data["niveau_risque"] == "eleve"
    assert data["score"] >= 70
    assert len(data["indices"]) >= 2


def test_signalement_isole_ne_bascule_pas_en_eleve(client, categories):
    reponse = client.post(
        "/api/signalements/",
        {
            "type_cible": TypeCible.NUMERO,
            "cible": "+22891234567",
            "categorie": CategorieCode.FRAUDE_FINANCIERE,
            "declarant_id": "declarant-unique",
        },
        format="json",
    )
    assert reponse.status_code == 201
    reputation = reponse.json()["reputation_cible"]
    # A single isolated report must never reach the "élevé" level.
    assert reputation["niveau_risque"] != "eleve"


def test_analyser_lien_raccourci_suspect(client):
    reponse = client.post(
        "/api/liens/analyser/", {"url": "http://bit.ly/gagnez-argent"}, format="json"
    )
    assert reponse.status_code == 200
    data = reponse.json()
    assert data["niveau_risque"] in {"suspect", "eleve"}
    assert data["score"] >= 30


def test_ussd_menu_principal(client):
    reponse = client.post("/api/ussd/simulate/", {"texte": ""}, format="json")
    assert reponse.status_code == 200
    data = reponse.json()
    assert data["type"] == "CON"
    assert "Vérifier un numéro" in data["message"]


def test_bot_verifier_format_conversationnel(client):
    reponse = client.post(
        "/api/bot/verifier/",
        {"texte": "Envoyez votre code PIN immediatement pour debloquer votre compte"},
        format="json",
    )
    assert reponse.status_code == 200
    data = reponse.json()
    assert data["niveau_risque"] in {"suspect", "eleve"}
    assert "reponse" in data
