// Gmail Web — analyse de l'email OUVERT uniquement (jamais toute la boîte).
// Extrait seulement l'expéditeur, l'objet, le corps visible et les liens.
(function () {
  "use strict";
  const TL = window.TL;
  if (!TL || !TL.selectors) return;
  const provider = TL.selectors.gmail;

  let settings = { gmail: true, protectionAuto: true };
  let dernierEmail = null;
  const vus = new Set();
  let chip = null;

  function localAnalyse(text) {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ kind: "ANALYSE_LOCAL", payload: { type: "email", content: text } }, (resp) => {
        resolve(chrome.runtime.lastError || !resp?.ok ? { verdict: "unknown" } : resp.data);
      });
    });
  }

  async function scan() {
    if (!settings.gmail) return;
    let ouvert, sujet, expediteur, corps;
    try {
      ouvert = provider.isOpenEmail();
      if (!ouvert) return;
      sujet = provider.findEmailSubject();
      expediteur = provider.findEmailSender();
      corps = provider.findEmailBodyText();
    } catch { return; } // DOM Gmail modifié -> échec propre

    const cle = `${expediteur}::${sujet}`;
    if (vus.has(cle) || !corps || corps.length < 5) return;
    vus.add(cle);

    const texte = `${sujet}\n${corps}`.slice(0, 4000);
    dernierEmail = { texte, expediteur };
    const r = await localAnalyse(texte);
    if (r.verdict === "high" || r.verdict === "suspicious" || r.verdict === "low") {
      if (chip) chip.close();
      const label = r.verdict === "low" ? "Email vérifié" : "Email à vérifier";
      chip = TL.ui.indicator({ verdict: r.verdict, text: label, onClick: analyser });
    }
  }

  async function analyser() {
    if (!dernierEmail) return;
    const { texte, expediteur } = dernierEmail;
    const result = await TL.analyse({ type: "email", content: texte, context: "gmail" });
    TL.ui.panel(result, {
      targetLabel: expediteur ? `Expéditeur : ${expediteur}` : "Email analysé",
      onReport: () => {
        const ok = window.confirm("Transmettre cet email à TrustLine pour contribuer à la détection ?\n\nSeuls l'objet et le contenu visible sont envoyés, de façon anonyme.");
        if (!ok) return;
        TL.report({ type_cible: "message", cible: texte, categorie: "phishing" }).then((res) => {
          window.alert(res && res.ok ? "Merci. Votre signalement contribue à protéger la communauté." : "Signalement impossible pour le moment.");
        });
      },
    });
  }

  let pending = false;
  const obs = new MutationObserver(() => {
    if (pending) return;
    pending = true;
    setTimeout(() => { pending = false; scan(); }, 1500);
  });

  chrome.runtime.sendMessage({ kind: "GET_SETTINGS" }, (resp) => {
    if (resp?.ok) settings = resp.data;
    if (!settings.gmail || !settings.protectionAuto) return;
    setTimeout(scan, 2000);
    try { obs.observe(document.body, { childList: true, subtree: true }); } catch {}
  });
})();
