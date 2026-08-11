// Détection LOCALE de message/email — signaux textuels explicables.
// Pur (testable Node). N'affirme jamais une arnaque sur un seul signal.

// Normalisation robuste : minuscules, accents retirés, espaces spéciaux neutralisés.
export function normaliser(texte) {
  return String(texte || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[ ​‌‍]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

const REGLES = [
  { code: "demande_code", label: "Demande d'un code personnel (OTP / PIN / mot de passe)", weight: 40,
    // Bidirectionnel : « code … envoyez » OU « envoyez … code » (phrasé réel des arnaques).
    re: /(\b(code|pin|otp|mot de passe|code secret)\b.{0,40}\b(envoy|donn|communiqu|partag|confirm))|(\b(envoy|donn|communiqu|partag|confirm|transmet|saisiss)\w*\b.{0,25}\b(code|pin|otp|mot de passe)\b)/ },
  { code: "urgence", label: "Urgence artificielle", weight: 20,
    re: /\b(urgent|immediatement|dans les \d+ ?(min|h|heures)|expire|dernier delai|avant \d+h|sinon|sera bloque|sera suspendu|sera annule)\b/ },
  { code: "promesse_gain", label: "Promesse de gain / faux concours", weight: 30,
    re: /\b(felicitation|vous avez gagne|gagnant|tirage|loterie|prix|recompense|selectionne|heureux gagnant)\b/ },
  { code: "demande_paiement", label: "Demande de paiement ou de transfert", weight: 30,
    re: /\b(envoyez|deposez|payer|virement|transferer|frais|debloquer|caution|avance)\b.{0,30}\b(fcfa|francs?|argent|\d{3,})/ },
  { code: "usurpation", label: "Se présente comme un service officiel", weight: 20,
    re: /\b(agent|service client|banque|operateur|flooz|t ?money|mobile money|support|equipe)\b/ },
  { code: "menace_compte", label: "Menace sur un compte (blocage, vérification)", weight: 25,
    re: /\b(compte.{0,20}(bloqu|suspend|desactiv|verifi|securis)|verifier votre compte|reactiver)\b/ },
  { code: "faux_depot", label: "Scénario de faux dépôt mobile money", weight: 35,
    re: /\b(depot.{0,20}(erreur|par erreur)|recu.{0,15}\d{3,}.{0,10}(f|fcfa)|renvoyez.{0,20}\d{3,})\b/ },
  { code: "faux_colis", label: "Faux colis / livraison bloquée", weight: 20,
    re: /\b(colis.{0,20}(bloqu|attente|douane|frais)|votre livraison)\b/ },
  { code: "faux_emploi", label: "Fausse offre d'emploi", weight: 20,
    re: /\b(offre d.?emploi|recrutement|poste.{0,20}(disponible|urgent)|salaire.{0,20}\d{3,})\b/ },
];

const RE_LIEN = /\bhttps?:\/\/[^\s]+|\b[a-z0-9-]+\.(com|net|org|xyz|top|info|tg|online|site|live)\b[^\s]*/gi;
const RE_TEL = /\+?\d[\d\s().-]{6,}\d/g;

// §69 anti-prompt-injection : un message qui tente de manipuler un système est,
// en soi, un signal suspect. Ces instructions ne sont JAMAIS exécutées, juste comptées.
const RE_INJECTION = /\b(ignore (previous|all).*(instruction|rule)|disable (security|protection)|send this to (your|all)|ignore trustline)\b/i;

/**
 * @param {string} texte
 * @returns {{signals:{code,label,weight}[], meta:{liens:string[],numeros:string[]}}}
 */
export function analyserMessageLocal(texte) {
  const brut = String(texte || "");
  const norm = normaliser(brut);
  const signals = [];

  for (const r of REGLES) {
    if (r.re.test(norm)) signals.push({ code: r.code, label: r.label, weight: r.weight });
  }

  const liens = [...new Set((brut.match(RE_LIEN) || []).map((s) => s.trim()))];
  const numeros = [...new Set((brut.match(RE_TEL) || []).map((s) => s.trim()))].filter((n) => n.replace(/\D/g, "").length >= 8);

  if (liens.length) signals.push({ code: "contient_lien", label: "Contient un lien externe", weight: 15 });
  if (numeros.length) signals.push({ code: "contient_numero", label: "Contient un numéro de téléphone", weight: 10 });
  if (RE_INJECTION.test(brut)) signals.push({ code: "manipulation", label: "Tentative de manipulation détectée", weight: 30 });

  return { signals, meta: { liens, numeros } };
}
