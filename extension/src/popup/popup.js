import { VERDICT_LABEL, VERDICT_TONE } from "../lib/verdict.js";

const $ = (id) => document.getElementById(id);

function sendSW(message) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage(message, (resp) => resolve(chrome.runtime.lastError ? null : resp));
  });
}

// Détection heuristique du type collé (aligné avec le site).
function detecter(v) {
  const t = v.trim();
  const chiffres = t.replace(/[^0-9]/g, "");
  if (chiffres.length >= 8 && chiffres.length <= 15 && chiffres.length / t.length > 0.6) return "phone";
  if (/^https?:\/\//i.test(t) || /^[a-z0-9-]+(\.[a-z0-9-]+)+(\/\S*)?$/i.test(t)) return "url";
  return "message";
}

function tempsRelatif(ts) {
  const d = Math.round((Date.now() - ts) / 60000);
  if (d < 1) return "à l'instant";
  if (d < 60) return `il y a ${d} min`;
  const h = Math.round(d / 60);
  if (h < 24) return `il y a ${h} h`;
  return new Date(ts).toLocaleDateString("fr-FR");
}

function el(tag, props = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "text") n.textContent = v;
    else if (k === "class") n.className = v;
    else if (k === "style") n.setAttribute("style", v);
    else n.setAttribute(k, v);
  }
  for (const c of kids) if (c) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
  return n;
}

function renderResult(result, payload) {
  const tone = VERDICT_TONE[result.verdict] || VERDICT_TONE.unknown;
  const box = $("result");
  box.textContent = "";
  box.hidden = false;

  box.appendChild(el("div", { class: "verdict", style: `background:${tone.bg}; color:${tone.fg};` },
    el("span", { text: VERDICT_LABEL[result.verdict] || "—" }),
    el("span", { class: "score", text: typeof result.score === "number" ? `${result.score}/100` : "" })
  ));

  if (result.signals && result.signals.length) {
    const ul = el("ul");
    result.signals.slice(0, 5).forEach((s, i) =>
      ul.appendChild(el("li", {}, el("span", { class: "n", text: String(i + 1).padStart(2, "0") }), el("span", { text: s.label })))
    );
    box.appendChild(ul);
  }
  if (result.recommendation) box.appendChild(el("p", { class: "reco", text: result.recommendation }));

  if (result.verdict !== "safe" && payload) {
    const wrap = el("div", { class: "report" });
    const btn = el("button", { class: "btn primary", text: "Signaler cette menace" });
    btn.addEventListener("click", async () => {
      if (!window.confirm("Transmettre cet élément à TrustLine pour contribuer à la détection ?\n\nEnvoi anonyme, contenu minimal.")) return;
      btn.disabled = true; btn.textContent = "Envoi…";
      const typeCible = payload.type === "phone" ? "numero" : payload.type === "url" ? "lien" : "message";
      const res = await sendSW({ kind: "REPORT", input: { type_cible: typeCible, cible: payload.content, categorie: "autre" } });
      btn.textContent = res && res.ok && res.data && res.data.ok ? "Signalement envoyé" : "Échec de l'envoi";
    });
    wrap.appendChild(btn);
    box.appendChild(wrap);
  }

  box.appendChild(el("p", { class: "note", text: result.remoteAvailable ? "Analyse : moteur TrustLine" : "Analyse locale — vérification distante indisponible" }));
}

async function analyser(content) {
  const v = content.trim();
  if (!v) return;
  const type = detecter(v);
  const btn = $("analyser");
  btn.disabled = true; btn.textContent = "Analyse…";
  const payload = { type, content: v, context: "popup" };
  const resp = await sendSW({ kind: "ANALYSE", payload });
  btn.disabled = false; btn.textContent = "Analyser";
  if (resp && resp.ok) { renderResult(resp.data, payload); refreshStatsAndHistory(); }
}

async function refreshStatsAndHistory() {
  const stats = await sendSW({ kind: "GET_STATS" });
  if (stats && stats.ok && stats.data.analyses > 0) {
    $("stats").hidden = false;
    $("stat-analyses").textContent = stats.data.analyses;
    $("stat-menaces").textContent = stats.data.menaces;
  }
  const hist = await sendSW({ kind: "GET_HISTORY" });
  const list = $("history-list");
  list.textContent = "";
  const items = (hist && hist.ok && hist.data) || [];
  $("history-empty").hidden = items.length > 0;
  items.slice(0, 8).forEach((h) => {
    const tone = VERDICT_TONE[h.verdict] || VERDICT_TONE.unknown;
    list.appendChild(el("li", {},
      el("span", { class: "h-label", text: h.label }),
      el("span", { style: "display:flex; align-items:center; gap:8px;" },
        el("span", { class: "h-time", text: tempsRelatif(h.at) }),
        el("span", { class: "pill", style: `background:${tone.bg}; color:${tone.fg};`, text: VERDICT_LABEL[h.verdict] || "—" })
      )
    ));
  });
}

$("analyser").addEventListener("click", () => analyser($("input").value));
$("input").addEventListener("keydown", (e) => { if ((e.ctrlKey || e.metaKey) && e.key === "Enter") analyser($("input").value); });
$("analyser-page").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab && tab.url && /^https?:/i.test(tab.url)) { $("input").value = tab.url; analyser(tab.url); }
  else window.alert("Cette page ne peut pas être analysée.");
});
$("clear").addEventListener("click", async () => { await sendSW({ kind: "CLEAR_HISTORY" }); refreshStatsAndHistory(); });
$("open-options").addEventListener("click", (e) => { e.preventDefault(); chrome.runtime.openOptionsPage(); });

refreshStatsAndHistory();
