"""Outil de diagnostic pour l'envoi WhatsApp sortant via Gupshup.

Envoie un message de test EN SYNCHRONE et affiche la réponse brute complète de
l'API Gupshup (statut HTTP + corps), pour identifier immédiatement pourquoi un
message n'arrive pas sur WhatsApp.

Usage :
    python manage.py test_gupshup --to 22890429399
    python manage.py test_gupshup --to 22890429399 --text "Test Trustline"

Le numéro --to doit être un destinataire qui a fait « join <mot-clé> » au numéro
sandbox (obligatoire sur le sandbox Gupshup, fenêtre de 24h).
"""
import json

import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Envoie un message WhatsApp de test via Gupshup et affiche la réponse brute."

    def add_arguments(self, parser):
        parser.add_argument("--to", required=True, help="Numéro destinataire (ex. 22890429399, sans +).")
        parser.add_argument("--text", default="Test Trustline ✅ (diagnostic Gupshup)")

    def handle(self, *args, **options):
        destination = options["to"].strip()
        texte = options["text"]

        cle = settings.GUPSHUP_API_KEY or ""
        cle_masquee = (cle[:4] + "…" + cle[-4:]) if len(cle) > 8 else ("(vide)" if not cle else "(courte)")

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Configuration Gupshup utilisée ==="))
        self.stdout.write(f"  GUPSHUP_API_URL   : {settings.GUPSHUP_API_URL}")
        self.stdout.write(f"  GUPSHUP_API_KEY   : {cle_masquee}")
        self.stdout.write(f"  GUPSHUP_SOURCE    : {settings.GUPSHUP_SOURCE}")
        self.stdout.write(f"  GUPSHUP_APP_NAME  : {settings.GUPSHUP_APP_NAME}")
        self.stdout.write(f"  destination       : {destination}")

        if not cle:
            self.stdout.write(self.style.ERROR(
                "\n❌ GUPSHUP_API_KEY est VIDE. Renseigne-la dans .env puis relance.\n"
                "   (Le webhook renvoie 200 mais n'envoie jamais → WhatsApp muet.)"
            ))
            return

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "apikey": cle,
        }
        data = {
            "channel": "whatsapp",
            "source": settings.GUPSHUP_SOURCE,
            "destination": destination,
            "message": json.dumps({"type": "text", "text": texte}),
            "src.name": settings.GUPSHUP_APP_NAME,
        }

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Envoi en cours… ==="))
        try:
            reponse = requests.post(
                settings.GUPSHUP_API_URL, headers=headers, data=data,
                timeout=settings.GUPSHUP_TIMEOUT,
            )
        except requests.RequestException as exc:
            self.stdout.write(self.style.ERROR(f"❌ Échec réseau / timeout : {exc}"))
            return

        self.stdout.write(f"\n  HTTP {reponse.status_code}")
        self.stdout.write(f"  Réponse brute : {reponse.text}")

        if reponse.ok:
            self.stdout.write(self.style.SUCCESS(
                "\n✅ Gupshup a accepté la requête (2xx). Si WhatsApp reste muet :\n"
                "   → le destinataire n'a PAS fait « join <mot-clé> » (opt-in sandbox), OU\n"
                "   → la fenêtre de 24h est expirée."
            ))
        else:
            self.stdout.write(self.style.ERROR(
                "\n❌ Gupshup a REFUSÉ la requête. Indices selon le message ci-dessus :\n"
                "   • 'Authentication Failed' → GUPSHUP_API_KEY invalide.\n"
                "   • source/app non reconnu  → GUPSHUP_SOURCE / GUPSHUP_APP_NAME incorrects.\n"
                "   • destination non opt-in  → le numéro doit d'abord 'join <mot-clé>'."
            ))
