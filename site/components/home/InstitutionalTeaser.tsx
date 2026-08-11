import { Reveal } from "@/components/ui/Reveal";
import { INSTITUTIONS } from "@/lib/content/institutions";

export function InstitutionalTeaser() {
  return (
    <section className="mx-auto max-w-content px-5 py-20 sm:px-8 sm:py-24">
      <Reveal className="grid grid-cols-1 gap-8 lg:grid-cols-12 lg:items-baseline">
        <h2 className="text-display-sm font-bold text-body lg:col-span-4">
          Besoin d&apos;aller plus loin ?
        </h2>
        <div className="flex flex-col gap-4 lg:col-span-7 lg:col-start-6">
          {INSTITUTIONS.map((i) => (
            <a
              key={i.href}
              href={i.href}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-baseline justify-between gap-4 border-b border-base pb-4 transition-colors hover:border-strong"
            >
              <span>
                <span className="text-sm font-semibold text-body">{i.label}</span>
                <span className="ml-2 text-xs text-muted">{i.desc}</span>
              </span>
              <span className="flex-none text-sm text-brand">↗</span>
            </a>
          ))}
          <p className="text-xs text-muted">
            Ressources institutionnelles — TrustLine n&apos;est affilié à aucun de ces organismes.
          </p>
        </div>
      </Reveal>
    </section>
  );
}
