"""WhatsApp integration via Gupshup (Sandbox).

Route: POST /api/webhook/gupshup/

Bridges Gupshup's inbound webhook format to the existing bot logic
(apps.bot.services.analyser_pour_bot), then sends the verdict back to the user
by calling Gupshup's outbound API.

Design notes (webhook constraints):
* ALWAYS returns HTTP 200 to Gupshup — even on internal errors — so Gupshup does
  not retry in a loop. The actual WhatsApp reply leaves separately via the
  outbound API call.
* CSRF/auth are disabled (authentication_classes = []) because this is an
  external server-to-server webhook, not a browser call.
* The outbound send runs in a background thread ("asynchrone si possible") so
  the 200 ack is returned immediately.
"""
import json
import logging
import threading

import requests
from django.conf import settings
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bot.services import (
    analyser_pour_whatsapp,
    est_salutation,
    message_guide,
)

logger = logging.getLogger("trustline.gupshup")

MESSAGE_TEXTE_UNIQUEMENT = (
    "🛡️ *Trustline* : je n'analyse que du texte pour le moment. "
    "Merci de coller le texte du message suspect. 🙏"
)


# --------------------------------------------------------------------------
# Outbound: send a WhatsApp text back through Gupshup
# --------------------------------------------------------------------------
def envoyer_message_gupshup(destination: str, texte: str) -> bool:
    """POST a text message to the Gupshup outbound API. Never raises."""
    if not destination:
        logger.warning("[gupshup] destination absente, envoi ignoré")
        return False
    if not settings.GUPSHUP_API_KEY:
        logger.warning("[gupshup] GUPSHUP_API_KEY non configurée, envoi ignoré")
        return False

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": settings.GUPSHUP_API_KEY,
    }
    data = {
        "channel": "whatsapp",
        "source": settings.GUPSHUP_SOURCE,
        "destination": destination,
        "message": json.dumps({"type": "text", "text": texte}),
        "src.name": settings.GUPSHUP_APP_NAME,
    }
    try:
        reponse = requests.post(
            settings.GUPSHUP_API_URL,
            headers=headers,
            data=data,
            timeout=settings.GUPSHUP_TIMEOUT,
        )
        logger.info(
            "[gupshup] envoi -> %s : HTTP %s %s",
            destination,
            reponse.status_code,
            reponse.text[:200],
        )
        return reponse.ok
    except requests.RequestException as exc:
        # Timeout / network / API error — logged, never propagated.
        logger.error("[gupshup] échec envoi -> %s : %s", destination, exc)
        return False


def _envoyer_async(destination: str, texte: str) -> None:
    """Fire-and-forget the outbound send so the webhook can ack immediately."""
    threading.Thread(
        target=envoyer_message_gupshup,
        args=(destination, texte),
        daemon=True,
    ).start()


# --------------------------------------------------------------------------
# Inbound payload parsing (defensive)
# --------------------------------------------------------------------------
def _extraire_message(corps: dict):
    """Return (texte, numero, type_message) from a Gupshup inbound payload.

    Any missing key yields ``None`` for that field rather than raising.
    """
    payload = corps.get("payload") or {}
    sender = payload.get("sender") or {}
    numero = sender.get("phone") or payload.get("source")
    type_message = payload.get("type")  # "text", "image", "audio"...
    interne = payload.get("payload") or {}
    texte = interne.get("text") if isinstance(interne, dict) else None
    return texte, numero, type_message


# --------------------------------------------------------------------------
# The webhook view
# --------------------------------------------------------------------------
class GupshupWebhookView(APIView):
    """POST /api/webhook/gupshup/ — WhatsApp inbound webhook (Gupshup)."""

    permission_classes = [AllowAny]
    authentication_classes = []  # external webhook: no session/CSRF, no auth

    @extend_schema(
        tags=["WhatsApp (Gupshup)"],
        summary="Webhook WhatsApp entrant (Gupshup Sandbox)",
        description=(
            "Reçoit les messages WhatsApp transférés par Gupshup, analyse le "
            "texte avec le moteur Trustline et renvoie le verdict à l'utilisateur "
            "via l'API sortante de Gupshup. Répond toujours 200 (accusé de "
            "réception) ; la réponse WhatsApp part de façon asynchrone."
        ),
        request=inline_serializer(
            name="GupshupWebhookRequest",
            fields={
                "app": serializers.CharField(required=False),
                "timestamp": serializers.IntegerField(required=False),
                "type": serializers.CharField(required=False),
                "payload": serializers.DictField(required=False),
            },
        ),
        responses={
            200: inline_serializer(
                name="GupshupWebhookAck",
                fields={"status": serializers.CharField()},
            )
        },
        examples=[
            OpenApiExample(
                "Message WhatsApp texte",
                value={
                    "app": "TrustLine",
                    "timestamp": 1699999999,
                    "type": "message",
                    "payload": {
                        "id": "abc123",
                        "source": "22890429399",
                        "type": "text",
                        "payload": {"text": "Vous avez gagné 500000 FCFA, envoyez votre code OTP"},
                        "sender": {"phone": "22890429399", "name": "Kofi"},
                    },
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        # Always ack 200 at the end — wrap everything defensively.
        try:
            corps = request.data if isinstance(request.data, dict) else {}
            logger.info("[gupshup] payload reçu: type=%s", corps.get("type"))

            # Non-message callbacks (delivery/user events) -> just acknowledge.
            if corps.get("type") != "message":
                logger.info("[gupshup] événement non-message ignoré: %s", corps.get("type"))
                return Response({"status": "ignored"})

            texte, numero, type_message = _extraire_message(corps)
            logger.info(
                "[gupshup] extrait: numero=%s type_msg=%s texte=%r",
                numero, type_message, (texte or "")[:80],
            )

            # No text (image/audio only, or empty) -> polite text-only reply.
            if not texte or not texte.strip():
                logger.info("[gupshup] message sans texte -> réponse 'texte uniquement'")
                _envoyer_async(numero, MESSAGE_TEXTE_UNIQUEMENT)
                return Response({"status": "no_text"})

            # Salutation / demande d'aide -> guide d'utilisation.
            if est_salutation(texte):
                logger.info("[gupshup] salutation détectée -> guide d'utilisation")
                _envoyer_async(numero, message_guide())
                return Response({"status": "guide"})

            # Verdict branché Trustline (branding + CTA), format WhatsApp.
            resultat = analyser_pour_whatsapp(texte, source="whatsapp")
            logger.info(
                "[gupshup] verdict: niveau=%s score=%s",
                resultat["niveau_risque"], resultat["score"],
            )

            _envoyer_async(numero, resultat["reponse"])
            return Response({"status": "processed"})

        except Exception as exc:  # noqa: BLE001 — webhook must never 500
            logger.exception("[gupshup] erreur interne gérée: %s", exc)
            return Response({"status": "error_handled"})
