"""Shared bot logic: turn a free-text message into a conversational verdict.

Used by /api/bot/verifier/ (generic) and the Gupshup WhatsApp webhook (branded).
Formatting lives here so it is defined in one place only.
"""
from django.conf import settings

from apps.core.constants import NiveauRisque
from apps.messages.services import analyser_message

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
        lignes.extend(f"• {indice}" for indice in verdict["indices"])
    lignes.append("")
    lignes.append(verdict["recommandation"])

    return {
        "reponse": "\n".join(lignes),
        "niveau_risque": niveau,
        "score": verdict["score"],
    }


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
_INDICES_TECHNIQUES = {"Score renforcé par le modèle d'apprentissage."}


def analyser_pour_whatsapp(texte: str, source: str = "whatsapp") -> dict:
    """Version WhatsApp du verdict : brandée *Trustline*, brève, avec CTA.

    Retourne ``{"reponse", "niveau_risque", "score"}`` comme analyser_pour_bot.
    """
    verdict = analyser_message(texte, source=source)
    niveau = verdict["niveau_risque"]
    nom = settings.TRUSTLINE_NOM
    indices = [i for i in verdict["indices"] if i not in _INDICES_TECHNIQUES]

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
