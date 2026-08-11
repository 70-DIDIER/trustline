"""Shared bot logic: turn a free-text message into a conversational verdict.

Used by /api/bot/verifier/ (generic) and the Gupshup WhatsApp webhook (branded).
Formatting lives here so it is defined in one place only.
"""
from django.conf import settings

from apps.core.constants import NiveauRisque
from apps.core.utils import normaliser_texte
from apps.messages.services import analyser_message

# Mots de salutation / demande d'aide qui déclenchent le guide d'utilisation.
_SALUTATIONS = {
    "salut", "bonjour", "bonsoir", "hello", "hi", "hey", "coucou", "yo",
    "allo", "allô", "aide", "help", "menu", "start", "commencer", "demarrer",
    "info", "infos", "guide", "comment", "?",
}

_EMOJI = {
    NiveauRisque.FAIBLE: "✅",
    NiveauRisque.SUSPECT: "⚠️",
    NiveauRisque.ELEVE: "🚨",
}
_ENTETE = {
    NiveauRisque.FAIBLE: "Aucun danger évident",
    NiveauRisque.SUSPECT: "Message suspect",
    NiveauRisque.ELEVE: "Attention, arnaque probable",
}


def analyser_pour_bot(texte: str, source: str = "bot") -> dict:
    """Analyse ``texte`` and return a conversational reply.

    Returns ``{"reponse": str, "niveau_risque": str, "score": int}``.
    ``source`` tags the LogAnalyse row (e.g. "bot", "whatsapp").
    """
    verdict = analyser_message(texte, source=source)
    niveau = verdict["niveau_risque"]

    lignes = [f"{_EMOJI[niveau]} {_ENTETE[niveau]} ({verdict['score']}/100)"]
    if verdict["indices"]:
        lignes.append("")
        # Verdicts carry structured indices; a chat reply only needs the headline.
        lignes.extend(f"• {indice['libelle']}" for indice in verdict["indices"])
    lignes.append("")
    lignes.append(verdict["recommandation"])

    return {
        "reponse": "\n".join(lignes),
        "niveau_risque": niveau,
        "score": verdict["score"],
    }


def est_salutation(texte: str) -> bool:
    """Vrai si le message est UNIQUEMENT une salutation / demande d'aide.

    On exige un message court (≤ 3 mots) composé seulement de mots de
    salutation, pour ne PAS confondre avec une arnaque qui commence par
    « Bonjour … » suivi d'un long texte.
    """
    norm = normaliser_texte(texte)
    mots = [m.strip("!.,:;") for m in norm.split() if m.strip("!.,:;")]
    if not mots or len(mots) > 3:
        return False
    return all(mot in _SALUTATIONS for mot in mots)


def message_guide() -> str:
    """Message de bienvenue / guide d'utilisation du bot, brandé Trustline."""
    nom = settings.TRUSTLINE_NOM
    return (
        f"👋 Bienvenue sur *{nom}* — votre bouclier contre les arnaques numériques\n\n"
        "Envoyez-moi un SMS, un message ou un lien suspect, et je vous dirai en "
        "quelques secondes s'il s'agit d'une arnaque, avec le niveau de risque et "
        "les raisons du verdict.\n\n"
        f"Pour aller plus loin, {nom} est aussi disponible sur :\n"
        "📱 *Application mobile* — vérification de numéros, historique, alertes "
        "d'appels suspects et Mode Vigie\n"
        "🧩 *Extension Chrome* — protection automatique pendant votre navigation\n"
        "🌐 *Site web* — recherche et signalement en ligne\n"
        "📟 *Service USSD* — accessible sans smartphone ni connexion Internet\n\n"
        "Un numéro ou un site déjà signalé par la communauté ? On vous prévient "
        "immédiatement, sur tous les canaux.\n\n"
        "Tapez votre message ou collez un lien pour commencer. 👇"
    )


def _cta_whatsapp(niveau: str) -> str:
    """Call-to-action branded Trustline, adapté au niveau de risque (bref)."""
    nom = settings.TRUSTLINE_NOM
    site = settings.TRUSTLINE_SITE
    if niveau == NiveauRisque.FAIBLE:
        return f"En cas de doute, vérifiez sur *{nom}* ({site})."
    # suspect / eleve : inciter à vérifier + signaler aux autorités
    return (
        f"🔎 Vérifiez ce numéro sur *{nom}* (application mobile ou {site}).\n"
        f"📢 Signalez-le aussi au CERT-TG (cert.tg) ou à l'ANCY."
    )


# Indices internes/techniques à ne pas montrer à l'utilisateur final.
#
# On filtre sur le CODE et non sur le libellé : le libellé est du texte
# d'affichage, susceptible d'être reformulé. Il l'a d'ailleurs été — le filtre
# visait « Score renforcé… » quand le moteur émet « Score confirmé… » — et
# l'indice technique repassait donc en clair dès l'activation du modèle.
_INDICES_TECHNIQUES = {"modele_ml"}


def analyser_pour_whatsapp(texte: str, source: str = "whatsapp") -> dict:
    """Version WhatsApp du verdict : brandée *Trustline*, brève, avec CTA.

    Retourne ``{"reponse", "niveau_risque", "score"}`` comme analyser_pour_bot.
    """
    verdict = analyser_message(texte, source=source)
    niveau = verdict["niveau_risque"]
    nom = settings.TRUSTLINE_NOM
    # Verdicts carry structured indices; only the headline is shown here.
    indices = [
        indice["libelle"]
        for indice in verdict["indices"]
        if indice["code"] not in _INDICES_TECHNIQUES
    ]

    lignes = [f"{_EMOJI[niveau]} *{nom}* — {_ENTETE[niveau]} ({verdict['score']}/100)"]
    # Les puces (raisons) n'ont de sens que si le message est à risque.
    if niveau != NiveauRisque.FAIBLE and indices:
        lignes.append("")
        lignes.extend(f"• {indice}" for indice in indices[:3])  # bref : 3 max
    lignes.append("")
    lignes.append(verdict["recommandation"])
    lignes.append("")
    lignes.append(_cta_whatsapp(niveau))

    return {
        "reponse": "\n".join(lignes),
        "niveau_risque": niveau,
        "score": verdict["score"],
    }
