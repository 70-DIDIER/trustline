import Link from "next/link";
import { Reveal } from "@/components/ui/Reveal";

const CONTEXTES = [
  { label: "WhatsApp", note: "un message d'un inconnu" },
  { label: "Gmail", note: "un lien de « vérification »" },
  { label: "Web", note: "un site marchand douteux" },
];

export function ExtensionSection() {
  return (
    <section className="border-y border-base bg-surface-alt">
      <div className="mx-auto max-w-content px-5 py-24 sm:px-8 sm:py-32">
        <div className="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:items-center">
          <Reveal className="lg:col-span-5">
            <span className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-muted">
              Extension navigateur
            </span>
            <h2 className="text-display-sm mt-4 font-bold leading-[1.15] text-body">
              TrustLine vous accompagne là où les arnaques apparaissent.
            </h2>
            <p className="mt-5 max-w-md text-base leading-relaxed text-secondary">
              Vérifiez un lien ou un site sans quitter votre navigateur. L&apos;extension signale
              les pages frauduleuses avant que vous ne saisissiez la moindre information.
            </p>
            <Link
              href="/telecharger"
              className="mt-8 inline-flex items-center justify-center rounded-sm bg-brand px-5 py-3 text-sm font-semibold text-on-brand transition-colors hover:bg-[var(--color-primary-hover)]"
            >
              Installer l&apos;extension
            </Link>
          </Reveal>

          <Reveal delay={120} className="lg:col-span-6 lg:col-start-7">
            <div className="rounded-lg border border-base bg-app p-4 shadow-elevated sm:p-6">
              <div className="flex flex-col gap-2.5">
                {CONTEXTES.map((c) => (
                  <div key={c.label} className="flex items-center gap-3 rounded-md bg-surface px-4 py-3">
                    <span className="w-20 flex-none text-sm font-semibold text-body">{c.label}</span>
                    <span className="text-sm text-muted">{c.note}</span>
                  </div>
                ))}
              </div>
              <div className="mt-3 flex items-center gap-3 rounded-md border border-[color-mix(in_srgb,var(--color-danger)_35%,transparent)] bg-danger-soft px-4 py-3">
                <svg viewBox="0 0 20 20" fill="none" className="h-5 w-5 flex-none text-danger">
                  <path d="M10 2.5l8 14H2l8-14Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
                  <path d="M10 8v3.2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
                  <circle cx="10" cy="13.8" r="0.9" fill="currentColor" />
                </svg>
                <div>
                  <p className="text-sm font-bold text-danger">Alerte TrustLine</p>
                  <p className="text-xs text-secondary">Ce site présente des signaux d&apos;hameçonnage.</p>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
