"""Message analysis: rule engine + reputation of embedded numbers/links."""
from apps.core.constants import TypeCible
from apps.core.services import enregistrer_log
from apps.core.utils import extraire_liens, extraire_numeros
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


def analyser_message(contenu: str, source: str = "api", persister: bool = True) -> dict:
    """Analyse a free-text message and return a normalised verdict dict.

    Combines the rule engine with the community reputation of any phone number
    embedded in the text.
    """
    liens = extraire_liens(contenu)
    numeros = extraire_numeros(contenu)
    score_reputation = _reputation_embarquee(numeros)

    resultat = moteur_par_defaut.analyser(contenu, score_reputation=score_reputation)

    if persister:
        Message.objects.create(
            contenu=contenu,
            liens_extraits=liens,
            numeros_extraits=numeros,
            score_risque=resultat.score,
            verdict=resultat.niveau_risque,
            indices_detectes=resultat.indices,
        )
    enregistrer_log(TypeCible.MESSAGE, contenu, resultat, source=source)

    return {
        "score": resultat.score,
        "niveau_risque": resultat.niveau_risque,
        "indices": resultat.indices,
        "recommandation": resultat.recommandation,
        "categories": resultat.categories,
        "liens_extraits": liens,
        "numeros_extraits": numeros,
    }
