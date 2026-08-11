// Contenu éditorial associé aux catégories réelles du backend (apps/core/constants.py).
// Ce sont des textes pédagogiques rédigés pour le produit — pas des statistiques.

export interface ContenuCategorie {
  description: string;
  signes: string[];
}

export const CONTENU_CATEGORIES: Record<string, ContenuCategorie> = {
  fraude_financiere: {
    description:
      "Manœuvre visant à vous faire transférer de l'argent, souvent via mobile money, sous un faux prétexte (dépôt par erreur, remboursement, frais préalables).",
    signes: [
      "Un message ou appel évoque un dépôt, un gain ou un remboursement non sollicité",
      "On vous demande de renvoyer une somme « par erreur »",
      "Des frais sont exigés avant de recevoir quoi que ce soit",
    ],
  },
  phishing: {
    description:
      "Faux message ou faux site imitant une banque, un opérateur ou une administration pour voler vos identifiants.",
    signes: [
      "Un lien vous demande de « vérifier » ou « réactiver » votre compte",
      "L'adresse du site ressemble à l'officielle sans l'être exactement",
      "Le message crée une urgence artificielle",
    ],
  },
  faux_concours: {
    description:
      "Fausse annonce de gain (loterie, tirage, concours) destinée à extorquer des frais de déblocage.",
    signes: [
      "Vous avez « gagné » un concours auquel vous n'avez jamais participé",
      "Il faut payer des frais pour débloquer le gain",
      "Le message est diffusé massivement, pas personnalisé",
    ],
  },
  faux_recrutement: {
    description:
      "Fausse offre d'emploi exigeant des frais de dossier ou des données personnelles avant tout entretien réel.",
    signes: [
      "Le poste est décrit vaguement, sans entretien préalable",
      "Des frais sont demandés avant l'embauche",
      "L'entreprise n'a pas de présence vérifiable",
    ],
  },
  usurpation_identite: {
    description:
      "Un contact se fait passer pour un proche, un agent officiel ou une administration pour gagner votre confiance.",
    signes: [
      "Le numéro ou le profil imite un service connu sans en être un canal officiel",
      "La demande est inhabituelle pour ce contact",
      "On vous met la pression pour agir vite, sans vérifier",
    ],
  },
  demande_otp_pin: {
    description:
      "Demande directe de votre code secret, PIN ou code de vérification (OTP) — jamais légitime.",
    signes: [
      "On vous demande votre code PIN ou le code reçu par SMS",
      "L'interlocuteur se présente comme un « agent » du service",
      "Le prétexte est une vérification, un blocage ou une sécurisation de compte",
    ],
  },
  autre: {
    description: "Signalement ne correspondant pas exactement aux catégories ci-dessus.",
    signes: ["Tout élément inhabituel : demande pressante, promesse improbable, contact inconnu insistant"],
  },
};
