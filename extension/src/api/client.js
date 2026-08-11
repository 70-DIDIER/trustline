// Couche API de l'extension (exécutée dans le service worker, qui dispose des
// host_permissions vers le backend — évite les problèmes de CORS des content scripts).
// Cache + déduplication + timeout + échec gracieux (jamais "safe" sur erreur).
import { CONFIG } from "../lib/config.js";

const cache = new Map(); // clé -> { at, data }
const enVol = new Map(); // clé -> Promise (déduplication des requêtes simultanées)

function cleFromPayload(p) {
  return `${p.type}:${(p.content || "").slice(0, 200)}`;
}

async function fetchTimeout(url, opts) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), CONFIG.REQUEST_TIMEOUT_MS);
  try {
    return await fetch(url, { ...opts, signal: ctrl.signal });
  } finally {
    clearTimeout(t);
  }
}

/**
 * Analyse distante via le backend TrustLine.
 * @returns {Promise<object|null>} réponse normalisée backend, ou null si indisponible.
 */
export async function analyserDistant(payload) {
  const cle = cleFromPayload(payload);

  const hit = cache.get(cle);
  if (hit && Date.now() - hit.at < CONFIG.CACHE_TTL_MS) return hit.data;
  if (enVol.has(cle)) return enVol.get(cle);

  const p = (async () => {
    try {
      const res = await fetchTimeout(`${CONFIG.API_BASE}${CONFIG.ENDPOINT_ANALYSE}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) return null; // 4xx/5xx -> pas de verdict distant, on retombera sur le local
      const data = await res.json();
      cache.set(cle, { at: Date.now(), data });
      return data;
    } catch {
      return null; // offline / timeout / réseau
    } finally {
      enVol.delete(cle);
    }
  })();

  enVol.set(cle, p);
  return p;
}

/** Envoi d'un signalement (avec consentement explicite côté UI). */
export async function envoyerSignalement(input) {
  try {
    const res = await fetchTimeout(`${CONFIG.API_BASE}${CONFIG.ENDPOINT_SIGNALEMENT}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
    if (!res.ok) return { ok: false };
    return { ok: true, data: await res.json() };
  } catch {
    return { ok: false };
  }
}
