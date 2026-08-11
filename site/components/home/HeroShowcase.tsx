import { RiskBadge } from "@/components/ui/RiskBadge";

// Vitrine produit du hero — une carte de résultat d'analyse crédible (état statique
// représentatif de ce que renvoie réellement l'API pour un numéro sûr). L'outil
// réellement interactif vit plus bas dans la page et sur /verifier.
const SIGNAUX = [
  { texte: "Aucun signalement communautaire", ok: true },
  { texte: "Format et opérateur reconnus", ok: true },
  { texte: "Absent des listes de menaces", ok: true },
];

export function HeroShowcase() {
  return (
    <div className="relative">
      <div className="rounded-lg border border-base bg-app shadow-elevated">
        {/* En-tête du panneau */}
        <div className="flex items-center justify-between border-b border-base px-5 py-3.5">
          <div className="flex items-center gap-2">
            <span className="grid h-6 w-6 place-items-center rounded-md bg-[var(--color-primary-light)]">
              <svg viewBox="0 0 20 20" fill="none" className="h-3.5 w-3.5 text-brand">
                <path d="M10 2.5l6 2.2v4.4c0 3.7-2.5 6.7-6 7.6-3.5-.9-6-3.9-6-7.6V4.7l6-2.2Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
              </svg>
            </span>
            <span className="text-sm font-semibold text-body">Analyse TrustLine</span>
          </div>
          <span className="font-mono text-[0.68rem] text-muted">312 ms</span>
        </div>

        {/* Cible analysée */}
        <div className="px-5 pt-5">
          <p className="text-[0.68rem] font-semibold uppercase tracking-wide text-muted">Numéro analysé</p>
          <p className="mt-1 font-mono text-lg text-body">+228 90 •• •• 12</p>
        </div>

        {/* Verdict */}
        <div className="mx-5 mt-4 flex items-center justify-between rounded-md border border-[color-mix(in_srgb,var(--color-success)_30%,transparent)] bg-[var(--color-success-light)] px-4 py-3">
          <div className="flex items-center gap-2.5">
            <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5 text-safe">
              <path d="M12 3l7 3v5.2c0 4.4-3 8-7 9-4-1-7-4.6-7-9V6l7-3Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
              <path d="M8.8 12.1l2.2 2.2 4.2-4.7" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span className="text-[0.95rem] font-bold text-safe">Faible risque</span>
          </div>
          <span className="font-mono text-sm text-safe tabular-nums">9<span className="opacity-60">/100</span></span>
        </div>

        {/* Signaux */}
        <div className="px-5 pt-4">
          <p className="text-[0.68rem] font-semibold uppercase tracking-wide text-muted">Signaux vérifiés</p>
          <ul className="mt-2.5 flex flex-col gap-2">
            {SIGNAUX.map((s) => (
              <li key={s.texte} className="flex items-center gap-2.5 text-sm text-secondary">
                <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5 flex-none text-safe">
                  <path d="M3.5 8.2l2.7 2.7 6.3-6.6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                {s.texte}
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-5 border-t border-base px-5 py-3.5">
          <p className="text-xs text-muted">
            Recommandation — vous pouvez répondre, mais restez attentif si la demande évolue.
          </p>
        </div>
      </div>

      {/* Micro-labels flottants — très subtils, desktop seulement */}
      <div className="absolute -right-4 -top-4 hidden items-center gap-1.5 rounded-full border border-base bg-app px-3 py-1.5 shadow-soft lg:flex">
        <RiskBadge niveau="faible" size="sm" />
      </div>
      <div className="absolute -bottom-4 left-8 hidden items-center gap-1.5 rounded-full border border-base bg-app px-3 py-1.5 text-xs font-medium text-secondary shadow-soft lg:flex">
        <span className="h-1.5 w-1.5 rounded-full bg-[var(--color-success)]" />
        Analyse instantanée
      </div>
    </div>
  );
}
