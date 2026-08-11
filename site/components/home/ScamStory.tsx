import { Reveal } from "@/components/ui/Reveal";

const SIGNAUX = [
  "Promesse financière non sollicitée",
  "Urgence artificielle (« confirmez maintenant »)",
  "Demande d'un code personnel",
  "Numéro court non officiel",
];

export function ScamStory() {
  return (
    <section className="border-b border-base bg-app">
      <div className="mx-auto max-w-content px-5 py-24 sm:px-8 sm:py-32">
      <Reveal className="max-w-2xl">
        <span className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-muted">
          Anatomie d&apos;une arnaque
        </span>
        <h2 className="text-display-sm mt-4 font-bold leading-[1.15] text-body">
          Une arnaque commence souvent par quelque chose qui semble normal.
        </h2>
      </Reveal>

      <div className="mt-14 grid grid-cols-1 gap-6 lg:grid-cols-12 lg:items-center lg:gap-10">
        {/* Le message reçu */}
        <Reveal className="lg:col-span-6">
          <div className="rounded-lg bg-surface p-6 sm:p-8">
            <p className="mb-4 flex items-center gap-2 text-xs text-muted">
              <span className="grid h-6 w-6 place-items-center rounded-full bg-surface-2 font-mono text-[0.6rem] text-secondary">
                SMS
              </span>
              Reçu · aujourd&apos;hui, 09:14
            </p>
            <div className="max-w-sm rounded-lg rounded-tl-none border border-base bg-app p-4 text-[0.95rem] leading-relaxed text-body">
              Felicitations ! Vous avez ete selectionne pour recevoir 500 000 FCFA. Confirmez
              votre gain avec votre code recu par SMS avant 12h, sinon il sera annule.
            </div>
          </div>
        </Reveal>

        {/* Ce que TrustLine en fait */}
        <Reveal delay={120} className="lg:col-span-6">
          <div className="rounded-lg border border-base bg-app p-6 shadow-soft sm:p-8">
            <div className="flex items-center justify-between">
              <span className="inline-flex items-center gap-2 rounded-full bg-danger-soft px-3 py-1 text-xs font-bold uppercase tracking-wide">
                <span className="h-1.5 w-1.5 rounded-full bg-[var(--color-danger)]" />
                Risque élevé
              </span>
              <span className="font-mono text-sm text-danger tabular-nums">92<span className="opacity-60">/100</span></span>
            </div>

            <p className="mt-5 text-[0.68rem] font-semibold uppercase tracking-wide text-muted">
              Signaux détectés
            </p>
            <ul className="mt-3 flex flex-col gap-2.5">
              {SIGNAUX.map((s) => (
                <li key={s} className="flex items-start gap-2.5 text-sm text-body">
                  <svg viewBox="0 0 16 16" fill="none" className="mt-0.5 h-3.5 w-3.5 flex-none text-danger">
                    <path d="M8 1.5l6.5 11.5h-13L8 1.5Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
                    <path d="M8 6v3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
                    <circle cx="8" cy="11" r="0.7" fill="currentColor" />
                  </svg>
                  {s}
                </li>
              ))}
            </ul>

            <p className="mt-6 border-t border-base pt-4 text-sm text-secondary">
              Ne communiquez aucun code. Aucun gain légitime n&apos;exige de payer ou de
              confirmer un code pour être versé.
            </p>
          </div>
        </Reveal>
      </div>
      </div>
    </section>
  );
}
