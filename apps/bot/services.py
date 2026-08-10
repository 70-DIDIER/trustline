"""Shared bot logic: turn a free-text message into a conversational verdict.

Used by BOTH /api/bot/verifier/ and the Gupshup WhatsApp webhook, so the
formatting lives in one place only.
"""
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
