"""Rule set for the v1 detection engine.

Each rule is a small, explainable unit: a name, a set of keyword/regex signals,
a weight (points added when the rule matches) and a human-readable ``indice``
shown to the user. Keeping rules as data (not code) makes them easy to justify
to the jury and easy to tune during the hackathon.

IMPORTANT: rules are matched against text already passed through
``apps.core.utils.normaliser_texte`` (accents stripped, lower-cased, spacing
collapsed). Patterns are therefore written in plain ASCII lowercase — no need
for accented variants such as ``[ée]``.
"""
import re
from dataclasses import dataclass, field

from apps.core.constants import CategorieCode


@dataclass
class Regle:
    """A single detection rule."""

    nom: str
    poids: int
    libelle: str  # short headline surfaced to the user (an "indice")
    motifs: list[str]  # regex patterns (matched against normalised text)
    categorie: str = CategorieCode.AUTRE
    # Longer "why does this matter" sentence shown under the headline in the
    # mobile app. Keeping it next to the rule means no verdict is a black box.
    detail: str = ""
    _compiles: list = field(default_factory=list, repr=False)

    def __post_init__(self):
        # re.IGNORECASE kept as a safety net even though the text is lower-cased.
        self._compiles = [re.compile(m, re.IGNORECASE) for m in self.motifs]

    def correspond(self, texte: str) -> bool:
        return any(rx.search(texte) for rx in self._compiles)


# --- Well-known Togolese services (used for impersonation detection) ---
SERVICES_OFFICIELS = [
    r"mixx",
    r"flooz",
    r"moov",
    r"\byas\b",
    r"togocom",
    r"togocel",
    r"tmoney",
    r"mobile\s*money",
    r"ecobank",
    r"orabank",
    r"\butb\b",
    r"\bboa\b",
    r"coris",
    r"\bnsia\b",
    r"banque",
    r"service\s*client",
    r"support\s*technique",
]

# --- Money / transfer signals ---
MOTIFS_ARGENT = [
    r"\d[\d\s.]*\s*(?:f\s*cfa|fcfa|francs?|xof)",
    r"transf[e]?r",
    r"envoy(?:er|ez|e)\s+(?:le\s+)?(?:montant|argent|\d)",
    r"faites?\s+un\s+d[e]?p[o]?t",
    r"recharge[rz]?",
    r"depos(?:er|ez|e)\s+\d",
    r"payer?\s+\d",
    r"virement",
]


REGLES: list[Regle] = [
    Regle(
        nom="demande_otp_pin",
        poids=45,
        libelle="Demande d'un code OTP / PIN / code secret (jamais légitime).",
        categorie=CategorieCode.DEMANDE_OTP_PIN,
        detail=(
            "Un code reçu par SMS sert à valider VOTRE opération, jamais celle "
            "d'un tiers. Aucun opérateur, aucune banque, aucun agent ne vous le "
            "demandera : la demande elle-même est la preuve de l'arnaque."
        ),
        motifs=[
            r"\botp\b",
            r"code\s+(?:de\s+)?(?:verification|confirmation|securite|secret|retrait|transaction)",
            r"\bcode\s+pin\b",
            r"\bpin\b\s*[:=]?\s*\d",
            r"(?:votre|le|ton)\s+code",
            r"communiqu(?:er|ez)\s+(?:le\s+)?code",
            r"donn(?:er|ez)\s+(?:moi\s+)?(?:votre\s+)?code",
            r"envoy(?:er|ez|e)\s+(?:le\s+)?code",
            r"confirm(?:er|ez)\s+(?:votre\s+)?(?:code|compte|identite)",
            r"verifi(?:er|ez)\s+(?:votre\s+)?(?:compte|identite)",
            r"mot\s+de\s+passe",
            r"identifiants?\s+(?:de\s+connexion|bancaires?)",
        ],
    ),
    Regle(
        nom="urgence_artificielle",
        poids=20,
        libelle="Pression / urgence artificielle pour vous faire agir vite.",
        categorie=CategorieCode.PHISHING,
        detail=(
            "La pression temporelle est là pour vous empêcher de réfléchir ou de "
            "vérifier auprès du vrai service. Un délai qui expire dans l'heure "
            "est un signal de manipulation, pas d'efficacité."
        ),
        motifs=[
            r"immediatement",
            r"dans\s+les?\s+\d+\s*(?:h|heures?|minutes?|min)",
            r"sous\s+\d+\s*(?:h|heures?|minutes?)",
            r"compte\s+(?:sera\s+|va\s+etre\s+|a\s+ete\s+)?(?:bloque|suspendu|desactive|ferme)",
            r"\burgent\b",
            r"dernier\s+(?:avertissement|delai|rappel)",
            r"sans\s+(?:plus\s+)?(?:tarder|delai)",
            r"depech(?:er|ez)\s*(?:vous)?",
            r"action\s+(?:requise|immediate)",
            r"expire",
        ],
    ),
    Regle(
        nom="promesse_gain",
        poids=30,
        libelle="Promesse de gain / faux concours (« vous avez gagné »).",
        categorie=CategorieCode.FAUX_CONCOURS,
        detail=(
            "On ne gagne pas à une loterie à laquelle on n'a jamais joué. Aucun "
            "gain légitime n'exige un paiement, un code ou des frais de dossier "
            "pour être débloqué."
        ),
        motifs=[
            r"vous\s+avez\s+gagne",
            r"felicitations?",
            r"gagnant",
            r"tirage\s+au\s+sort",
            r"loterie",
            r"\bcadeau\b",
            r"prix\s+de\s+\d",
            r"heureux\s+(?:elu|gagnant)",
            r"vous\s+(?:etes|avez\s+ete)\s+selectionne",
            r"recompense",
            r"bon\s+d'?\s*achat",
            r"cheque\s+de\s+\d",
        ],
    ),
    Regle(
        nom="demande_transfert",
        poids=25,
        libelle="Demande d'envoi ou de transfert d'argent.",
        categorie=CategorieCode.FRAUDE_FINANCIERE,
        detail=(
            "Sollicitation directe d'un mouvement d'argent. Le scénario le plus "
            "répandu au Togo est le « dépôt reçu par erreur » : le dépôt n'a "
            "jamais eu lieu, vous enverriez votre propre argent."
        ),
        motifs=MOTIFS_ARGENT,
    ),
    Regle(
        nom="usurpation_service",
        poids=20,
        libelle="Se fait passer pour un service officiel (banque / opérateur).",
        categorie=CategorieCode.USURPATION_IDENTITE,
        detail=(
            "Le message se réclame d'une institution sans aucune preuve "
            "d'identité. Le nom affiché d'un expéditeur SMS se falsifie : "
            "raccrochez et rappelez par un numéro que vous avez cherché vous-même."
        ),
        # Weight only applies when combined with an action — handled in engine.
        motifs=SERVICES_OFFICIELS,
    ),
    Regle(
        nom="lien_suspect",
        poids=25,
        libelle="Présence d'un lien raccourci ou suspect.",
        categorie=CategorieCode.PHISHING,
        detail=(
            "Le lien mène hors des canaux officiels et sa destination réelle est "
            "masquée. Ces pages imitent l'apparence d'un service légitime pour "
            "collecter vos identifiants."
        ),
        motifs=[
            r"bit\.ly",
            r"tinyurl",
            r"cutt\.ly",
            r"is\.gd",
            r"t\.co/",
            r"goo\.gl",
            r"rb\.gy",
            r"https?://\d{1,3}(?:\.\d{1,3}){3}",  # raw IP address
            r"(?:https?://|www\.)[^\s]*\.(?:xyz|top|tk|ml|ga|cf|gq|club|online)\b",
        ],
    ),
]


# --- Multilingue : fusion du lexique éwé dans les règles ci-dessus ---------
# Les motifs éwé (apps/scoring/lexique_ewe.py) sont ajoutés aux motifs français
# de chaque règle du même nom. Ajouter une langue = ajouter un lexique ici,
# sans toucher au moteur ni aux endpoints.
from apps.scoring.lexique_ewe import MOTIFS_EWE  # noqa: E402


def _fusionner_lexique(regles: list[Regle], motifs_par_regle: dict) -> None:
    """Append extra language patterns to matching rules (in place)."""
    index = {regle.nom: regle for regle in regles}
    for nom, motifs in motifs_par_regle.items():
        regle = index.get(nom)
        if regle is None:
            continue
        regle.motifs = regle.motifs + list(motifs)
        regle._compiles += [re.compile(m, re.IGNORECASE) for m in motifs]


_fusionner_lexique(REGLES, MOTIFS_EWE)
