// Moteur de décision — agrège les signaux locaux en un verdict explicable, et
// combine avec le moteur backend. Règle d'or (§30/§50) : jamais de condamnation
// sur un signal faible isolé ; la décision est toujours explicable.
import { analyserUrlLocal } from "./url.js";
import { analyserMessageLocal } from "./message.js";
import { VERDICT, verdictFromScore, verdictFromBackend, VERDICT_LABEL } from "../lib/verdict.js";

const RECO = {
  safe: "Aucun signal connu. Restez toutefois attentif si la demande évolue.",
  low: "Quelques éléments à surveiller. Ne communiquez rien de sensible dans l'urgence.",
  suspicious: "Plusieurs signaux suspects. Vérifiez auprès du service officiel avant d'agir.",
  high: "Ne payez pas, ne communiquez aucun code, n'ouvrez pas le lien. Signalez ce contenu.",
  unknown: "Analyse incomplète — vérifiez par un autre canal avant d'agir.",
};

function scoreDepuisSignaux(signals) {
  const utiles = signals.filter((s) => s.weight > 0);
  if (utiles.length === 0) return 0;
  const somme = utiles.reduce((t, s) => t + s.weight, 0);
  // Un unique signal faible ne peut pas à lui seul faire basculer en risque élevé.
  if (utiles.length === 1 && utiles[0].weight < 35) return Math.min(utiles[0].weight, 25);
  return Math.min(somme, 100);
}

/** Analyse locale seule (rapide, privacy-friendly, hors-ligne). */
export function analyseLocale({ type, content }) {
  const { signals, meta } =
    type === "url" ? analyserUrlLocal(content) : analyserMessageLocal(content);
  const score = scoreDepuisSignaux(signals);
  const verdict = verdictFromScore(score);
  return {
    verdict,
    score,
    signals: signals.map(({ code, label }) => ({ code, label })),
    explanation:
      signals.length === 0
        ? "Aucun signal d'arnaque connu détecté localement."
        : `${signals.length} signal${signals.length > 1 ? "aux" : ""} détecté${signals.length > 1 ? "s" : ""} localement.`,
    recommendation: RECO[verdict],
    source: "local",
    meta,
    remoteAvailable: false,
  };
}

/**
 * Combine l'analyse locale et la réponse backend.
 * @param {object} local  résultat de analyseLocale
 * @param {object|null} backend  réponse backend normalisée { niveau_risque, score, indices, recommandation } ou null
 */
export function combiner(local, backend) {
  if (backend && backend.niveau_risque) {
    const verdict = verdictFromBackend(backend.niveau_risque);
    // Signaux backend + signaux locaux non redondants (enrichissement).
    const backendSignals = (backend.indices || []).map((label, i) => ({ code: `srv_${i}`, label }));
    const merged = [...backendSignals];
    for (const s of local.signals) if (!merged.some((m) => m.label === s.label)) merged.push(s);
    return {
      verdict,
      score: typeof backend.score === "number" ? backend.score : local.score,
      signals: merged,
      explanation: `${merged.length} signal${merged.length > 1 ? "aux" : ""} pris en compte.`,
      recommendation: backend.recommandation || RECO[verdict],
      source: "trustline",
      meta: local.meta,
      remoteAvailable: true,
    };
  }

  // Backend indisponible : ne JAMAIS affirmer "sûr" (§20/§31).
  if (local.signals.length === 0) {
    return {
      verdict: VERDICT.UNKNOWN,
      score: 0,
      signals: [],
      explanation: "La vérification distante est indisponible et aucun signal local n'a été trouvé.",
      recommendation: RECO.unknown,
      source: "local",
      meta: local.meta,
      remoteAvailable: false,
    };
  }
  return {
    ...local,
    explanation: `${local.explanation} Vérification distante indisponible.`,
  };
}

export { VERDICT, VERDICT_LABEL };
