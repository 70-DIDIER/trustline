// Outlook Web — même logique que Gmail via l'abstraction MailProvider
// (TL.selectors.outlook). Les sélecteurs Outlook sont "best-effort" : si le DOM
// diffère, l'intégration échoue proprement sans rien casser (§35/§70).
(function () {
  "use strict";
  const TL = window.TL;
  if (!TL || !TL.selectors) return;
  const provider = TL.selectors.outlook;

  let settings = { outlook: true, protectionAuto: true };
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
    if (!settings.outlook) return;
    let sujet, expediteur, corps;
    try {
      if (!provider.isOpenEmail()) return;
      sujet = provider.findEmailSubject();
      expediteur = provider.findEmailSender();
      corps = provider.findEmailBodyText();
    } catch { return; }

    const cle = `${expediteur}::${sujet}`;
    if (vus.has(cle) || !corps || corps.length < 5) return;
    vus.add(cle);

    const texte = `${sujet}\n${corps}`.slice(0, 4000);
    dernierEmail = { texte, expediteur };
    const r = await localAnalyse(texte);
    if (["high", "suspicious", "low"].includes(r.verdict)) {
      if (chip) chip.close();
      chip = TL.ui.indicator({ verdict: r.verdict, text: r.verdict === "low" ? "Email vérifié" : "Email à vérifier", onClick: analyser });
    }
  }

  async function analyser() {
    if (!dernierEmail) return;
    const { texte, expediteur } = dernierEmail;
    const result = await TL.analyse({ type: "email", content: texte, context: "outlook" });
    TL.ui.panel(result, {
      targetLabel: expediteur ? `Expéditeur : ${expediteur}` : "Email analysé",
      onReport: () => {
        if (!window.confirm("Transmettre cet email à TrustLine pour contribuer à la détection ?")) return;
        TL.report({ type_cible: "message", cible: texte, categorie: "phishing" }).then((res) =>
          window.alert(res && res.ok ? "Merci. Votre signalement contribue à protéger la communauté." : "Signalement impossible pour le moment.")
        );
      },
    });
  }

  let pending = false;
  const obs = new MutationObserver(() => {
    if (pending) return;
    pending = true;
    setTimeout(() => { pending = false; scan(); }, 1600);
  });

  chrome.runtime.sendMessage({ kind: "GET_SETTINGS" }, (resp) => {
    if (resp?.ok) settings = resp.data;
    if (!settings.outlook || !settings.protectionAuto) return;
    setTimeout(scan, 2200);
    try { obs.observe(document.body, { childList: true, subtree: true }); } catch {}
  });
})();
