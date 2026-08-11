"use client";

import { useEffect, useMemo, useState } from "react";
import { getAlertes, type AlertePublique, type NiveauRisque } from "@/lib/api";
import { CampaignCard } from "@/components/alerts/CampaignCard";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/States";
import { RISK_LABEL } from "@/components/ui/RiskBadge";
import { cn } from "@/lib/utils";

const NIVEAUX: { value: NiveauRisque | "tous"; label: string }[] = [
  { value: "tous", label: "Tous" },
  { value: "eleve", label: RISK_LABEL.eleve },
  { value: "suspect", label: RISK_LABEL.suspect },
  { value: "faible", label: RISK_LABEL.faible },
];

export function AlertesClient() {
  const [alertes, setAlertes] = useState<AlertePublique[] | null>(null);
  const [erreur, setErreur] = useState(false);
  const [filtre, setFiltre] = useState<NiveauRisque | "tous">("tous");
  const [recherche, setRecherche] = useState("");

  function charger() {
    setErreur(false);
    setAlertes(null);
    getAlertes()
      .then(setAlertes)
      .catch(() => setErreur(true));
  }

  useEffect(charger, []);

  const filtrees = useMemo(() => {
    const q = recherche.trim().toLowerCase();
    return (alertes ?? []).filter(
      (a) =>
        (filtre === "tous" || a.niveau_risque === filtre) &&
        (q === "" || a.libelle.toLowerCase().includes(q))
    );
  }, [alertes, filtre, recherche]);

  return (
    <div>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-1.5">
          {NIVEAUX.map((n) => (
            <button
              key={n.value}
              type="button"
              onClick={() => setFiltre(n.value)}
              className={cn(
                "rounded-full px-3.5 py-1.5 text-xs font-semibold transition-colors",
                filtre === n.value ? "bg-brand text-on-brand" : "bg-surface-2 text-muted hover:text-body"
              )}
            >
              {n.label}
            </button>
          ))}
        </div>
        <label className="relative w-full sm:w-64">
          <span className="sr-only">Rechercher une alerte</span>
          <svg viewBox="0 0 20 20" fill="none" className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted">
            <circle cx="9" cy="9" r="6" stroke="currentColor" strokeWidth="1.6" />
            <path d="M14 14l4 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
          </svg>
          <input
            type="text"
            value={recherche}
            onChange={(e) => setRecherche(e.target.value)}
            placeholder="Rechercher…"
            className="w-full rounded-sm border border-base bg-app py-2 pl-9 pr-3 text-sm text-body outline-none placeholder:text-muted focus:border-[var(--color-primary)]"
          />
        </label>
      </div>

      <div className="mt-8">
        {erreur ? (
          <ErrorState
            message="Le service d'analyse est momentanément indisponible. Réessayez dans quelques instants."
            onRetry={charger}
          />
        ) : !alertes ? (
          <LoadingState label="Chargement des alertes…" />
        ) : filtrees.length === 0 ? (
          <EmptyState
            title="Aucune alerte active pour ce filtre"
            description="Les catégories réapparaissent dès qu'un signalement communautaire les concerne."
          />
        ) : (
          <div className="grid gap-5 sm:grid-cols-2">
            {filtrees.map((a) => (
              <CampaignCard key={a.categorie} alerte={a} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
