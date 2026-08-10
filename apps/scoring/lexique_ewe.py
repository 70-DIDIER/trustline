"""Lexique ÉWÉ pour le moteur de détection (arnaques rédigées en éwé/mina).

⚠️ BASE PROVISOIRE — À VALIDER PAR UN LOCUTEUR NATIF ⚠️
--------------------------------------------------------
Ce fichier étend le moteur de règles (`rules.py`) avec des motifs en éwé, pour
détecter les SMS d'arnaque qui ne sont pas rédigés en français. Il réutilise
EXACTEMENT les mêmes catégories : il suffit d'ajouter des motifs par règle.

Comment ça marche
-----------------
* Le texte analysé est déjà normalisé par ``apps.core.utils.normaliser_texte``
  (minuscules, accents/tons supprimés). Les lettres spéciales de l'éwé
  (ɔ, ɖ, ƒ, ŋ, ʋ, ɣ) ne sont PAS des accents : elles SURVIVENT à la
  normalisation. Comme beaucoup d'utilisateurs ne peuvent pas les taper au
  clavier, chaque motif tolère la variante ASCII via des classes, ex. :
      [ɔo]  (ɔ ou o)   |   (?:ɖ|d|dz)   |   (?:ƒ|f)   |   (?:ŋ|ng?)

Comment enrichir / corriger
---------------------------
Ajoute / modifie simplement les chaînes dans le dictionnaire ci-dessous, en
gardant la clé = nom de la règle. Rien d'autre à toucher : `rules.py` fusionne
automatiquement ces motifs avec les motifs français.

Chaque ligne = un motif regex + un commentaire "# sens (À VALIDER)".
"""

# clé = nom de règle (voir rules.py) ; valeur = liste de motifs regex éwé.
MOTIFS_EWE = {
    "demande_otp_pin": [
        r"na[ ]+.*code",          # "na ... code" = donne le code (À VALIDER)
        r"code[ ]+la\b",          # "code la" = le code (À VALIDER)
        r"code[ ]+w[ɔo]",         # "code wɔ" (À VALIDER)
        r"na[ ]+code",            # "na code" = donne le code (À VALIDER)
    ],
    "urgence_artificielle": [
        r"\bkaba\b",              # kaba = vite / rapidement (À VALIDER)
        r"fifia",                 # fifia = maintenant / tout de suite (À VALIDER)
        r"enumake",               # enumake = immédiatement (À VALIDER)
        r"kpuie",                 # kpuie = bientôt / vite (À VALIDER)
    ],
    "promesse_gain": [
        r"nunana",                # nunana = cadeau / don (À VALIDER)
        r"[eɛ]?[ɖd]u[ ]+dz[ɔo]", # "ɖu dzɔ" = gagner (À VALIDER)
        r"dz[ɔo]gbeny[uʋ]i",      # dzɔgbenyui = chance / bonheur (À VALIDER)
    ],
    "demande_transfert": [
        r"[ɖd]o[ ]+ga",           # "ɖo ga" = envoyer de l'argent (À VALIDER)
        r"[ɖd]ra[ ]+ga",          # "dzra ga" (À VALIDER)
        r"\bga\b(?=.*(?:\d|fcfa))",  # "ga" (argent) proche d'un montant (À VALIDER)
        r"fe[ ]+ga",              # "fe ga" = payer de l'argent (À VALIDER)
    ],
    "usurpation_service": [
        r"\bbanki\b",             # banki = banque (À VALIDER)
        r"dɔwɔƒe",                # dɔwɔƒe = service / bureau (À VALIDER)
    ],
    # lien_suspect : les URLs sont indépendantes de la langue -> rien à ajouter.
}
