// Types alignés EXACTEMENT sur les serializers DRF réels du backend
// (github.com/70-DIDIER/trustline, apps/*/serializers.py). Aucun champ inventé.

export type NiveauRisque = "faible" | "suspect" | "eleve";

export type TypeCible = "numero" | "sms" | "lien" | "site" | "message";

// --- POST /api/numeros/verifier/ ---
export interface VerdictNumero {
  numero: string;
  score: number;
  niveau_risque: NiveauRisque;
  est_liste_blanche: boolean;
  organisation: string | null;
  nombre_signalements: number;
  date_dernier_signalement: string | null;
  categories: string[];
  indices: string[];
  recommandation: string;
}

// --- GET /api/numeros/{numero}/ ---
export interface NumeroDetail {
  numero: string;
  score_risque: number;
  niveau_risque: NiveauRisque;
  nombre_signalements: number;
  date_dernier_signalement: string | null;
  est_liste_blanche: boolean;
  date_creation: string;
}

// --- POST /api/messages/analyser/ ---
export interface VerdictMessage {
  score: number;
  niveau_risque: NiveauRisque;
  indices: string[];
  recommandation: string;
  categories: string[];
  liens_extraits: string[];
  numeros_extraits: string[];
}

// --- POST /api/liens/analyser/ ---
export interface VerdictLien {
  url: string;
  domaine: string;
  score: number;
  niveau_risque: NiveauRisque;
  indices: string[];
  recommandation: string;
}

// --- POST /api/signalements/ ---
export interface SignalementInput {
  type_cible: TypeCible;
  cible: string;
  categorie: string;
  declarant_id: string;
  commentaire?: string;
}

export interface Signalement {
  id: number;
  type_cible: TypeCible;
  cible: string;
  categorie: string;
  declarant: string;
  commentaire: string;
  statut: "en_attente" | "valide" | "conteste" | "rejete";
  date_creation: string;
  message?: string;
  reputation_cible?: {
    numero: string;
    score_risque: number;
    niveau_risque: NiveauRisque;
    nombre_signalements: number;
  };
}

// --- GET /api/stats/ ---
export interface Stats {
  total_signalements: number;
  total_numeros_suivis: number;
  total_analyses: number;
  signalements_par_categorie: { categorie__code: string; categorie__libelle: string; total: number }[];
  signalements_par_statut: { statut: string; total: number }[];
  top_numeros_signales: {
    numero: string;
    score_risque: number;
    niveau_risque: NiveauRisque;
    nombre_signalements: number;
  }[];
}

// --- GET /api/alertes/ (endpoint ajouté ce jour, dérivé des signalements réels) ---
export interface AlertePublique {
  categorie: string;
  libelle: string;
  nombre_signalements: number;
  niveau_risque: NiveauRisque;
  derniere_activite: string | null;
  types_cibles: Record<string, number>;
}

// --- GET /api/health/ ---
export interface HealthResponse {
  status: string;
  service: string;
  time: string;
}

// Référentiels reproduits depuis apps/core/constants.py (CategorieCode, TypeCible).
// Ce ne sont pas des données dynamiques — ce sont les choix fixes acceptés par l'API.
export const CATEGORIES: { code: string; label: string }[] = [
  { code: "fraude_financiere", label: "Fraude financière" },
  { code: "phishing", label: "Phishing / hameçonnage" },
  { code: "faux_concours", label: "Faux concours ou promesse de gain" },
  { code: "faux_recrutement", label: "Faux recrutement / fausse offre d'emploi" },
  { code: "usurpation_identite", label: "Usurpation d'identité (service officiel)" },
  { code: "demande_otp_pin", label: "Demande de code OTP / PIN / mot de passe" },
  { code: "autre", label: "Autre type d'arnaque" },
];

export const TYPES_CIBLE: { code: TypeCible; label: string }[] = [
  { code: "numero", label: "Numéro de téléphone" },
  { code: "sms", label: "SMS" },
  { code: "lien", label: "Lien / site web" },
  { code: "message", label: "Message (WhatsApp, réseau social…)" },
];

// Canaux de réception affichés dans le formulaire de signalement (étape "contexte").
// Le backend ne stocke pas encore ce champ séparément — il est ajouté au commentaire
// de façon transparente (voir signalements.ts) plutôt que d'inventer un champ API.
export const CANAUX_RECEPTION = [
  "SMS",
  "Appel téléphonique",
  "WhatsApp",
  "Facebook",
  "Site web",
  "Autre",
] as const;
