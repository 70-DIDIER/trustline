import { VerificationBox } from "@/components/verification/VerificationBox";
import { Reveal } from "@/components/ui/Reveal";

export function LiveDemo() {
  return (
    <section className="border-b border-base bg-app">
      <div className="mx-auto max-w-content px-5 py-24 sm:px-8 sm:py-32">
      <div className="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:items-center">
        <Reveal className="lg:col-span-5">
          <span className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-muted">
            Essayez
          </span>
          <h2 className="text-display-sm mt-4 font-bold text-body">
            Voyez ce que TrustLine détecte.
          </h2>
          <p className="mt-5 max-w-md text-base leading-relaxed text-secondary">
            Collez un vrai numéro, un lien ou un message. L&apos;analyse ci-contre est réelle —
            c&apos;est exactement le moteur utilisé partout dans TrustLine.
          </p>
          <ul className="mt-8 flex flex-col gap-3 text-sm text-secondary">
            <li className="flex items-center gap-3">
              <span className="h-1 w-6 rounded-full bg-[var(--color-success)]" />
              Aucun compte, aucune donnée conservée pour un simple test
            </li>
            <li className="flex items-center gap-3">
              <span className="h-1 w-6 rounded-full bg-[var(--color-primary)]" />
              Détection automatique du type (numéro, lien, message)
            </li>
          </ul>
        </Reveal>

        <Reveal delay={120} className="lg:col-span-7">
          <VerificationBox />
        </Reveal>
      </div>
      </div>
    </section>
  );
}
