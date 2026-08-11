// UI TrustLine injectée dans les pages hôtes — entièrement en Shadow DOM pour ne
// jamais polluer les styles de WhatsApp/Gmail/le web (§36). Tout contenu analysé
// est rendu via textContent (jamais innerHTML) pour prévenir tout XSS (§37).
(function () {
  "use strict";
  const TL = (window.TL = window.TL || {});

  const TONE = {
    safe: { fg: "#0f8f5f", bg: "#e7f7f0", label: "Sûr" },
    low: { fg: "#0f8f5f", bg: "#e7f7f0", label: "Faible risque" },
    suspicious: { fg: "#a06f0f", bg: "#fbf3e2", label: "Prudence" },
    high: { fg: "#c23a3a", bg: "#fcecec", label: "Risque élevé" },
    unknown: { fg: "#4b5563", bg: "#f1f4f8", label: "Analyse indisponible" },
  };

  function el(tag, props = {}, ...kids) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) {
      if (k === "text") n.textContent = v; // contenu = toujours textContent (anti-XSS)
      else if (k === "style") n.setAttribute("style", v);
      else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v);
    }
    for (const c of kids) if (c) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    return n;
  }

  const HOST_ID = "trustline-shadow-host";
  function ensureHost() {
    let host = document.getElementById(HOST_ID);
    if (host) host.remove();
    host = document.createElement("div");
    host.id = HOST_ID;
    host.setAttribute("style", "all: initial; position: fixed; z-index: 2147483647;");
    document.documentElement.appendChild(host);
    return host.attachShadow({ mode: "open" });
  }

  const BASE_CSS = `
    :host { all: initial; }
    * { box-sizing: border-box; font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; }
    .card { position: fixed; top: 84px; right: 20px; width: 340px; max-width: calc(100vw - 40px);
      background: #fff; color: #111827; border: 1px solid #e6eaf0; border-radius: 14px;
      box-shadow: 0 12px 40px -12px rgba(17,24,39,.28); overflow: hidden; }
    .head { display:flex; align-items:center; justify-content:space-between; padding: 12px 14px; border-bottom: 1px solid #eef1f6; }
    .brand { display:flex; align-items:center; gap:8px; font-weight:700; font-size:13px; }
    .brand svg { width:18px; height:18px; }
    .x { cursor:pointer; border:0; background:transparent; color:#667085; font-size:18px; line-height:1; padding:2px 6px; border-radius:6px; }
    .x:hover { background:#f1f4f8; }
    .body { padding: 14px; }
    .verdict { display:flex; align-items:center; justify-content:space-between; gap:10px; padding:10px 12px; border-radius:10px; font-weight:800; font-size:14px; }
    .verdict .score { font-variant-numeric: tabular-nums; font-weight:700; font-size:13px; opacity:.85; }
    .lbl { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.04em; color:#667085; margin:14px 0 6px; }
    ul { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:8px; }
    li { display:flex; gap:8px; align-items:flex-start; font-size:13px; line-height:1.45; color:#111827; }
    li .n { flex:none; width:18px; height:18px; border-radius:5px; background:#f1f4f8; color:#475467; font-size:10px; font-weight:700; display:grid; place-items:center; margin-top:1px; }
    .reco { margin-top:14px; padding-top:12px; border-top:1px solid #eef1f6; font-size:13px; color:#475467; line-height:1.5; }
    .actions { display:flex; gap:8px; margin-top:16px; }
    button.act { flex:1; cursor:pointer; border-radius:8px; padding:9px 10px; font-size:13px; font-weight:600; border:1px solid #d5dae3; background:#fff; color:#111827; }
    button.act:hover { background:#f7f8fa; }
    button.act.primary { background:#2457d6; color:#fff; border-color:#2457d6; }
    button.act.primary:hover { background:#1d49bd; }
    button.act.danger { background:#c23a3a; color:#fff; border-color:#c23a3a; }
    .muted { font-size:11px; color:#667085; margin-top:10px; }
    .reveal { animation: tlin .22s ease-out; }
    @keyframes tlin { from { opacity:0; transform: translateY(6px);} to { opacity:1; transform:none; } }
    @media (prefers-reduced-motion: reduce){ .reveal{ animation:none; } }
  `;

  function logo() {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
    p.setAttribute("d", "M12 3l7 3v5.2c0 4.4-3 8-7 9-4-1-7-4.6-7-9V6l7-3Z");
    p.setAttribute("stroke", "#2457d6"); p.setAttribute("stroke-width", "1.7"); p.setAttribute("stroke-linejoin", "round");
    svg.appendChild(p);
    return svg;
  }

  // Panneau d'analyse complet.
  function panel(result, opts = {}) {
    const tone = TONE[result.verdict] || TONE.unknown;
    const shadow = ensureHost();
    shadow.appendChild(el("style", { text: BASE_CSS }));

    const closeBtn = el("button", { class: "x", "aria-label": "Fermer", text: "×", onclick: () => close() });
    const head = el("div", { class: "head" },
      el("div", { class: "brand" }, logo(), el("span", { text: "TrustLine" })),
      closeBtn
    );

    const verdict = el("div", { class: "verdict", style: `background:${tone.bg}; color:${tone.fg};` },
      el("span", { text: tone.label }),
      el("span", { class: "score", text: typeof result.score === "number" ? `${result.score}/100` : "" })
    );

    const body = el("div", { class: "body reveal" }, verdict);

    if (opts.targetLabel) {
      body.appendChild(el("p", { class: "muted", text: opts.targetLabel }));
    }

    if (result.signals && result.signals.length) {
      body.appendChild(el("p", { class: "lbl", text: `${result.signals.length} signal${result.signals.length > 1 ? "aux" : ""} détecté${result.signals.length > 1 ? "s" : ""}` }));
      const ul = el("ul");
      result.signals.slice(0, 6).forEach((s, i) =>
        ul.appendChild(el("li", {}, el("span", { class: "n", text: String(i + 1).padStart(2, "0") }), el("span", { text: s.label })))
      );
      body.appendChild(ul);
    }

    if (result.recommendation) body.appendChild(el("p", { class: "reco", text: result.recommendation }));

    const actions = el("div", { class: "actions" });
    if (opts.onReport && result.verdict !== "safe") {
      actions.appendChild(el("button", {
        class: "act primary", text: "Signaler",
        onclick: () => opts.onReport(),
      }));
    }
    actions.appendChild(el("button", { class: "act", text: "Fermer", onclick: () => close() }));
    body.appendChild(actions);

    body.appendChild(el("p", { class: "muted", text: result.remoteAvailable ? "Analyse : moteur TrustLine" : "Analyse locale — vérification distante indisponible" }));

    const card = el("div", { class: "card", role: "dialog", "aria-label": "Analyse TrustLine" }, head, body);
    shadow.appendChild(card);

    function close() {
      const h = document.getElementById(HOST_ID);
      if (h) h.remove();
      opts.onClose && opts.onClose();
    }
    return { close };
  }

  // Avertissement avant navigation vers un lien à risque (§10/§47).
  function warningBeforeNav(result, opts = {}) {
    const tone = TONE[result.verdict] || TONE.unknown;
    const shadow = ensureHost();
    shadow.appendChild(el("style", { text: BASE_CSS + `
      .overlay { position: fixed; inset:0; background: rgba(17,24,39,.45); display:grid; place-items:center; }
      .modal { width: 400px; max-width: calc(100vw - 32px); background:#fff; border-radius:16px; overflow:hidden; box-shadow:0 24px 60px -20px rgba(0,0,0,.5); }
    ` }));
    const signals = el("ul");
    (result.signals || []).slice(0, 4).forEach((s, i) =>
      signals.appendChild(el("li", {}, el("span", { class: "n", text: String(i + 1).padStart(2, "0") }), el("span", { text: s.label })))
    );
    const modal = el("div", { class: "modal reveal" },
      el("div", { class: "head" }, el("div", { class: "brand" }, logo(), el("span", { text: "TrustLine — attention" }))),
      el("div", { class: "body" },
        el("div", { class: "verdict", style: `background:${tone.bg}; color:${tone.fg};` }, el("span", { text: tone.label }), el("span", { class: "score", text: result.score ? `${result.score}/100` : "" })),
        opts.domain ? el("p", { class: "muted", text: `Domaine : ${opts.domain}` }) : null,
        el("p", { class: "lbl", text: "Pourquoi ?" }),
        signals,
        el("div", { class: "actions" },
          el("button", { class: "act primary", text: "Retourner en sécurité", onclick: () => { close(); opts.onBack && opts.onBack(); } }),
          el("button", { class: "act", text: "Continuer malgré le risque", onclick: () => { close(); opts.onContinue && opts.onContinue(); } })
        )
      )
    );
    const overlay = el("div", { class: "overlay", onclick: (e) => { if (e.target.classList.contains("overlay")) close(); } }, modal);
    shadow.appendChild(overlay);
    function close() { const h = document.getElementById(HOST_ID); if (h) h.remove(); }
    return { close };
  }

  // Communication avec le service worker.
  function analyse(payload) {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ kind: "ANALYSE", payload }, (resp) => {
        if (chrome.runtime.lastError || !resp || !resp.ok) return resolve({ verdict: "unknown", signals: [], recommendation: "Analyse indisponible.", remoteAvailable: false });
        resolve(resp.data);
      });
    });
  }
  function report(input) {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ kind: "REPORT", input }, (resp) => resolve(resp && resp.ok ? resp.data : { ok: false }));
    });
  }

  // Indicateur flottant discret (chip) — WhatsApp/Gmail. Hôte Shadow DOM dédié.
  const CHIP_ID = "trustline-chip-host";
  function indicator({ verdict = "suspicious", text, onClick }) {
    const tone = TONE[verdict] || TONE.suspicious;
    let host = document.getElementById(CHIP_ID);
    if (host) host.remove();
    host = document.createElement("div");
    host.id = CHIP_ID;
    host.setAttribute("style", "all: initial; position: fixed; z-index: 2147483646;");
    document.documentElement.appendChild(host);
    const shadow = host.attachShadow({ mode: "open" });
    shadow.appendChild(el("style", { text: BASE_CSS + `
      .chip { position: fixed; bottom: 20px; right: 20px; display:flex; align-items:center; gap:8px;
        background:#fff; border:1px solid #e6eaf0; border-radius:999px; padding:8px 14px 8px 10px;
        box-shadow:0 8px 28px -10px rgba(17,24,39,.3); cursor:pointer; font-size:13px; font-weight:600; color:#111827; }
      .chip:hover { background:#f7f8fa; }
      .dot { width:8px; height:8px; border-radius:50%; }
    ` }));
    const chip = el("div", { class: "chip reveal", role: "button", tabindex: "0",
      onclick: () => onClick && onClick(),
      onkeydown: (e) => { if (e.key === "Enter" || e.key === " ") onClick && onClick(); },
    },
      el("span", { class: "dot", style: `background:${tone.fg};` }),
      logo(),
      el("span", { text })
    );
    shadow.appendChild(chip);
    return { close: () => { const h = document.getElementById(CHIP_ID); if (h) h.remove(); } };
  }

  TL.ui = { panel, warningBeforeNav, indicator, TONE };
  TL.analyse = analyse;
  TL.report = report;
})();
