import type { NiveauRisque } from "@/lib/api";

export type ModeVerification = "auto" | "numero" | "lien" | "message";

export interface VerdictNormalise {
  type: "numero" | "lien" | "message";
  cible: string;
  niveau_risque: NiveauRisque;
  score: number;
  indices: string[];
  recommandation: string;
  meta: { label: string; value: string }[];
}
