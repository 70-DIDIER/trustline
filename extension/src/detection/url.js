// Détection LOCALE d'URL — heuristiques rapides, déterministes, explicables.
// Aucune dépendance chrome : testable sous Node. Ne condamne jamais sur un seul
// signal faible (voir engine.js qui agrège).

// Marques togolaises couramment usurpées (pour repérer les typosquats).
const MARQUES = ["ecobank", "orabank", "uba", "boa", "coris", "togocom", "moov", "flooz", "tmoney", "yas", "canalbox"];
const RACCOURCISSEURS = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly", "rb.gy", "shorturl.at"];
const MOTS_CHEMIN = ["login", "signin", "verify", "verifier", "secure", "confirmer", "account", "compte", "gagner", "gain", "recompense", "password", "motdepasse"];

function distanceProche(a, b) {
  // Distance de Levenshtein bornée — pour détecter un domaine "presque" une marque.
  const m = a.length, n = b.length;
  if (Math.abs(m - n) > 2) return 99;
  const dp = Array.from({ length: m + 1 }, (_, i) => [i, ...Array(n).fill(0)]);
  for (let j = 0; j <= n; j++) dp[0][j] = j;
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      dp[i][j] = Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return dp[m][n];
}

/**
 * @param {string} urlBrute
 * @returns {{signals: {code:string,label:string,weight:number}[], meta:{domaine:string,url:string}}}
 */
export function analyserUrlLocal(urlBrute) {
  const signals = [];
  let url;
  const brute = String(urlBrute || "").trim();
  const avecSchema = /^https?:\/\//i.test(brute) ? brute : `http://${brute}`;
  try {
    url = new URL(avecSchema);
  } catch {
    return { signals: [{ code: "url_invalide", label: "Lien non analysable", weight: 0 }], meta: { domaine: "", url: brute } };
  }

  const host = url.hostname.toLowerCase();
  const domaine = host.replace(/^www\./, "");
  const labelDomaine = domaine.split(".").slice(-2, -1)[0] || domaine;

  if (url.protocol === "http:") {
    signals.push({ code: "sans_https", label: "Connexion non sécurisée (http)", weight: 20 });
  }
  if (/^\d{1,3}(\.\d{1,3}){3}$/.test(host)) {
    signals.push({ code: "ip_domaine", label: "Adresse IP utilisée comme domaine", weight: 35 });
  }
  if (host.includes("xn--")) {
    signals.push({ code: "punycode", label: "Caractères internationaux masqués (punycode)", weight: 35 });
  }
  if (url.username || url.password || brute.includes("@")) {
    signals.push({ code: "credentials_url", label: "Identifiants intégrés à l'adresse", weight: 30 });
  }
  const nbSousDomaines = host.split(".").length - 2;
  if (nbSousDomaines >= 3) {
    signals.push({ code: "sous_domaines", label: "Sous-domaines inhabituellement nombreux", weight: 20 });
  }
  if (domaine.length > 30) {
    signals.push({ code: "domaine_long", label: "Nom de domaine anormalement long", weight: 15 });
  }
  if ((labelDomaine.match(/-/g) || []).length >= 3 || /\d{4,}/.test(labelDomaine)) {
    signals.push({ code: "domaine_bruite", label: "Nom de domaine composé de manière suspecte", weight: 15 });
  }
  if (RACCOURCISSEURS.includes(domaine)) {
    signals.push({ code: "raccourci", label: "Lien raccourci (destination masquée)", weight: 25 });
  }
  for (const marque of MARQUES) {
    if (labelDomaine !== marque && labelDomaine.includes(marque) && domaine !== `${marque}.tg`) {
      signals.push({ code: "typosquat", label: `Imite une marque connue (« ${marque} »)`, weight: 40 });
      break;
    }
    if (distanceProche(labelDomaine, marque) === 1 && labelDomaine !== marque) {
      signals.push({ code: "typosquat_proche", label: `Très proche d'une marque connue (« ${marque} »)`, weight: 40 });
      break;
    }
  }
  const chemin = (url.pathname + url.search).toLowerCase();
  const motTrouve = MOTS_CHEMIN.find((m) => chemin.includes(m));
  if (motTrouve) {
    signals.push({ code: "chemin_sensible", label: "Demande une action sensible (connexion, code…)", weight: 15 });
  }

  return { signals, meta: { domaine, url: url.href } };
}
