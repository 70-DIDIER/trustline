"""Tests for the USSD endpoints (JSON simulator + Africa's Talking gateway)."""
import pytest
from rest_framework.test import APIClient

from apps.core.constants import CategorieCode, StatutSignalement
from apps.core.models import CategorieArnaque
from apps.numeros.models import Numero
from apps.signalements.models import Signalement

pytestmark = pytest.mark.django_db

URL = "/api/ussd/africastalking/"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def categorie_otp():
    cat, _ = CategorieArnaque.objects.get_or_create(
        code=CategorieCode.DEMANDE_OTP_PIN, defaults={"libelle": "Demande OTP/PIN"}
    )
    return cat


def _post(client, text, phone="+22890000111"):
    return client.post(
        URL,
        {"sessionId": "s1", "serviceCode": "*384*1#", "phoneNumber": phone, "text": text},
        format="multipart",
    )


def test_menu_principal_est_con(client):
    reponse = _post(client, "")
    assert reponse.status_code == 200
    corps = reponse.content.decode()
    assert corps.startswith("CON ")
    assert "Vérifier un numéro" in corps


def test_verifier_numero_signale_est_end(client):
    Numero.objects.create(
        numero="+22890112233", score_risque=77, niveau_risque="eleve",
        nombre_signalements=4,
    )
    reponse = _post(client, "1*90112233")
    corps = reponse.content.decode()
    assert corps.startswith("END ")
    assert "ELEVE" in corps
    assert "+22890112233" in corps


def test_signaler_cree_signalement_et_est_end(client, categorie_otp):
    reponse = _post(client, "2*79887766*6")
    corps = reponse.content.decode()
    assert corps.startswith("END ")
    assert Signalement.objects.filter(cible="+22879887766").count() == 1
    signalement = Signalement.objects.get(cible="+22879887766")
    assert signalement.categorie.code == CategorieCode.DEMANDE_OTP_PIN
    assert signalement.declarant == "ussd:+22890000111"


def test_categorie_invalide_redemande_con(client):
    reponse = _post(client, "2*79887766*9")
    corps = reponse.content.decode()
    assert corps.startswith("CON ")
    assert "invalide" in corps.lower()


def test_conseils_est_end(client):
    reponse = _post(client, "3")
    corps = reponse.content.decode()
    assert corps.startswith("END ")
    assert "OTP" in corps


def test_choix_invalide_est_end(client):
    reponse = _post(client, "9")
    assert reponse.content.decode().startswith("END ")


def test_reponse_est_texte_brut(client):
    reponse = _post(client, "")
    assert reponse["Content-Type"].startswith("text/plain")


def test_get_non_autorise(client):
    # AT n'utilise que POST ; un GET doit être refusé (405).
    assert client.get(URL).status_code == 405
