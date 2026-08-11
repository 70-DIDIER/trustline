// Configuration centralisée — SEUL endroit où l'URL de l'API est définie.
// Pas de hardcode dispersé. En production, remplacez API_BASE par votre domaine
// et ajoutez-le à `host_permissions` dans manifest.json.
export const CONFIG = {
  API_BASE: "http://127.0.0.1:8000/api",
  ENDPOINT_ANALYSE: "/extension/analyser/",
  ENDPOINT_SIGNALEMENT: "/signalements/",
  // Cache local des analyses (URL/numéro) — performance + moins de requêtes.
  CACHE_TTL_MS: 30 * 60 * 1000, // 30 min
  // Anti-spam backend : deux analyses identiques rapprochées = une seule requête.
  DEDUP_WINDOW_MS: 4000,
  // Timeout d'une requête d'analyse distante.
  REQUEST_TIMEOUT_MS: 6000,
  // Historique local : nombre max d'entrées conservées.
  HISTORY_MAX: 50,
};

// Réglages par défaut (surchargés par la page Options, stockés en local).
export const DEFAULT_SETTINGS = {
  protectionAuto: true, // analyse passive des liens/pages
  analyserLiens: true,
  whatsapp: true,
  gmail: true,
  outlook: true,
  notifications: true,
  historiqueLocal: true,
};
