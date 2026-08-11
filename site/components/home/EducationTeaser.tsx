import Link from "next/link";
import { Reveal } from "@/components/ui/Reveal";
import { FICHES } from "@/lib/content/fiches";

const APERCU = FICHES.slice(0, 3);

export function EducationTeaser() {
  return (
    <section className="border-b border-base bg-app">
      <div className="mx-auto max-w-content px-5 py-20 sm:px-8 sm:py-28">
        <Reveal className="max-w-2xl">
          <span className="font-mono text-xs font-semibold uppercase tracking-[0.14em] text-muted">
            Apprendre
          </span>
          <h2 className="text-display-sm mt-4 font-bold text-body">
            Reconnaître les signaux avant qu&apos;il ne soit trop tard.
          </h2>
        </Reveal>

        <div className="mt-12 divide-y divide-[var(--border)] border-y border-base">
          {APERCU.map((f, i) => (
            <Reveal key={f.titre} delay={i * 80}>
              <Link
                href="/apprendre"
                className="group grid grid-cols-1 gap-3 py-7 transition-colors sm:grid-cols-12 sm:items-center sm:gap-6"
              >
                <span className="font-mono text-xs text-muted sm:col-span-1">{String(i + 1).padStart(2, "0")}</span>
                <h3 className="text-lg font-bold text-body sm:col-span-3">{f.titre}</h3>
                <p className="text-sm leading-relaxed text-secondary sm:col-span-7">{f.commence}</p>
                <span className="text-sm font-semibold text-brand opacity-0 transition-opacity group-hover:opacity-100 sm:col-span-1 sm:text-right">
                  →
                </span>
              </Link>
            </Reveal>
          ))}
        </div>

        <Link href="/apprendre" className="mt-8 inline-block text-sm font-semibold text-brand hover:underline">
          Toutes les fiches et les 5 réflexes à retenir →
        </Link>
      </div>
    </section>
  );
}
