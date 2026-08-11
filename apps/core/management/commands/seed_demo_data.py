"""Seed realistic Togolese demo data so the jury demo has content immediately.

Run with:  python manage.py seed_demo_data

Idempotent: categories and whitelist use get_or_create; demo numbers, reports
and messages are wiped and recreated on each run so the demo is reproducible.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.constants import (
    CATEGORIES_PAR_DEFAUT,
    CategorieCode,
    NiveauRisque,
    StatutSignalement,
    TypeCible,
)
from apps.core.models import CategorieArnaque, ListeBlanche, LogAnalyse
from apps.messages.services import analyser_message
from apps.numeros.models import Numero
from apps.numeros.services import invalider_cache_numero
from apps.signalements.models import Signalement
from apps.signalements.reputation import mettre_a_jour_numero
from apps.veille.models import Alerte, Conseil

# Official numbers (illustrative — to be replaced with verified sources).
LISTE_BLANCHE = [
    ("+22870000001", "Yas Togo (Moov Africa)", "Service client officiel"),
    ("+22890000002", "Mixx by Yas (Mobile Money)", "Service client officiel"),
    ("+22822215000", "Ecobank Togo", "Banque - service client"),
    ("+22870141414", "Togocom", "Service client officiel"),
]

# Scam numbers, each with a few reports (distinct reporters + categories + dates).
# Format: (numero, [(categorie, declarant, age_en_jours, statut), ...])
NUMEROS_ARNAQUE = [
    (
        "+22890112233",
        [
            (CategorieCode.DEMANDE_OTP_PIN, "decl-A1", 1, StatutSignalement.VALIDE),
            (CategorieCode.FRAUDE_FINANCIERE, "decl-B2", 2, StatutSignalement.VALIDE),
            (CategorieCode.USURPATION_IDENTITE, "decl-C3", 3, StatutSignalement.VALIDE),
            (CategorieCode.FRAUDE_FINANCIERE, "decl-D4", 5, StatutSignalement.EN_ATTENTE),
        ],
    ),
    (
        "+22879887766",
        [
            (CategorieCode.FAUX_CONCOURS, "decl-E5", 2, StatutSignalement.VALIDE),
            (CategorieCode.FAUX_CONCOURS, "decl-F6", 4, StatutSignalement.VALIDE),
            (CategorieCode.FRAUDE_FINANCIERE, "decl-G7", 6, StatutSignalement.EN_ATTENTE),
        ],
    ),
    (
        "+22898765432",
        [
            # Single reporter -> must stay "suspect", never "élevé".
            (CategorieCode.FAUX_RECRUTEMENT, "decl-H8", 1, StatutSignalement.EN_ATTENTE),
        ],
    ),
]

# Realistic scam SMS (Togolese Mobile Money context).
MESSAGES_DEMO = [
    "Felicitations! Votre numero a gagne 2.000.000 FCFA a la loterie MIXX. "
    "Pour retirer, envoyez votre code PIN au 90112233 immediatement.",
    "MIXX: Votre compte sera bloque dans 24h. Confirmez votre code OTP en repondant "
    "a ce message pour eviter la suspension.",
    "Bonjour, je suis agent Flooz. Une erreur de depot a ete faite sur votre compte, "
    "veuillez renvoyer 15000 FCFA au 79887766 svp.",
    "Salut, on se retrouve a 16h pour la reunion de demain, merci de confirmer.",
]

# Live campaigns shown in the mobile app's "Alertes" tab.
# Format: (titre, description, recommandation, niveau, canal, nb_signalements,
#          age_en_heures, epinglee)
ALERTES = [
    (
        "Campagne « faux dépôt Mobile Money »",
        "Vague de SMS annonçant un dépôt reçu par erreur, suivie d'un appel "
        "demandant de renvoyer la somme. L'argent n'a jamais été déposé : la "
        "victime envoie le sien.",
        "Vérifiez toujours votre solde réel via le menu officiel de votre "
        "opérateur avant tout renvoi. Un SMS peut être falsifié.",
        NiveauRisque.ELEVE,
        Alerte.Canal.MIXTE,
        340,
        4,
        True,
    ),
    (
        "Faux site de vérification de compte",
        "Un domaine imitant un service financier local collecte identifiants et "
        "codes PIN. Le lien circule par WhatsApp et par SMS.",
        "N'ouvrez jamais un lien reçu par message pour vous connecter. Saisissez "
        "vous-même l'adresse officielle du service.",
        NiveauRisque.ELEVE,
        Alerte.Canal.LIEN,
        118,
        26,
        False,
    ),
    (
        "Fausses offres de recrutement",
        "Messages proposant un emploi avec « frais de dossier » à verser avant "
        "l'entretien. En forte hausse sur les réseaux sociaux.",
        "Aucun employeur sérieux ne facture des frais à un candidat. Vérifiez "
        "l'existence de l'entreprise et son adresse physique.",
        NiveauRisque.SUSPECT,
        Alerte.Canal.RESEAUX,
        62,
        50,
        False,
    ),
    (
        "Faux gains de tombola",
        "SMS annonçant un gain de 500 000 FCFA avec un lien de « récupération » "
        "et une demande de code PIN. Campagne récurrente.",
        "On ne gagne pas à une loterie à laquelle on n'a pas joué. Ne composez "
        "aucun code, ne cliquez sur aucun lien.",
        NiveauRisque.SUSPECT,
        Alerte.Canal.SMS,
        45,
        96,
        False,
    ),
]

# Prevention cards served to the "Conseils de sécurité" screen.
# Format: (titre, resume, [points], icone, code_categorie)
CONSEILS = [
    (
        "Ne partagez jamais un code reçu par SMS",
        "Aucun agent, aucune banque, aucun opérateur ne vous demandera votre "
        "code OTP ou votre PIN.",
        [
            "Un code reçu par SMS sert à valider VOTRE opération, pas celle d'un tiers.",
            "Si quelqu'un vous le demande au téléphone, c'est une arnaque, sans exception.",
            "Raccrochez et rappelez le service par un numéro que vous avez cherché vous-même.",
        ],
        "key",
        CategorieCode.DEMANDE_OTP_PIN,
    ),
    (
        "Le faux dépôt par erreur",
        "Vous recevez un SMS annonçant un dépôt, puis un appel vous demandant "
        "de le renvoyer.",
        [
            "Vérifiez votre solde réel via le menu officiel de votre opérateur.",
            "Un SMS peut être falsifié : l'expéditeur affiché n'est pas une preuve.",
            "Si le dépôt n'existe pas, vous enverriez votre propre argent.",
        ],
        "wallet",
        CategorieCode.FRAUDE_FINANCIERE,
    ),
    (
        "Les promesses de gain",
        "Vous ne pouvez pas gagner à une loterie à laquelle vous n'avez jamais joué.",
        [
            "Aucun gain légitime n'exige un paiement préalable pour être débloqué.",
            "Les liens de « récupération » mènent à des pages de collecte de données.",
            "Signalez ces messages pour protéger les autres utilisateurs.",
        ],
        "gift",
        CategorieCode.FAUX_CONCOURS,
    ),
    (
        "Reconnaître un faux site",
        "Les faux sites imitent l'apparence des services légitimes à l'identique.",
        [
            "Lisez l'adresse complète dans la barre du navigateur, caractère par caractère.",
            "Méfiez-vous des extensions inhabituelles et des liens raccourcis.",
            "Ne saisissez jamais vos identifiants depuis un lien reçu par message.",
        ],
        "link",
        CategorieCode.PHISHING,
    ),
    (
        "Les faux recrutements",
        "Une offre d'emploi qui demande de l'argent n'est pas une offre d'emploi.",
        [
            "Aucun employeur sérieux ne facture des « frais de dossier » à un candidat.",
            "Vérifiez l'existence de l'entreprise et son adresse physique.",
            "Méfiez-vous des offres reçues sans avoir postulé.",
        ],
        "briefcase",
        CategorieCode.FAUX_RECRUTEMENT,
    ),
]


class Command(BaseCommand):
    help = "Insère des données de démonstration réalistes (arnaques Mobile Money togolaises)."

    def handle(self, *args, **options):
        self._seed_categories()
        self._seed_liste_blanche()
        self._wipe_demo()
        self._seed_numeros_arnaque()
        self._seed_messages()
        self._seed_alertes()
        self._seed_conseils()
        self.stdout.write(self.style.SUCCESS("\n[OK] Données de démo Trustline insérées."))
        self.stdout.write(
            f"   Catégories: {CategorieArnaque.objects.count()} | "
            f"Liste blanche: {ListeBlanche.objects.count()} | "
            f"Numéros: {Numero.objects.count()} | "
            f"Signalements: {Signalement.objects.count()} | "
            f"Messages: {LogAnalyse.objects.filter(type_cible=TypeCible.MESSAGE).count()} | "
            f"Alertes: {Alerte.objects.count()} | "
            f"Conseils: {Conseil.objects.count()}"
        )

    # -- Steps ----------------------------------------------------------
    def _seed_categories(self):
        for code, libelle in CATEGORIES_PAR_DEFAUT:
            CategorieArnaque.objects.get_or_create(
                code=code, defaults={"libelle": libelle}
            )
        self.stdout.write("- Catégories d'arnaque prêtes.")

    def _seed_liste_blanche(self):
        for numero, organisation, source in LISTE_BLANCHE:
            ListeBlanche.objects.get_or_create(
                numero=numero,
                defaults={"organisation": organisation, "source": source},
            )
            # Reflect whitelist status on the Numero table too.
            obj, _ = Numero.objects.get_or_create(numero=numero)
            obj.est_liste_blanche = True
            obj.score_risque = 0
            obj.niveau_risque = "faible"
            obj.save(update_fields=["est_liste_blanche", "score_risque", "niveau_risque"])
        self.stdout.write("- Liste blanche (opérateurs & banques) prête.")

    def _wipe_demo(self):
        """Remove previously seeded scam numbers/reports/messages for reproducibility."""
        numeros = [n for n, _ in NUMEROS_ARNAQUE]
        Signalement.objects.filter(cible__in=numeros).delete()
        Numero.objects.filter(numero__in=numeros).delete()
        LogAnalyse.objects.all().delete()
        from apps.messages.models import Message

        Message.objects.all().delete()

    def _seed_numeros_arnaque(self):
        maintenant = timezone.now()
        for numero, signalements in NUMEROS_ARNAQUE:
            numero_obj, _ = Numero.objects.get_or_create(numero=numero)
            for code, declarant, age_jours, statut in signalements:
                categorie = CategorieArnaque.objects.get(code=code)
                s = Signalement.objects.create(
                    type_cible=TypeCible.NUMERO,
                    cible=numero_obj.numero,
                    numero_cible=numero_obj,
                    categorie=categorie,
                    declarant=declarant,
                    statut=statut,
                )
                # Backdate creation to exercise the recency decay.
                Signalement.objects.filter(pk=s.pk).update(
                    date_creation=maintenant - timedelta(days=age_jours)
                )
            mettre_a_jour_numero(numero_obj)
            invalider_cache_numero(numero_obj.numero)
            numero_obj.refresh_from_db()
            self.stdout.write(
                f"- {numero_obj.numero} -> {numero_obj.niveau_risque.upper()} "
                f"({numero_obj.score_risque}/100, "
                f"{numero_obj.nombre_signalements} signalement(s))"
            )

    def _seed_messages(self):
        for contenu in MESSAGES_DEMO:
            verdict = analyser_message(contenu, source="seed")
            apercu = contenu[:45].replace("\n", " ")
            self.stdout.write(
                f"- Message « {apercu}… » -> {verdict['niveau_risque'].upper()} "
                f"({verdict['score']}/100)"
            )

    def _seed_alertes(self):
        """Recreate the campaign feed so the mobile app always has live content."""
        Alerte.objects.all().delete()
        maintenant = timezone.now()
        for (
            titre,
            description,
            recommandation,
            niveau,
            canal,
            nb,
            age_heures,
            epinglee,
        ) in ALERTES:
            Alerte.objects.create(
                titre=titre,
                description=description,
                recommandation=recommandation,
                niveau_risque=niveau,
                canal=canal,
                nombre_signalements=nb,
                epinglee=epinglee,
                date_debut=maintenant - timedelta(hours=age_heures),
            )
        self.stdout.write(f"- {len(ALERTES)} alertes de campagne publiées.")

    def _seed_conseils(self):
        """Prevention cards are upserted by title so admin edits survive a reseed."""
        for ordre, (titre, resume, points, icone, code) in enumerate(CONSEILS, start=1):
            categorie = CategorieArnaque.objects.filter(code=code).first()
            Conseil.objects.update_or_create(
                titre=titre,
                defaults={
                    "resume": resume,
                    "points": points,
                    "icone": icone,
                    "categorie": categorie,
                    "ordre": ordre,
                    "actif": True,
                },
            )
        self.stdout.write(f"- {len(CONSEILS)} conseils de sécurité prêts.")
