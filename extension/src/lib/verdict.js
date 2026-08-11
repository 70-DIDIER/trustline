// Format de verdict normalisé de l'extension et correspondance avec le backend.
// Backend (français) : niveau_risque ∈ { faible, suspect, eleve }.
// Extension (normalisé) : verdict ∈ { safe, low, suspicious, high, unknown }.

/** @typedef {"safe"|"low"|"suspicious"|"high"|"unknown"} Verdict */

export const VERDICT = Object.freeze({
  SAFE: "safe",
  LOW: "low",
  SUSPICIOUS: "suspicious",
  HIGH: "high",
  UNKNOWN: "unknown",
});

// Le backend ne renvoie que 3 niveaux ; on les mappe vers l'échelle de l'extension.
const FROM_BACKEND = {
  faible: VERDICT.LOW,
  suspect: VERDICT.SUSPICIOUS,
  eleve: VERDICT.HIGH,
};

export function verdictFromBackend(niveauRisque) {
  return FROM_BACKEND[niveauRisque] || VERDICT.UNKNOWN;
}

// Décision locale à partir d'un score de signaux (0-100) — voir detection/engine.js.
export function verdictFromScore(score) {
  if (score >= 70) return VERDICT.HIGH;
  if (score >= 40) return VERDICT.SUSPICIOUS;
  if (score >= 15) return VERDICT.LOW;
  return VERDICT.SAFE;
}

export const VERDICT_LABEL = {
  safe: "Sûr",
  low: "Faible risque",
  suspicious: "Prudence",
  high: "Risque élevé",
  unknown: "Analyse indisponible",
};

// Tons alignés sur le design system du site (bleu marque, vert/ambre/rouge sémantiques, gris).
export const VERDICT_TONE = {
  safe: { fg: "#18b77a", bg: "#e7f7f0", dot: "#18b77a" },
  low: { fg: "#18b77a", bg: "#e7f7f0", dot: "#18b77a" },
  suspicious: { fg: "#c98a16", bg: "#fbf3e2", dot: "#c98a16" },
  high: { fg: "#d64545", bg: "#fcecec", dot: "#d64545" },
  unknown: { fg: "#667085", bg: "#f1f4f8", dot: "#667085" },
};

export function normaliserVerdict(niveauRisque) {
  return verdictFromBackend(niveauRisque);
}
