// Protection web générique — pré-scan LOCAL des liens visibles, et avertissement
// avant navigation UNIQUEMENT sur les liens à risque (n'intercepte jamais un lien
// sûr : ne casse pas la navigation normale du site, §36).
(function () {
  "use strict";
  const TL = window.TL;
  if (!TL || !TL.selectors) return;

  let settings = { analyserLiens: true, protectionAuto: true };
  const analysedHosts = new Map(); // host -> verdict local
  const risky = new WeakSet(); // ancres à risque déjà repérées

  function localAnalyse(url) {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ kind: "ANALYSE_LOCAL", payload: { type: "url", content: url } }, (resp) => {
        resolve(chrome.runtime.lastError || !resp?.ok ? { verdict: "unknown", signals: [], meta: {} } : resp.data);
      });
    });
  }

  async function scan() {
    if (!settings.analyserLiens) return;
    let anchors;
    try {
      anchors = TL.selectors.web.findVisibleLinks().slice(0, 50);
    } catch {
      return; // DOM inattendu : échec silencieux, on ne casse rien
    }
    for (const a of anchors) {
      let host;
      try { host = new URL(a.href).host; } catch { continue; }
      if (analysedHosts.has(host)) {
        if (["high", "suspicious"].includes(analysedHosts.get(host))) risky.add(a);
        continue;
      }
      const r = await localAnalyse(a.href);
      analysedHosts.set(host, r.verdict);
      if (["high", "suspicious"].includes(r.verdict)) risky.add(a);
    }
  }

  // Interception : uniquement sur les liens repérés à risque.
  document.addEventListener(
    "click",
    async (e) => {
      const a = e.target && e.target.closest ? e.target.closest('a[href^="http"]') : null;
      if (!a || !risky.has(a)) return;
      e.preventDefault();
      e.stopPropagation();
      const full = await TL.analyse({ type: "url", content: a.href, context: "web" });
      if (full.verdict === "safe" || full.verdict === "low") {
        window.location.href = a.href; // finalement sans risque -> on laisse passer
        return;
      }
      let domain = "";
      try { domain = new URL(a.href).host; } catch {}
      TL.ui.warningBeforeNav(full, {
        domain,
        onContinue: () => { window.location.href = a.href; },
        onBack: () => {},
      });
    },
    true
  );

  // MutationObserver throttlé — WhatsApp/Gmail sont dynamiques, le web aussi.
  let pending = false;
  const obs = new MutationObserver(() => {
    if (pending) return;
    pending = true;
    setTimeout(() => { pending = false; scan(); }, 1500);
  });

  chrome.runtime.sendMessage({ kind: "GET_SETTINGS" }, (resp) => {
    if (resp?.ok) settings = resp.data;
    if (!settings.protectionAuto) return;
    scan();
    try { obs.observe(document.body, { childList: true, subtree: true }); } catch {}
  });
})();
