import Link from "next/link";
import { Reveal } from "@/components/ui/Reveal";

// Point d'orgue sombre — la seconde inversion (après la bande data) qui
// referme le rythme clair/foncé de la page sur une action unique.
export function FinalCta() {
  return (
    <section className="bg-inverse-grad">
      <Reveal className="mx-auto flex max-w-content flex-col items-center gap-8 px-5 py-24 text-center sm:px-8 sm:py-32">
        <h2 className="text-display-md font-bold text-inverse-text">
          Avant de faire confiance,
          <br />
          vérifiez.
        </h2>
        <Link
          href="/verifier"
          className="inline-flex items-center justify-center rounded-sm bg-brand px-7 py-3.5 text-sm font-semibold text-on-brand transition-colors hover:bg-[var(--color-primary-hover)]"
        >
          Vérifier maintenant
        </Link>
        <div className="mt-6 flex flex-col items-center gap-3 border-t border-inverse pt-8">
          <span className="font-display text-base font-bold text-inverse-text">TrustLine</span>
          <p className="font-mono text-xs uppercase tracking-[0.18em] text-inverse-muted">
            Connecter · Protéger · Assurer
          </p>
        </div>
      </Reveal>
    </section>
  );
}
