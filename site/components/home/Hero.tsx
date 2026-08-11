import Link from "next/link";
import { HeroShowcase } from "./HeroShowcase";

export function Hero() {
  return (
    <header className="bg-ground">
      <div className="mx-auto grid max-w-content grid-cols-1 gap-14 px-5 py-20 sm:px-8 lg:grid-cols-12 lg:items-center lg:gap-10 lg:py-28">
        <div className="lg:col-span-6">
          <span className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-muted">
            Protection numérique · Togo
          </span>
          <h1 className="text-display-md mt-6 font-bold tracking-tight text-body">
            Avant de faire confiance,
            <br />
            <span className="text-brand">vérifiez.</span>
          </h1>
          <p className="mt-6 max-w-md text-lg leading-relaxed text-secondary">
            TrustLine vous aide à vérifier un numéro, un lien ou un message suspect avant
            d&apos;agir.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-5">
            <Link
              href="/verifier"
              className="inline-flex items-center justify-center rounded-sm bg-brand px-5 py-3 text-sm font-semibold text-on-brand transition-colors hover:bg-[var(--color-primary-hover)]"
            >
              Vérifier maintenant
            </Link>
            <Link
              href="/signaler"
              className="group inline-flex items-center gap-1.5 text-sm font-semibold text-body transition-colors hover:text-brand"
            >
              Signaler une arnaque
              <svg viewBox="0 0 16 16" fill="none" className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </Link>
          </div>
        </div>

        <div className="lg:col-span-6">
          <HeroShowcase />
        </div>
      </div>
    </header>
  );
}
