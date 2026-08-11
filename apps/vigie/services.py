"""Mode Vigie business logic.

Two responsibilities:

* **serve the signal catalogue** — the rules (label, weight, regex patterns) the
  phone applies to the *local* speech transcription. Shipping the patterns
  instead of the audio is what makes the privacy promise true: nothing spoken
  ever reaches the server, yet the detection stays centrally updatable;
* **score a finished session** from the list of rule codes that fired.
"""
import hashlib
import json
import re

from apps.core.utils import clamp_score, niveau_from_score, normaliser_texte
from apps.scoring.engine import moteur_par_defaut
from apps.scoring.rules import REGLES

# Extra spoken-only signals: these never appear in a written SMS but are the
# backbone of a voice scam, so Mode Vigie looks for them on top of the shared
# rule set.
SIGNAUX_ORAUX = [
    {
        "code": "identite_pretendue",
        "libelle": "Identité prétendue non vérifiable",
        "poids": 20,
        "detail": (
            "L'interlocuteur affirme appeler d'un service officiel. Un vrai "
            "conseiller accepte que vous raccrochiez pour le rappeler."
        ),
        "categorie": "usurpation_identite",
        "motifs": [
            r"je suis (?:un )?agent",
            r"service (?:client|technique|financier)",
            r"j'?appelle de (?:la )?(?:part de )?",
            r"votre (?:banque|operateur|conseiller)",
        ],
    },
    {
        "code": "menace_suspension",
        "libelle": "Menace de suspension du compte",
        "poids": 25,
        "detail": (
            "La menace de blocage sert à provoquer la panique. Aucun opérateur "
            "ne suspend un compte pendant un appel téléphonique."
        ),
        "categorie": "phishing",
        "motifs": [
            r"compte (?:sera |va etre |est )?(?:bloque|suspendu|desactive|ferme)",
            r"suspension",
            r"perdre (?:votre|ton) (?:compte|numero|argent)",
        ],
    },
    {
        "code": "insistance_secret",
        "libelle": "Demande de ne prévenir personne",
        "poids": 22,
        "detail": (
            "Vous isoler de vos proches est une technique de manipulation : une "
            "démarche légitime supporte très bien d'être vérifiée par un tiers."
        ),
        "categorie": "autre",
        "motifs": [
            r"ne dites? (?:rien )?a personne",
            r"restez? en ligne",
            r"ne raccrochez? pas",
            r"entre nous",
        ],
    },
]


def catalogue_signaux() -> list[dict]:
    """Return every signal Mode Vigie looks for, patterns included."""
    signaux = [
        {
            "code": regle.nom,
            "libelle": regle.libelle,
            "poids": regle.poids,
            "detail": regle.detail,
            "categorie": str(regle.categorie),
            "motifs": list(regle.motifs),
        }
        for regle in REGLES
    ]
    signaux.extend(SIGNAUX_ORAUX)
    return signaux


def version_catalogue() -> str:
    """Stable fingerprint of the catalogue, so the app refreshes only on change."""
    charge = json.dumps(catalogue_signaux(), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(charge.encode("utf-8")).hexdigest()[:12]


def _poids_par_code() -> dict:
    return {signal["code"]: signal["poids"] for signal in catalogue_signaux()}


def evaluer_session(codes_signaux) -> dict:
    """Score a finished listening session from the rule codes that fired."""
    poids = _poids_par_code()
    codes = [c for c in dict.fromkeys(codes_signaux or []) if c in poids]
    score = clamp_score(sum(poids[c] for c in codes))
    niveau = niveau_from_score(score)
    return {"codes": codes, "score": score, "niveau_risque": niveau}


# --- Analyse assistée par le modèle -----------------------------------------
#
# Les motifs oraux ne font pas partie de REGLES : le moteur de scoring ne les
# connaît donc pas. On les applique ici pour que le verdict serveur couvre au
# moins tout ce que le téléphone sait détecter seul.
_MOTIFS_ORAUX_COMPILES: list[tuple[dict, list[re.Pattern]]] = []


def _motifs_oraux() -> list[tuple[dict, list[re.Pattern]]]:
    global _MOTIFS_ORAUX_COMPILES
    if not _MOTIFS_ORAUX_COMPILES:
        _MOTIFS_ORAUX_COMPILES = [
            (signal, [re.compile(m, re.IGNORECASE) for m in signal["motifs"]])
            for signal in SIGNAUX_ORAUX
        ]
    return _MOTIFS_ORAUX_COMPILES


def analyser_transcription(texte: str) -> dict:
    """Analyse a Mode Vigie transcript with the full engine (rules + model).

    Deliberately calls the engine directly instead of ``analyser_message`` :
    that helper writes the analysed text to ``Message`` **and** to
    ``LogAnalyse.cible``. A call transcript must never be stored, so it is
    scored in memory and dropped — only the score and the signal codes are
    ever persisted, and only by ``POST /api/vigie/sessions/``.
    """
    texte = (texte or "").strip()
    if not texte:
        return {
            "score": 0,
            "niveau_risque": niveau_from_score(0),
            "signaux": [],
            "indices": [],
            "analyse_ml": moteur_par_defaut.ml_model is not None,
        }

    resultat = moteur_par_defaut.analyser(texte)
    indices = [i.as_dict() for i in resultat.indices]
    codes = {i["code"] for i in indices}
    score = resultat.score

    texte_norm = normaliser_texte(texte)
    for signal, motifs in _motifs_oraux():
        if signal["code"] in codes:
            continue
        if any(motif.search(texte_norm) for motif in motifs):
            codes.add(signal["code"])
            score += signal["poids"]
            indices.append(
                {
                    "code": signal["code"],
                    "libelle": signal["libelle"],
                    "poids": signal["poids"],
                    "detail": signal["detail"],
                    "categorie": signal["categorie"],
                }
            )

    score = clamp_score(score)
    return {
        "score": score,
        "niveau_risque": niveau_from_score(score),
        "signaux": [i["code"] for i in indices],
        "indices": indices,
        "analyse_ml": moteur_par_defaut.ml_model is not None,
    }