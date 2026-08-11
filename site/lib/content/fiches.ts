// Fiches pédagogiques — contenu éditorial rédigé pour /apprendre.
// Ancré dans les schémas d'arnaque réellement documentés au Togo (ANCy, CERT.tg),
// pas des statistiques du backend.

export interface Fiche {
  titre: string;
  commence: string;
  cherche: string;
  signaux: string[];
  jamais: string[];
  faire: string[];
}

export const FICHES: Fiche[] = [
  {
    titre: "Le faux dépôt",
    commence:
      "Un SMS ou une notification mobile money annonce qu'un dépôt a été reçu « par erreur » et invite à le renvoyer ou à « confirmer » l'opération.",
    cherche:
      "Vous faire initier vous-même un transfert réel vers le compte de l'arnaqueur, en misant sur la précipitation.",
    signaux: [
      "Le message évoque un dépôt que vous n'avez jamais demandé",
      "On vous presse de « confirmer » via un code USSD non officiel",
      "Le montant est rond et l'urgence est artificielle",
    ],
    jamais: ["Ne composez aucun code USSD reçu par SMS", "Ne renvoyez jamais un « dépôt par erreur »"],
    faire: ["Vérifiez votre solde réel dans l'application officielle de votre opérateur", "Signalez le numéro"],
  },
  {
    titre: "Le faux agent",
    commence:
      "Un appel ou un message se présente comme un agent Togocom, Moov, ou d'une banque, pour une « vérification » ou un « déblocage » de compte.",
    cherche: "Obtenir votre code PIN, votre code OTP ou un accès direct à votre compte.",
    signaux: [
      "On vous demande votre code secret « pour vérification »",
      "L'appel crée un sentiment d'urgence ou de menace (compte bloqué, suspendu)",
      "Le numéro appelant n'est pas un numéro officiel publié",
    ],
    jamais: ["Ne communiquez jamais un code PIN ou OTP à un appelant", "Ne rappelez pas le numéro reçu par SMS"],
    faire: ["Raccrochez et contactez le service client officiel via le numéro publié sur le site de l'opérateur"],
  },
  {
    titre: "Le faux gain",
    commence: "Un message félicite un « gagnant » d'une loterie ou d'un concours auquel il n'a jamais participé.",
    cherche: "Vous faire payer des « frais de déblocage » pour un gain qui n'existe pas.",
    signaux: [
      "Vous avez « gagné » sans avoir participé",
      "Il faut payer pour recevoir le gain",
      "Le message est envoyé en masse, pas personnalisé",
    ],
    jamais: ["Ne payez jamais pour « débloquer » un gain"],
    faire: ["Supprimez le message", "Signalez-le si le numéro insiste"],
  },
  {
    titre: "Le faux emploi",
    commence: "Une offre d'emploi très attractive circule sur les réseaux sociaux ou par message direct.",
    cherche: "Facturer de faux frais de dossier, de formation ou d'uniforme avant tout entretien réel.",
    signaux: [
      "Aucun entretien n'est prévu avant le paiement",
      "Le poste est vague, le salaire hors norme",
      "L'entreprise n'a pas d'existence vérifiable",
    ],
    jamais: ["Ne payez jamais pour obtenir un emploi"],
    faire: ["Vérifiez l'existence légale de l'entreprise avant toute démarche"],
  },
  {
    titre: "Le phishing",
    commence:
      "Un message ou un faux site imite une banque, un opérateur ou une administration pour « vérifier » votre compte.",
    cherche: "Voler vos identifiants ou vos données bancaires via un formulaire piégé.",
    signaux: [
      "Le lien mène à une adresse qui ressemble à l'officielle sans l'être",
      "Le site demande des identifiants complets, y compris un code secret",
      "Le message crée une urgence (« compte suspendu »)",
    ],
    jamais: ["Ne cliquez pas sur un lien reçu par SMS pour « vérifier un compte »"],
    faire: ["Tapez vous-même l'adresse officielle dans votre navigateur"],
  },
  {
    titre: "L'usurpation d'identité",
    commence: "Un profil ou un numéro se fait passer pour un proche, un agent officiel ou une administration.",
    cherche: "Exploiter la confiance déjà accordée à la personne ou à l'institution usurpée.",
    signaux: [
      "Le ton ou les habitudes du contact semblent différents",
      "La demande est inhabituelle (argent, code, document)",
      "Le contact évite tout appel vocal de vérification",
    ],
    jamais: ["Ne vous fiez pas uniquement au nom affiché"],
    faire: ["Vérifiez par un autre canal avant d'agir (appel direct, rencontre)"],
  },
  {
    titre: "Le faux site marchand",
    commence: "Une boutique en ligne propose des prix très attractifs, souvent relayée par publicité ou réseaux sociaux.",
    cherche: "Encaisser le paiement sans jamais livrer le produit.",
    signaux: [
      "Aucune adresse physique ni moyen de contact vérifiable",
      "Le paiement se fait uniquement par mobile money direct, sans plateforme sécurisée",
      "Les avis clients sont absents ou tous identiques",
    ],
    jamais: ["Ne payez pas d'avance sur un site inconnu sans vérification"],
    faire: ["Recherchez le nom du site avant tout paiement", "Privilégiez le paiement à la livraison quand c'est possible"],
  },
];

export const REFLEXES = [
  "Vérifiez.",
  "Ne communiquez jamais votre PIN.",
  "Ne cliquez pas dans l'urgence.",
  "Appelez le service officiel.",
  "Signalez.",
];
