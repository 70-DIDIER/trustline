"""Business logic for creating a report and refreshing reputation."""
from django.db import transaction

from apps.core.constants import TypeCible
from apps.core.models import CategorieArnaque
from apps.core.utils import normaliser_numero
from apps.numeros.models import Numero
from apps.numeros.services import invalider_cache_numero
from apps.signalements.models import Signalement
from apps.signalements.reputation import mettre_a_jour_numero


@transaction.atomic
def creer_signalement(
    *,
    type_cible,
    cible,
    categorie_code,
    declarant,
    commentaire="",
    montant_perdu=None,
    appareil=None,
):
    """Create a Signalement and update the target's reputation if applicable.

    Returns a tuple ``(signalement, numero_or_None)``.
    """
    categorie = CategorieArnaque.objects.get(code=categorie_code)

    numero_obj = None
    cible_stockee = cible
    if type_cible == TypeCible.NUMERO:
        cible_stockee = normaliser_numero(cible)
        numero_obj, _ = Numero.objects.get_or_create(numero=cible_stockee)

    signalement = Signalement.objects.create(
        type_cible=type_cible,
        cible=cible_stockee,
        numero_cible=numero_obj,
        categorie=categorie,
        declarant=declarant,
        appareil=appareil,
        commentaire=commentaire or "",
        montant_perdu=montant_perdu,
    )
    # The reference embeds the primary key, so it can only be built post-insert.
    signalement.reference = signalement.generer_reference()
    signalement.save(update_fields=["reference"])

    if numero_obj is not None:
        mettre_a_jour_numero(numero_obj)
        invalider_cache_numero(numero_obj.numero)

    return signalement, numero_obj


@transaction.atomic
def moderer_signalement(signalement, statut):
    """Apply a moderation status to a report and refresh the target reputation.

    Shared by the REST admin API and the Django admin. Returns the report.
    """
    signalement.statut = statut
    signalement.save(update_fields=["statut"])

    numero_obj = signalement.numero_cible
    if numero_obj is not None:
        mettre_a_jour_numero(numero_obj)
        invalider_cache_numero(numero_obj.numero)

    return signalement
