"""Simplified USSD flow.

USSD gateways typically send the full input string with each step joined by
``*`` (e.g. ``"2*90112233*6"``). We parse that string and reply with a short,
plain-text message. ``type`` mirrors the classic gateway convention:
``CON`` keeps the session open, ``END`` closes it.
"""
from apps.core.constants import CategorieCode, TypeCible
from apps.messages.services import analyser_message  # noqa: F401 (kept for parity)
from apps.numeros.services import verifier_numero
from apps.signalements.services import creer_signalement

# Digit -> category code for the "report a number" branch.
CATEGORIES_USSD = {
    "1": CategorieCode.FRAUDE_FINANCIERE,
    "2": CategorieCode.PHISHING,
    "3": CategorieCode.FAUX_CONCOURS,
    "4": CategorieCode.FAUX_RECRUTEMENT,
    "5": CategorieCode.USURPATION_IDENTITE,
    "6": CategorieCode.DEMANDE_OTP_PIN,
    "7": CategorieCode.AUTRE,
}

_MENU_CATEGORIES = (
    "Catégorie de l'arnaque:\n"
    "1. Fraude financière\n2. Phishing\n3. Faux gain\n"
    "4. Faux recrutement\n5. Usurpation\n6. Demande OTP/PIN\n7. Autre"
)

MENU_PRINCIPAL = (
    "Trustline - Anti-arnaque\n"
    "1. Vérifier un numéro\n"
    "2. Signaler un numéro\n"
    "3. Conseils sécurité"
)

CONSEILS = (
    "Conseils Trustline:\n"
    "- Ne donnez JAMAIS votre code OTP/PIN.\n"
    "- Un service officiel ne demande pas d'argent par SMS.\n"
    "- Méfiez-vous des gains et de l'urgence.\n"
    "- En cas de doute, signalez via Trustline."
)


def _con(message):
    return {"type": "CON", "message": message}


def _fin(message):
    return {"type": "END", "message": message}


def traiter_ussd(texte: str, declarant: str = "ussd-anonyme") -> dict:
    """Handle one USSD step and return {'type': 'CON'|'END', 'message': str}."""
    texte = (texte or "").strip()
    parties = [p for p in texte.split("*") if p != ""] if texte else []

    # Initial dial -> main menu.
    if not parties:
        return _con(MENU_PRINCIPAL)

    choix = parties[0]

    # --- 1) Verify a number ---
    if choix == "1":
        if len(parties) < 2:
            return _con("Entrez le numéro à vérifier:")
        verdict = verifier_numero(parties[1])
        niveau = verdict["niveau_risque"].upper()
        return _fin(
            f"Numéro {verdict['numero']}\n"
            f"Risque: {niveau} ({verdict['score']}/100)\n"
            f"{verdict['recommandation']}"
        )

    # --- 2) Report a number ---
    if choix == "2":
        if len(parties) < 2:
            return _con("Entrez le numéro à signaler:")
        if len(parties) < 3:
            return _con(_MENU_CATEGORIES)
        categorie = CATEGORIES_USSD.get(parties[2])
        if categorie is None:
            return _con("Choix invalide.\n" + _MENU_CATEGORIES)
        _, numero = creer_signalement(
            type_cible=TypeCible.NUMERO,
            cible=parties[1],
            categorie_code=categorie,
            declarant=declarant,
        )
        return _fin(
            "Merci! Signalement enregistré.\n"
            f"Numéro {numero.numero} - niveau actuel: "
            f"{numero.niveau_risque.upper()}."
        )

    # --- 3) Security tips ---
    if choix == "3":
        return _fin(CONSEILS)

    return _fin("Choix invalide. Rappelez le service Trustline.")
