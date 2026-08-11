import type { Metadata } from "next";
import Link from "next/link";
import { EducationCard } from "@/components/education/EducationCard";
import { FICHES, REFLEXES } from "@/lib/content/fiches";

export const metadata: Metadata = {
  title: "Apprendre",
  description: "Reconnaître une arnaque avant qu'il ne soit trop tard — fiches pédagogiques TrustLine.",
};

export default function ApprendrePage() {
  return (
    <main>
      <div className="mx-auto max-w-content px-5 py-16 sm:px-8 sm:py-24">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
          <h1 className="text-display-sm font-bold text-body lg:col-span-7">
            Reconnaître une arnaque avant qu&apos;il ne soit trop tard.
          </h1>
          <p className="text-sm leading-relaxed text-secondary lg:col-span-4 lg:col-start-9">
            Sept schémas récurrents observés au Togo, et le réflexe qui les arrête à chaque
            fois : vérifier avant d&apos;agir.
          </p>
        </div>

        <div className="mt-14 grid grid-cols-1 gap-10 lg:grid-cols-12 lg:gap-12">
          <div className="grid gap-3 lg:col-span-7">
            {FICHES.map((f) => (
              <EducationCard key={f.titre} fiche={f} />
            ))}
          </div>

          <aside className="lg:col-span-5">
            <div className="lg:sticky lg:top-24">
              <div className="rounded-lg border border-base bg-surface-alt p-6 sm:p-7">
                <span className="font-mono text-xs font-semibold uppercase tracking-[0.14em] text-muted">
                  Le fil rouge
                </span>
                <h2 className="mt-3 text-lg font-bold leading-snug text-body">
                  Des scénarios différents, un seul réflexe.
                </h2>
                <p className="mt-3 text-sm leading-relaxed text-secondary">
                  Peu importe l&apos;histoire — dépôt, gain, colis, emploi — la parade est
                  identique&nbsp;: ne rien décider dans l&apos;urgence, vérifier la source, et ne
                  jamais communiquer un code reçu par SMS.
                </p>
                <div className="mt-6 flex flex-wrap gap-3">
                  <Link
                    href="/verifier"
                    className="inline-flex items-center justify-center rounded-sm bg-brand px-4 py-2.5 text-sm font-semibold text-on-brand transition-colors hover:bg-[var(--color-primary-hover)]"
                  >
                    Vérifier un message
                  </Link>
                  <Link
                    href="/signaler"
                    className="inline-flex items-center gap-1.5 rounded-sm border border-strong px-4 py-2.5 text-sm font-semibold text-body transition-colors hover:border-[var(--color-primary)] hover:text-brand"
                  >
                    Signaler
                  </Link>
                </div>
              </div>
            </div>
          </aside>
        </div>
      </div>

      <div className="border-t border-base bg-surface-alt">
        <div className="mx-auto max-w-content px-5 py-16 sm:px-8 sm:py-20">
          <h2 className="text-display-sm font-bold text-body">Les 5 réflexes à retenir</h2>
          <ol className="mt-10 grid gap-8 sm:grid-cols-5">
            {REFLEXES.map((r, i) => (
              <li key={r} className="border-t-2 border-brand pt-4">
                <span className="font-mono text-xs text-muted">{String(i + 1).padStart(2, "0")}</span>
                <p className="mt-1.5 text-sm font-semibold text-body">{r}</p>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </main>
  );
}
