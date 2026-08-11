import { RiskBadge } from "@/components/ui/RiskBadge";
import type { AlertePublique, TypeCible } from "@/lib/api";
import { TYPES_CIBLE } from "@/lib/api";
import { CONTENU_CATEGORIES } from "@/lib/content/categories";
import { formatRelatif } from "@/lib/utils";

const LABEL_TYPE: Record<string, string> = Object.fromEntries(TYPES_CIBLE.map((t) => [t.code, t.label]));

export function CampaignCard({ alerte }: { alerte: AlertePublique }) {
  const contenu = CONTENU_CATEGORIES[alerte.categorie] ?? CONTENU_CATEGORIES.autre;
  const canaux = Object.keys(alerte.types_cibles) as TypeCible[];

  return (
    <div className="reveal flex flex-col gap-4 rounded-lg border border-base bg-app p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <RiskBadge niveau={alerte.niveau_risque} />
        <span className="text-xs text-muted">{formatRelatif(alerte.derniere_activite)}</span>
      </div>

      <div>
        <h3 className="font-display text-lg font-bold text-body">{alerte.libelle}</h3>
        <p className="mt-1.5 text-sm leading-relaxed text-muted">{contenu.description}</p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {canaux.map((c) => (
          <span key={c} className="rounded-full border border-base bg-app px-2.5 py-1 text-[0.7rem] font-medium text-muted">
            {LABEL_TYPE[c] ?? c}
          </span>
        ))}
        <span className="rounded-full border border-base bg-app px-2.5 py-1 text-[0.7rem] font-medium text-muted">
          {alerte.nombre_signalements} signalement{alerte.nombre_signalements > 1 ? "s" : ""}
        </span>
      </div>

      <div className="border-t border-base pt-4">
        <p className="text-[0.7rem] font-semibold uppercase tracking-wide text-muted">Signes à reconnaître</p>
        <ul className="mt-2 flex flex-col gap-1.5">
          {contenu.signes.map((s) => (
            <li key={s} className="flex items-start gap-2 text-sm text-body">
              <span className="mt-1.5 h-1 w-1 flex-none rounded-full bg-brand" />
              {s}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
