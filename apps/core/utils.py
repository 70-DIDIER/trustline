"""Small shared helpers: score→level mapping, phone normalisation, link extraction."""
import re
import unicodedata

from django.conf import settings

from apps.core.constants import NiveauRisque

# Togo country code. Local mobile numbers are 8 digits (e.g. 90XXXXXX / 70XXXXXX).
INDICATIF_TOGO = "228"

# Space-like characters that show up in copy-pasted / crafted SMS and would
# otherwise defeat keyword matching (non-breaking space, zero-width, etc.).
_ESPACES_SPECIAUX = "   ​‌‍﻿\t\r\n"


def normaliser_texte(texte: str) -> str:
    """Normalise free text for robust rule matching.

    Real Togolese SMS are often typed WITHOUT accents ("felicitations"),
    in UPPERCASE, with odd spacing or non-breaking/zero-width spaces. We:

    * decompose Unicode (NFKD) and strip combining accents → "é" becomes "e",
      full-width digits/letters become ASCII;
    * lower-case everything;
    * turn every space-like character into a plain space and collapse runs.

    Digits are preserved (money-amount rules rely on them).
    """
    if not texte:
        return ""
    # NFKD splits accented letters into base + combining mark; drop the marks.
    decompose = unicodedata.normalize("NFKD", texte)
    sans_accents = "".join(c for c in decompose if not unicodedata.combining(c))
    # Unify all exotic whitespace, then lower-case and collapse spaces.
    for espace in _ESPACES_SPECIAUX:
        sans_accents = sans_accents.replace(espace, " ")
    return re.sub(r"\s+", " ", sans_accents.lower()).strip()

# Matches http(s) links as well as bare "www." / "domain.tld/..." fragments.
_LIEN_REGEX = re.compile(
    r"((?:https?://|www\.)[^\s,;]+|[a-z0-9-]+(?:\.[a-z0-9-]+)+/[^\s,;]*)",
    re.IGNORECASE,
)


def niveau_from_score(score: int) -> str:
    """Map a 0-100 risk score to a ``NiveauRisque`` value using shared thresholds."""
    score = clamp_score(score)
    if score >= settings.SEUIL_ELEVE:
        return NiveauRisque.ELEVE
    if score >= settings.SEUIL_SUSPECT:
        return NiveauRisque.SUSPECT
    return NiveauRisque.FAIBLE


def clamp_score(score) -> int:
    """Clamp any numeric score into the 0-100 integer range."""
    try:
        value = int(round(float(score)))
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, value))


def normaliser_numero(numero: str) -> str:
    """Normalise a phone number to a canonical ``+228XXXXXXXX`` form.

    Accepts inputs such as ``90112233``, ``0022890112233``, ``+228 90 11 22 33``.
    Non-Togo / already international numbers are returned digit-normalised with a
    leading ``+`` so the value stays stable and comparable.
    """
    if not numero:
        return ""

    # Keep digits only (drop spaces, dashes, parentheses, leading +/00).
    digits = re.sub(r"\D", "", str(numero))

    # Drop an international "00" prefix -> treat the rest as country+number.
    if digits.startswith("00"):
        digits = digits[2:]

    if not digits:
        return ""

    # Local 8-digit Togo number -> prepend the country code.
    if len(digits) == 8:
        digits = INDICATIF_TOGO + digits

    return "+" + digits


def formater_numero(numero: str) -> str:
    """Return a human-friendly form of a normalised number: ``+228 90 11 22 33``.

    Non-Togolese or unusual numbers are returned unchanged — better a raw value
    than a misleading grouping.
    """
    numero = (numero or "").strip()
    if numero.startswith("+" + INDICATIF_TOGO) and len(numero) == 12:
        local = numero[4:]
        paires = " ".join(local[i : i + 2] for i in range(0, 8, 2))
        return f"+{INDICATIF_TOGO} {paires}"
    return numero


_NUMERO_REGEX = re.compile(r"(?:\+?228[\s.-]?)?(?:\d[\s.-]?){8,}")


def extraire_numeros(texte: str) -> list[str]:
    """Extract candidate phone numbers from free text (normalised to +228…)."""
    if not texte:
        return []
    resultats, vus = [], set()
    for brut in _NUMERO_REGEX.findall(texte):
        norm = normaliser_numero(brut)
        # Keep only plausible phone numbers (country code + local part).
        if 10 <= len(norm) <= 16 and norm not in vus:
            vus.add(norm)
            resultats.append(norm)
    return resultats


def extraire_liens(texte: str) -> list[str]:
    """Extract candidate URLs / domains from a free-text message."""
    if not texte:
        return []
    trouves = _LIEN_REGEX.findall(texte)
    # Preserve order while removing duplicates.
    vus, resultat = set(), []
    for lien in trouves:
        lien = lien.rstrip(".")
        if lien.lower() not in vus:
            vus.add(lien.lower())
            resultat.append(lien)
    return resultat
