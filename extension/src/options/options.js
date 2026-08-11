const OPTIONS = [
  { key: "protectionAuto", t: "Protection automatique", d: "Pré-scan des liens et badge de navigation." },
  { key: "analyserLiens", t: "Analyser les liens", d: "Avertir avant d'ouvrir un lien à risque." },
  { key: "whatsapp", t: "WhatsApp Web", d: "Repérer les messages suspects, à la demande." },
  { key: "gmail", t: "Gmail", d: "Indiquer les emails présentant des signaux de phishing." },
  { key: "outlook", t: "Outlook Web", d: "Même protection pour Outlook (best-effort)." },
  { key: "notifications", t: "Notifications", d: "Alerter uniquement en cas de risque élevé." },
  { key: "historiqueLocal", t: "Historique local", d: "Conserver un historique d'analyses sur cet appareil." },
];

function sendSW(message) {
  return new Promise((resolve) => chrome.runtime.sendMessage(message, (r) => resolve(chrome.runtime.lastError ? null : r)));
}

function render(settings) {
  const root = document.getElementById("opts");
  root.textContent = "";
  for (const o of OPTIONS) {
    const label = document.createElement("label");
    label.className = "switch";
    const input = document.createElement("input");
    input.type = "checkbox";
    input.checked = !!settings[o.key];
    input.addEventListener("change", async () => {
      await sendSW({ kind: "SET_SETTINGS", patch: { [o.key]: input.checked } });
    });
    const slider = document.createElement("span");
    slider.className = "slider";
    label.append(input, slider);

    const text = document.createElement("div");
    const t = document.createElement("div"); t.className = "t"; t.textContent = o.t;
    const d = document.createElement("div"); d.className = "d"; d.textContent = o.d;
    text.append(t, d);

    const row = document.createElement("div");
    row.className = "opt";
    row.append(text, label);
    root.appendChild(row);
  }
}

document.getElementById("clear-all").addEventListener("click", async () => {
  if (!window.confirm("Effacer tous les réglages et l'historique local de TrustLine ?")) return;
  await sendSW({ kind: "CLEAR_ALL" });
  const resp = await sendSW({ kind: "GET_SETTINGS" });
  if (resp && resp.ok) render(resp.data);
  window.alert("Données locales effacées.");
});

(async () => {
  const resp = await sendSW({ kind: "GET_SETTINGS" });
  render(resp && resp.ok ? resp.data : {});
})();
