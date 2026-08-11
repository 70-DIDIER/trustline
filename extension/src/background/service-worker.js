// Service worker MV3 (module) — routeur de messages typé + badge de navigation
// (heuristique locale, sans spammer le backend) + notifications risque élevé.
import { analyseLocale, combiner } from "../detection/engine.js";
import { analyserDistant, envoyerSignalement } from "../api/client.js";
import { getSettings, setSettings, getHistory, clearHistory, clearAll, addHistory, bumpStats, getStats, getDeclarantId } from "../storage/store.js";

const BADGE = {
  high: { text: "!", color: "#d64545" },
  suspicious: { text: "!", color: "#c98a16" },
  low: { text: "", color: "#18b77a" },
  safe: { text: "", color: "#18b77a" },
  unknown: { text: "", color: "#667085" },
};
const notifies = new Set(); // URLs déjà notifiées (dédup en mémoire)

// Analyse complète (local + distant) — cœur réutilisé par la popup et les content scripts.
async function analyser(payload) {
  const local = analyseLocale(payload);
  const distant = await analyserDistant(payload);
  const resultat = combiner(local, distant);
  await bumpStats(resultat.verdict);
  await addHistory({
    kind: payload.type,
    label: payload.type === "url" ? (resultat.meta?.domaine || "lien") : payload.type === "phone" ? payload.content : "Message analysé",
    verdict: resultat.verdict,
  });
  return resultat;
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  (async () => {
    try {
      switch (msg?.kind) {
        case "ANALYSE":
          sendResponse({ ok: true, data: await analyser(msg.payload) });
          break;
        case "ANALYSE_LOCAL":
          // Rapide, local uniquement (pas de réseau, pas d'historique) : pré-scan des liens.
          sendResponse({ ok: true, data: analyseLocale(msg.payload) });
          break;
        case "REPORT": {
          // L'UI a déjà recueilli le consentement. On complète avec l'id anonyme.
          const declarant_id = await getDeclarantId();
          const input = {
            type_cible: msg.input.type_cible,
            cible: String(msg.input.cible || "").slice(0, 480),
            categorie: msg.input.categorie || "autre",
            declarant_id,
            commentaire: "Signalé via l'extension TrustLine",
          };
          sendResponse({ ok: true, data: await envoyerSignalement(input) });
          break;
        }
        case "GET_STATS":
          sendResponse({ ok: true, data: await getStats() });
          break;
        case "GET_HISTORY":
          sendResponse({ ok: true, data: await getHistory() });
          break;
        case "CLEAR_HISTORY":
          await clearHistory();
          sendResponse({ ok: true });
          break;
        case "GET_SETTINGS":
          sendResponse({ ok: true, data: await getSettings() });
          break;
        case "SET_SETTINGS":
          sendResponse({ ok: true, data: await setSettings(msg.patch) });
          break;
        case "CLEAR_ALL":
          await clearAll();
          sendResponse({ ok: true });
          break;
        default:
          sendResponse({ ok: false, error: "message inconnu" });
      }
    } catch (e) {
      sendResponse({ ok: false, error: String(e) });
    }
  })();
  return true; // réponse asynchrone
});

// Badge de navigation : heuristique LOCALE uniquement (rapide, ne consomme pas le backend).
chrome.tabs.onUpdated.addListener(async (tabId, info, tab) => {
  if (info.status !== "complete" || !tab.url || !/^https?:\/\//i.test(tab.url)) return;
  const settings = await getSettings();
  if (!settings.protectionAuto) return;

  const local = analyseLocale({ type: "url", content: tab.url });
  const b = BADGE[local.verdict] || BADGE.unknown;
  chrome.action.setBadgeText({ tabId, text: b.text });
  chrome.action.setBadgeBackgroundColor({ tabId, color: b.color });

  if (local.verdict === "high" && settings.notifications && !notifies.has(tab.url)) {
    notifies.add(tab.url);
    chrome.notifications.create({
      type: "basic",
      iconUrl: "public/icons/128.png",
      title: "TrustLine — lien potentiellement dangereux",
      message: "Cette page présente des signaux d'hameçonnage. Ne saisissez aucune donnée.",
      priority: 2,
    });
  }
});
