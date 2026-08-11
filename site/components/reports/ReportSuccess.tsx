import { ButtonLink } from "@/components/ui/Button";
import type { Signalement } from "@/lib/api";

export function ReportSuccess({ signalement, onNew }: { signalement: Signalement; onNew: () => void }) {
  return (
    <div className="reveal rounded-xl border border-base bg-app p-8 text-center sm:p-10">
      <div className="mx-auto grid h-14 w-14 place-items-center rounded-full bg-safe-soft">
        <svg viewBox="0 0 24 24" fill="none" className="h-7 w-7 text-safe">
          <path d="M5 12.5l4.5 4.5L19 7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
      <h2 className="font-display mt-5 text-xl font-bold text-body sm:text-2xl">Signalement enregistré</h2>
      <p className="mx-auto mt-2 max-w-sm text-sm text-muted">
        Votre signalement contribue à protéger les autres utilisateurs. Merci.
      </p>
      <p className="mt-4 inline-flex items-center gap-2 rounded-full border border-base bg-app px-4 py-1.5 font-mono text-sm text-body">
        Référence #{signalement.id}
      </p>

      {signalement.reputation_cible ? (
        <p className="mx-auto mt-4 max-w-sm text-xs text-muted">
          {signalement.reputation_cible.numero} compte désormais{" "}
          {signalement.reputation_cible.nombre_signalements} signalement(s).
        </p>
      ) : null}

      <div className="mt-7 flex flex-wrap justify-center gap-3">
        <button
          type="button"
          onClick={onNew}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-strong px-4 py-2.5 text-sm font-semibold text-body transition-colors hover:bg-surface-2"
        >
          Signaler autre chose
        </button>
        <ButtonLink href="/alertes" variant="primary">
          Voir les alertes
        </ButtonLink>
      </div>
    </div>
  );
}
