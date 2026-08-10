"""Tests for the Gupshup WhatsApp webhook (POST /api/webhook/gupshup/)."""
from unittest import mock

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

URL = "/api/webhook/gupshup/"


def _payload_texte(texte, phone="22890429399"):
    return {
        "app": "TrustLine",
        "timestamp": 1699999999,
        "type": "message",
        "payload": {
            "id": "abc123",
            "source": phone,
            "type": "text",
            "payload": {"text": texte},
            "sender": {"phone": phone, "name": "Kofi"},
        },
    }


@pytest.fixture
def client():
    return APIClient()


@mock.patch("apps.bot.webhooks._envoyer_async")
def test_message_texte_arnaque_declenche_envoi(mock_envoi, client):
    payload = _payload_texte(
        "Felicitations! Vous avez gagne 500000 FCFA, envoyez votre code OTP"
    )
    reponse = client.post(URL, payload, format="json")

    assert reponse.status_code == 200
    assert reponse.json()["status"] == "processed"
    # Outbound send called with the sender's number and a non-empty verdict.
    mock_envoi.assert_called_once()
    destination, texte_reponse = mock_envoi.call_args.args
    assert destination == "22890429399"
    assert "100" in texte_reponse or "eleve" in texte_reponse.lower() or "🚨" in texte_reponse


@mock.patch("apps.bot.webhooks._envoyer_async")
def test_message_sans_texte_repond_texte_uniquement(mock_envoi, client):
    from apps.bot.webhooks import MESSAGE_TEXTE_UNIQUEMENT

    payload = {
        "type": "message",
        "payload": {
            "source": "22890429399",
            "type": "image",
            "payload": {"url": "http://example.com/img.jpg"},
            "sender": {"phone": "22890429399"},
        },
    }
    reponse = client.post(URL, payload, format="json")

    assert reponse.status_code == 200
    assert reponse.json()["status"] == "no_text"
    mock_envoi.assert_called_once_with("22890429399", MESSAGE_TEXTE_UNIQUEMENT)


@mock.patch("apps.bot.webhooks._envoyer_async")
def test_evenement_non_message_est_ignore(mock_envoi, client):
    reponse = client.post(URL, {"type": "message-event"}, format="json")
    assert reponse.status_code == 200
    assert reponse.json()["status"] == "ignored"
    mock_envoi.assert_not_called()


@mock.patch("apps.bot.webhooks._envoyer_async")
def test_payload_vide_renvoie_200_sans_planter(mock_envoi, client):
    reponse = client.post(URL, {}, format="json")
    assert reponse.status_code == 200
    mock_envoi.assert_not_called()


def test_envoyer_message_gupshup_sans_cle_ne_plante_pas(settings):
    from apps.bot.webhooks import envoyer_message_gupshup

    settings.GUPSHUP_API_KEY = ""
    assert envoyer_message_gupshup("22890429399", "test") is False


def test_envoyer_message_gupshup_construit_la_requete(settings):
    from apps.bot import webhooks

    settings.GUPSHUP_API_KEY = "cle-test"
    with mock.patch.object(webhooks.requests, "post") as mock_post:
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 202
        mock_post.return_value.text = "ok"
        resultat = webhooks.envoyer_message_gupshup("22890429399", "Bonjour")

    assert resultat is True
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["apikey"] == "cle-test"
    assert kwargs["data"]["destination"] == "22890429399"
    assert kwargs["data"]["channel"] == "whatsapp"
    assert '"text": "Bonjour"' in kwargs["data"]["message"]
