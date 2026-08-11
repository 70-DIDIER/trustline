"""Message analysis: rule engine + reputation of embedded numbers/links."""
from apps.core.constants import TypeCible
from apps.core.services import enregistrer_log
from apps.core.utils import extraire_liens, extraire_numeros, normaliser_numero
from apps.messages.models import Message
from apps.numeros.models import Numero
from apps.scoring.engine import moteur_par_defaut


def _reputation_embarquee(numeros: list[str]) -> int:
    """Highest reputation score among phone numbers found in the message."""
    if not numeros:
        return 0
    scores = Numero.objects.filter(numero__in=numeros).values_list(
        "score_risque", flat=True
    )
    return max(scores, default=0)


def analyser_message(
    contenu: str,
    source: str = "api",
    persister: bool = True,
    expediteur: str = "",
) -> dict:
    """Analyse a free-text message and return a normalised verdict dict.

    Combines the rule engine with the community reputation of any phone number
    embedded in the text — and of the sender, when the app knows it.
    """
    liens = extraire_liens(contenu)
    numeros = extraire_numeros(contenu)

    # The sender is a reputation signal too, even when absent from the body.
    numeros_reputation = list(numeros)
    if expediteur:
        expediteur_norm = normaliser_numero(expediteur)
        if expediteur_norm and expediteur_norm not in numeros_reputation:
            numeros_reputation.append(expediteur_norm)

    score_reputation = _reputation_embarquee(numeros_reputation)

    resultat = moteur_par_defaut.analyser(contenu, score_reputation=score_reputation)

    if persister:
        Message.objects.create(
            contenu=contenu,
            liens_extraits=liens,
            numeros_extraits=numeros,
            score_risque=resultat.score,
            verdict=resultat.niveau_risque,
            indices_detectes=[i.as_dict() for i in resultat.indices],
        )
    enregistrer_log(TypeCible.MESSAGE, contenu, resultat, source=source)

    verdict = resultat.as_dict()
    verdict["liens_extraits"] = liens
    verdict["numeros_extraits"] = numeros
    return verdict