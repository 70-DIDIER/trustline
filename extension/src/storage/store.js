// Stockage LOCAL uniquement (chrome.storage.local) — réglages + historique.
// Aucun historique serveur par défaut. Aucune donnée privée superflue.
import { DEFAULT_SETTINGS, CONFIG } from "../lib/config.js";

const KEY_SETTINGS = "tl_settings";
const KEY_HISTORY = "tl_history";
const KEY_STATS = "tl_stats_today";

export async function getSettings() {
  const { [KEY_SETTINGS]: s } = await chrome.storage.local.get(KEY_SETTINGS);
  return { ...DEFAULT_SETTINGS, ...(s || {}) };
}

export async function setSettings(patch) {
  const current = await getSettings();
  const next = { ...current, ...patch };
  await chrome.storage.local.set({ [KEY_SETTINGS]: next });
  return next;
}

export async function getHistory() {
  const { [KEY_HISTORY]: h } = await chrome.storage.local.get(KEY_HISTORY);
  return Array.isArray(h) ? h : [];
}

export async function addHistory(entry) {
  const settings = await getSettings();
  if (!settings.historiqueLocal) return;
  const h = await getHistory();
  // On ne conserve qu'un libellé court — jamais le contenu privé intégral.
  h.unshift({
    at: Date.now(),
    kind: entry.kind, // "url" | "message" | "phone"
    label: entry.label, // ex. "web.example.com" ou "Message analysé"
    verdict: entry.verdict,
  });
  await chrome.storage.local.set({ [KEY_HISTORY]: h.slice(0, CONFIG.HISTORY_MAX) });
}

export async function clearHistory() {
  await chrome.storage.local.set({ [KEY_HISTORY]: [] });
}

export async function clearAll() {
  await chrome.storage.local.clear();
}

// Compteurs du jour (analyses / menaces) — remis à zéro chaque jour, purement local.
export async function bumpStats(verdict) {
  const today = new Date().toISOString().slice(0, 10);
  const { [KEY_STATS]: s } = await chrome.storage.local.get(KEY_STATS);
  const stats = s && s.day === today ? s : { day: today, analyses: 0, menaces: 0 };
  stats.analyses += 1;
  if (verdict === "high" || verdict === "suspicious") stats.menaces += 1;
  await chrome.storage.local.set({ [KEY_STATS]: stats });
  return stats;
}

// Identifiant déclarant anonyme, persistant localement — aucune donnée personnelle.
export async function getDeclarantId() {
  const KEY = "tl_declarant";
  const { [KEY]: id } = await chrome.storage.local.get(KEY);
  if (id) return id;
  const nouveau = `ext-${crypto.randomUUID()}`;
  await chrome.storage.local.set({ [KEY]: nouveau });
  return nouveau;
}

export async function getStats() {
  const today = new Date().toISOString().slice(0, 10);
  const { [KEY_STATS]: s } = await chrome.storage.local.get(KEY_STATS);
  return s && s.day === today ? s : { day: today, analyses: 0, menaces: 0 };
}
