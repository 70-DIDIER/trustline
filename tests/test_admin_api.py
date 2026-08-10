"""Tests for the admin REST API (JWT + admin only)."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.core.constants import CategorieCode, StatutSignalement, TypeCible
from apps.core.models import CategorieArnaque, ListeBlanche
from apps.numeros.models import Numero
from apps.signalements.services import creer_signalement

pytestmark = pytest.mark.django_db

User = get_user_model()


@pytest.fixture
def admin_client():
    admin = User.objects.create_user("admin", password="x", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=admin)
    return client


@pytest.fixture
def categorie():
    cat, _ = CategorieArnaque.objects.get_or_create(
        code=CategorieCode.DEMANDE_OTP_PIN, defaults={"libelle": "OTP"}
    )
    return cat


# --- Protection ----------------------------------------------------------

def test_admin_endpoints_exigent_authentification():
    client = APIClient()  # anonyme
    for url in [
        "/api/admin/signalements/",
        "/api/admin/numeros/",
        "/api/admin/liste-blanche/",
        "/api/admin/messages/",
        "/api/admin/logs/",
    ]:
        assert client.get(url).status_code in (401, 403), url


def test_utilisateur_non_staff_refuse():
    user = User.objects.create_user("bob", password="x", is_staff=False)
    client = APIClient()
    client.force_authenticate(user=user)
    assert client.get("/api/admin/signalements/").status_code == 403


# --- Signalements + modération -------------------------------------------

def test_lister_et_filtrer_signalements(admin_client, categorie):
    creer_signalement(
        type_cible=TypeCible.NUMERO, cible="90112233",
        categorie_code=CategorieCode.DEMANDE_OTP_PIN, declarant="d1",
    )
    reponse = admin_client.get("/api/admin/signalements/")
    assert reponse.status_code == 200
    assert reponse.json()["count"] == 1  # réponse paginée

    # Filtre par statut inexistant -> 0
    r2 = admin_client.get("/api/admin/signalements/?statut=valide")
    assert r2.json()["count"] == 0


def test_moderer_signalement_recalcule_reputation(admin_client, categorie):
    signalement, numero = creer_signalement(
        type_cible=TypeCible.NUMERO, cible="90112233",
        categorie_code=CategorieCode.DEMANDE_OTP_PIN, declarant="d1",
    )
    url = f"/api/admin/signalements/{signalement.id}/moderer/"
    reponse = admin_client.post(url, {"action": StatutSignalement.VALIDE}, format="json")
    assert reponse.status_code == 200
    assert reponse.json()["statut"] == "valide"


# --- Numéros + liste blanche ---------------------------------------------

def test_ajouter_numero_liste_blanche(admin_client):
    numero = Numero.objects.create(numero="+22890445566", score_risque=50, niveau_risque="suspect")
    url = f"/api/admin/numeros/{numero.id}/liste-blanche/"
    reponse = admin_client.post(url, {"organisation": "Banque X"}, format="json")
    assert reponse.status_code == 200
    data = reponse.json()
    assert data["est_liste_blanche"] is True
    assert data["score_risque"] == 0
    assert ListeBlanche.objects.filter(numero="+22890445566").exists()


# --- Liste blanche CRUD --------------------------------------------------

def test_creer_et_supprimer_liste_blanche(admin_client):
    creer = admin_client.post(
        "/api/admin/liste-blanche/",
        {"numero": "+22890000002", "organisation": "Mixx", "source": "officiel"},
        format="json",
    )
    assert creer.status_code == 201
    entry_id = creer.json()["id"]

    supprimer = admin_client.delete(f"/api/admin/liste-blanche/{entry_id}/")
    assert supprimer.status_code == 204
    assert not ListeBlanche.objects.filter(id=entry_id).exists()
