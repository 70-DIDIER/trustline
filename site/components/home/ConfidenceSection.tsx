import { Reveal } from "@/components/ui/Reveal";

const POINTS = [
  "Aucune collecte de répertoire téléphonique",
  "Numéros et messages anonymisés avant tout stockage",
  "Signalements utilisés uniquement pour améliorer la détection",
  "Aucune information sensible exposée publiquement",
];

export function ConfidenceSection() {
  return (
    <section className="border-y border-base bg-app">
      <div className="mx-auto max-w-content px-5 py-20 sm:px-8 sm:py-28">
        <Reveal className="grid grid-cols-1 gap-10 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <span className="font-mono text-xs font-semibold uppercase tracking-[0.14em] text-muted">
              Confiance
            </span>
            <h2 className="text-display-sm mt-4 font-bold text-body">
              Conçu pour protéger, sans vous surveiller.
            </h2>
            <p className="mt-4 text-sm leading-relaxed text-secondary">
              D&apos;autres solutions d&apos;identification d&apos;appelant se construisent en
              aspirant le carnet d&apos;adresses de leurs utilisateurs. TrustLine a refusé ce
              modèle.
            </p>
          </div>
          <ul className="grid grid-cols-1 gap-x-8 gap-y-4 sm:grid-cols-2 lg:col-span-6 lg:col-start-7">
            {POINTS.map((p) => (
              <li key={p} className="flex items-start gap-3 text-sm text-body">
                <svg viewBox="0 0 20 20" fill="none" className="mt-0.5 h-4 w-4 flex-none text-[var(--color-success)]">
                  <path d="M5 10.5l3.2 3.2L15 6.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                {p}
              </li>
            ))}
          </ul>
        </Reveal>
      </div>
    </section>
  );
}
