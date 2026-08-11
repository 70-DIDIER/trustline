"""Tests for the endpoints the mobile application depends on.

The app is anonymous: everything personal (history, reports, profile) hangs off
the ``X-Device-Id`` header. These tests pin that contract down.
"""
import uuid

import pytest
from rest_framework.test import APIClient

from apps.core.constants import CategorieCode, NiveauRisque, TypeCible
from apps.core.models import CategorieArnaque
from apps.veille.models import Alerte, Conseil

pytestmark = pytest.mark.django_db

DEVICE = str(uuid.uuid4())
AUTRE_DEVICE = str(uuid.uuid4())


@pytest.fixture
def client():
    """Client identified as a mobile device."""
    return APIClient(headers={"X-Device-Id": DEVICE, "X-App-Version": "1.0.0"})


@pytest.fixture
def client_anonyme():
    """Client without any device header (browser extension, USSD gateway…)."""
    return APIClient()


@pytest.fixture
def categories():
    for code, libelle in [
        (CategorieCode.FRAUDE_FINANCIERE, "Fraude financière"),
        (CategorieCode.DEMANDE_OTP_PIN, "Demande OTP/PIN"),
        (CategorieCode.PHISHING, "Phishing"),
    ]:
        CategorieArnaque.objects.get_or_create(code=code, defaults={"libelle": libelle})


# --- Identité appareil ----------------------------------------------------

def test_enregistrement_appareil_est_idempotent(client):
    premier = client.post("/api/appareils/", {"plateforme": "android"}, format="json")
    second = client.post("/api/appareils/", {"plateforme": "android"}, format="json")

    assert premier.status_code == 200
    assert second.status_code == 200
    assert premier.json()["device_id"] == second.json()["device_id"] == DEVICE


def test_profil_refuse_un_device_id_manquant(client_anonyme):
    reponse = client_anonyme.get("/api/appareils/moi/")
    assert reponse.status_code == 400
    assert "device_id" in reponse.json()


def test_profil_refuse_un_device_id_non_uuid():
    client = APIClient(headers={"X-Device-Id": "pas-un-uuid"})
    assert client.get("/api/appareils/moi/").status_code == 400


# --- Historique -----------------------------------------------------------

def test_analyse_alimente_l_historique_de_l_appareil(client):
    client.post(
        "/api/messages/analyser/",
        {"contenu": "Envoyez votre code OTP immediatement, compte bloque"},
        format="json",
    )
    reponse = client.get("/api/historique/")

    assert reponse.status_code == 200
    resultats = reponse.json()["results"]
    assert len(resultats) == 1
    assert resultats[0]["type_verification"] == "message"
    # The whole verdict is stored so the detail screen works offline.
    assert resultats[0]["verdict"]["indices"]


def test_historique_est_cloisonne_par_appareil(client):
    client.post("/api/messages/analyser/", {"contenu": "code OTP urgent"}, format="json")

    voisin = APIClient(headers={"X-Device-Id": AUTRE_DEVICE})
    assert voisin.get("/api/historique/").json()["results"] == []


def test_analyse_sans_device_id_ne_casse_rien(client_anonyme):
    """L'extension navigateur n'a pas d'identité : le verdict doit sortir quand même."""
    reponse = client_anonyme.post(
        "/api/liens/analyser/", {"url": "http://bit.ly/gagnez"}, format="json"
    )
    assert reponse.status_code == 200
    assert reponse.json()["score"] > 0


def test_suppression_d_une_entree_d_historique(client):
    client.post("/api/messages/analyser/", {"contenu": "code OTP urgent"}, format="json")
    entree = client.get("/api/historique/").json()["results"][0]

    assert client.delete(f"/api/historique/{entree['id']}/").status_code == 204
    assert client.get("/api/historique/").json()["results"] == []


def test_vider_l_historique(client):
    for contenu in ["code OTP urgent", "vous avez gagne 500000 FCFA"]:
        client.post("/api/messages/analyser/", {"contenu": contenu}, format="json")

    reponse = client.delete("/api/historique/vider/")
    assert reponse.status_code == 200
    assert reponse.json()["supprimes"] == 2
    assert client.get("/api/historique/").json()["results"] == []


def test_verification_de_numero_en_contexte_appel(client):
    client.post("/api/numeros/verifier/?contexte=appel", {"numero": "90112233"}, format="json")
    resultats = client.get("/api/historique/").json()["results"]
    assert resultats[0]["type_verification"] == "appel"


# --- Verdicts expliqués ---------------------------------------------------

def test_verdict_message_porte_ses_indices_structures(client):
    reponse = client.post(
        "/api/messages/analyser/",
        {"contenu": "Felicitations! Envoyez votre code OTP pour recevoir 500000 FCFA"},
        format="json",
    )
    data = reponse.json()

    assert data["niveau_risque"] == NiveauRisque.ELEVE
    premier = data["indices"][0]
    assert {"code", "libelle", "poids", "detail", "categorie"} <= set(premier)
    # Every verdict explains itself and proposes one concrete gesture.
    assert data["explication"] and data["action_recommandee"]
    assert 0 < data["confiance"] < 1


def test_verdict_numero_expose_les_declarants_distincts(client, categories):
    for declarant in ["decl-1", "decl-2"]:
        APIClient().post(
            "/api/signalements/",
            {
                "type_cible": TypeCible.NUMERO,
                "cible": "+22890445566",
                "categorie": CategorieCode.FRAUDE_FINANCIERE,
                "declarant_id": declarant,
            },
            format="json",
        )

    data = client.post(
        "/api/numeros/verifier/", {"numero": "90445566"}, format="json"
    ).json()

    assert data["nombre_signalements"] == 2
    assert data["nombre_declarants"] == 2
    assert data["numero_formate"] == "+228 90 44 55 66"


# --- Signalements ---------------------------------------------------------

def test_signalement_depuis_l_app_porte_une_reference(client, categories):
    reponse = client.post(
        "/api/signalements/",
        {
            "type_cible": TypeCible.NUMERO,
            "cible": "90112233",
            "categorie": CategorieCode.DEMANDE_OTP_PIN,
            "montant_perdu": 15000,
        },
        format="json",
    )
    assert reponse.status_code == 201
    data = reponse.json()
    assert data["reference"].startswith("TL-")
    assert data["montant_perdu"] == 15000
    assert data["reputation_cible"]["numero_formate"] == "+228 90 11 22 33"


def test_mes_signalements_ne_montrent_que_ceux_de_l_appareil(client, categories):
    client.post(
        "/api/signalements/",
        {
            "type_cible": TypeCible.NUMERO,
            "cible": "90112233",
            "categorie": CategorieCode.DEMANDE_OTP_PIN,
        },
        format="json",
    )
    APIClient(headers={"X-Device-Id": AUTRE_DEVICE}).post(
        "/api/signalements/",
        {
            "type_cible": TypeCible.LIEN,
            "cible": "http://faux-site.xyz",
            "categorie": CategorieCode.PHISHING,
        },
        format="json",
    )

    resultats = client.get("/api/signalements/mes/").json()["results"]
    assert len(resultats) == 1
    assert resultats[0]["cible"] == "+22890112233"


# --- Veille : alertes & conseils ------------------------------------------

def test_alertes_epinglees_remontent_en_tete(client_anonyme):
    Alerte.objects.create(titre="Ancienne campagne", description="…")
    Alerte.objects.create(titre="À la une", description="…", epinglee=True)
    Alerte.objects.create(titre="Terminée", description="…", active=False)

    titres = [a["titre"] for a in client_anonyme.get("/api/alertes/").json()["results"]]
    assert titres == ["À la une", "Ancienne campagne"]


def test_conseils_servis_dans_l_ordre(client_anonyme):
    Conseil.objects.create(titre="Second", resume="…", ordre=2)
    Conseil.objects.create(titre="Premier", resume="…", ordre=1, points=["a", "b"])

    conseils = client_anonyme.get("/api/conseils/").json()
    assert [c["titre"] for c in conseils] == ["Premier", "Second"]
    assert conseils[0]["points"] == ["a", "b"]


# --- Mode Vigie -----------------------------------------------------------

def test_catalogue_vigie_livre_les_motifs_a_appliquer_localement(client_anonyme):
    data = client_anonyme.get("/api/vigie/signaux/").json()

    assert data["version"]
    codes = {s["code"] for s in data["signaux"]}
    assert "demande_otp_pin" in codes
    # Voice-only signals complete the shared rule set.
    assert "menace_suspension" in codes
    assert all(s["motifs"] for s in data["signaux"])


def test_analyse_transcription_vigie_repere_les_signaux_oraux(client):
    reponse = client.post(
        "/api/vigie/analyser/",
        {
            "texte": "Bonjour je suis un agent de votre operateur, votre compte "
            "sera bloque. Envoyez moi le code de verification immediatement "
            "et ne dites rien a personne.",
        },
        format="json",
    )
    assert reponse.status_code == 200
    data = reponse.json()

    codes = set(data["signaux"])
    # Règles partagées avec l'analyse de SMS…
    assert "demande_otp_pin" in codes
    # …et signaux propres à l'oral, absents de REGLES.
    assert {"identite_pretendue", "menace_suspension", "insistance_secret"} <= codes
    assert data["niveau_risque"] == NiveauRisque.ELEVE
    assert all(i["libelle"] for i in data["indices"])


def test_analyse_transcription_vigie_ne_persiste_jamais_le_texte(client):
    """La transcription transite pour être analysée, elle ne doit rien laisser.

    C'est la contrepartie du consentement demandé dans l'application : le texte
    est scoré en mémoire puis abandonné. `/api/messages/analyser/` le stocke,
    lui, dans Message et LogAnalyse — d'où l'endpoint distinct.
    """
    from apps.core.models import LogAnalyse
    from apps.messages.models import Message

    secret = "envoyez le code 4321 a mon numero personnel"
    avant_logs = LogAnalyse.objects.count()
    avant_messages = Message.objects.count()

    assert client.post(
        "/api/vigie/analyser/", {"texte": secret}, format="json"
    ).status_code == 200

    assert LogAnalyse.objects.count() == avant_logs
    assert Message.objects.count() == avant_messages
    assert not LogAnalyse.objects.filter(cible__icontains="4321").exists()


def test_analyse_transcription_vigie_exige_un_appareil(client_anonyme):
    reponse = client_anonyme.post(
        "/api/vigie/analyser/", {"texte": "bonjour"}, format="json"
    )
    assert reponse.status_code in {400, 401, 403}


def test_session_vigie_est_scoree_par_le_serveur(client):
    reponse = client.post(
        "/api/vigie/sessions/",
        {
            "duree_secondes": 92,
            "signaux": ["demande_otp_pin", "menace_suspension", "code_inconnu"],
        },
        format="json",
    )
    assert reponse.status_code == 201
    data = reponse.json()
    # Unknown codes are dropped; the score comes from the official weights.
    assert data["signaux"] == ["demande_otp_pin", "menace_suspension"]
    assert data["score"] == 70
    assert data["niveau_risque"] == NiveauRisque.ELEVE
    # The session also lands in the history.
    assert client.get("/api/historique/").json()["results"][0]["type_verification"] == "vigie"


# --- Accueil --------------------------------------------------------------

def test_accueil_agrege_tout_en_un_appel(client, categories):
    Alerte.objects.create(titre="Campagne en cours", description="…", epinglee=True)
    Conseil.objects.create(titre="Ne partagez jamais un code", resume="…", ordre=1)
    client.post("/api/messages/analyser/", {"contenu": "code OTP urgent"}, format="json")

    data = client.get("/api/accueil/").json()

    assert data["statistiques"]["verifications"] == 1
    assert data["alertes"][0]["titre"] == "Campagne en cours"
    assert data["conseil_du_jour"]["titre"] == "Ne partagez jamais un code"
    assert len(data["verifications_recentes"]) == 1
    assert data["communaute"]["analyses"] >= 1


def test_accueil_fonctionne_sans_identite(client_anonyme):
    """Avant l'enregistrement de l'appareil, l'accueil doit quand même s'afficher."""
    data = client_anonyme.get("/api/accueil/").json()
    assert data["statistiques"]["verifications"] == 0
    assert data["verifications_recentes"] == []