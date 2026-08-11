// WhatsApp Web — détection PASSIVE des messages visibles suspects, puis analyse
// à la demande. Ne scanne jamais silencieusement toutes les conversations, ne
// modifie pas les bulles de WhatsApp, n'envoie rien sans action de l'utilisateur.
(function () {
  "use strict";
  const TL = window.TL;
  if (!TL || !TL.selectors) return;

  let settings = { whatsapp: true, protectionAuto: true };
  let dernierSuspect = null; // texte du dernier message flaggé
  const vus = new Set(); // hash de messages déjà analysés (dédup)
  let chip = null;

  function hash(s) { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return h; }

  function localAnalyse(text) {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ kind: "ANALYSE_LOCAL", payload: { type: "message", content: text } }, (resp) => {
        resolve(chrome.runtime.lastError || !resp?.ok ? { verdict: "unknown" } : resp.data);
      });
    });
  }

  async function scan() {
    if (!settings.whatsapp) return;
    let messages;
    try { messages = TL.selectors.whatsapp.findVisibleMessages(); }
    catch { return; } // DOM WhatsApp modifié -> échec propre (§70)
    let flagged = 0;
    for (const node of messages.slice(-30)) {
      const text = TL.selectors.whatsapp.messageText(node);
      const h = hash(text);
      if (vus.has(h)) { if (node.__tlFlag) flagged++; continue; }
      vus.add(h);
      const r = await localAnalyse(text);
      if (r.verdict === "high" || r.verdict === "suspicious") {
        node.__tlFlag = true;
        dernierSuspect = text;
        flagged++;
      }
    }
    if (flagged > 0 && dernierSuspect) {
      if (chip) chip.close();
      chip = TL.ui.indicator({
        verdict: "high",
        text: `${flagged} message${flagged > 1 ? "s" : ""} à vérifier`,
        onClick: analyserDernier,
      });
    }
  }

  async function analyserDernier() {
    if (!dernierSuspect) return;
    const texte = dernierSuspect;
    const result = await TL.analyse({ type: "message", content: texte, context: "whatsapp" });
    TL.ui.panel(result, {
      targetLabel: "Message WhatsApp analysé",
      onReport: () => {
        const ok = window.confirm("Transmettre ce message à TrustLine pour contribuer à la détection ?\n\nSeul le contenu du message est envoyé, de façon anonyme.");
        if (!ok) return;
        TL.report({ type_cible: "message", cible: texte, categorie: "autre" }).then((res) => {
          window.alert(res && res.ok ? "Merci. Votre signalement contribue à protéger la communauté." : "Signalement impossible pour le moment.");
        });
      },
    });
  }

  let pending = false;
  const obs = new MutationObserver(() => {
    if (pending) return;
    pending = true;
    setTimeout(() => { pending = false; scan(); }, 2000); // throttling
  });

  chrome.runtime.sendMessage({ kind: "GET_SETTINGS" }, (resp) => {
    if (resp?.ok) settings = resp.data;
    if (!settings.whatsapp || !settings.protectionAuto) return;
    setTimeout(scan, 2500);
    try { obs.observe(document.body, { childList: true, subtree: true }); } catch {}
  });
})();
