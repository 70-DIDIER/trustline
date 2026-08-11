import type { Fiche } from "@/lib/content/fiches";

export function EducationCard({ fiche }: { fiche: Fiche }) {
  return (
    <details className="group rounded-lg border border-base bg-surface open:bg-surface-2">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-5 py-4 text-left">
        <span className="font-display text-base font-bold text-body">{fiche.titre}</span>
        <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 flex-none text-muted transition-transform group-open:rotate-180">
          <path d="M5 7.5l5 5 5-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </summary>
      <div className="flex flex-col gap-5 px-5 pb-6">
        <Bloc titre="Comment ça commence" texte={fiche.commence} />
        <Bloc titre="Ce que l'arnaqueur cherche" texte={fiche.cherche} />
        <ListeBloc titre="Les signaux d'alerte" items={fiche.signaux} tone="warn" />
        <ListeBloc titre="Ce qu'il ne faut jamais faire" items={fiche.jamais} tone="danger" />
        <ListeBloc titre="Ce qu'il faut faire" items={fiche.faire} tone="safe" />
      </div>
    </details>
  );
}

function Bloc({ titre, texte }: { titre: string; texte: string }) {
  return (
    <div>
      <p className="text-[0.7rem] font-semibold uppercase tracking-wide text-muted">{titre}</p>
      <p className="mt-1 text-sm leading-relaxed text-body">{texte}</p>
    </div>
  );
}

function ListeBloc({ titre, items, tone }: { titre: string; items: string[]; tone: "warn" | "danger" | "safe" }) {
  const dot = tone === "warn" ? "bg-[var(--warn)]" : tone === "danger" ? "bg-[var(--danger)]" : "bg-[var(--safe)]";
  return (
    <div>
      <p className="text-[0.7rem] font-semibold uppercase tracking-wide text-muted">{titre}</p>
      <ul className="mt-1.5 flex flex-col gap-1.5">
        {items.map((it) => (
          <li key={it} className="flex items-start gap-2 text-sm text-body">
            <span className={`mt-1.5 h-1.5 w-1.5 flex-none rounded-full ${dot}`} />
            {it}
          </li>
        ))}
      </ul>
    </div>
  );
}
