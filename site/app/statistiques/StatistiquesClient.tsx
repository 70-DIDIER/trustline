"use client";

import { useEffect, useState } from "react";
import { getStats, type Stats } from "@/lib/api";
import { ChartCard } from "@/components/stats/ChartCard";
import { TopNumeros } from "@/components/numbers/TopNumeros";
import { ErrorState, LoadingState } from "@/components/ui/States";
import { SectionHeading } from "@/components/ui/SectionHeading";

const STATUT_LABEL: Record<string, string> = {
  en_attente: "En attente de modération",
  valide: "Validés",
  conteste: "Contestés",
  rejete: "Rejetés",
};

const AUJOURDHUI = new Intl.DateTimeFormat("fr-FR", { day: "2-digit", month: "long", year: "numeric" }).format(
  new Date()
);

// KPI rendu sur fond sombre — grand chiffre blanc, libellé discret.
function DarkKpi({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="px-0 py-2 sm:px-8 sm:py-0 sm:first:pl-0">
      <p className="text-xs font-semibold uppercase tracking-wide text-inverse-muted">{label}</p>
      <p className="mt-2 font-mono text-[clamp(2.5rem,5vw,3.5rem)] font-bold leading-none tabular-nums text-white">
        {value}
      </p>
    </div>
  );
}

export function StatistiquesClient() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [erreur, setErreur] = useState(false);

  function charger() {
    setErreur(false);
    setStats(null);
    getStats().then(setStats).catch(() => setErreur(true));
  }

  useEffect(charger, []);

  return (
    <>
      {/* Bande data sombre — identité « observatoire » + KPIs réels */}
      <section className="bg-inverse-grad">
        <div className="mx-auto max-w-content px-5 py-16 sm:px-8 sm:py-20">
          <div className="max-w-2xl">
            <span className="block font-mono text-xs font-semibold uppercase tracking-[0.16em] text-inverse-muted">
              Observatoire
            </span>
            <h1 className="text-display-sm mt-4 font-bold text-white">
              Ce que les signalements nous apprennent.
            </h1>
            <p className="mt-4 text-sm leading-relaxed text-inverse-muted">
              Uniquement des données réellement enregistrées par la plateforme. Aucune information
              personnelle n&apos;est exposée ici.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 divide-y divide-[color:var(--color-inverse-border)] border-t border-inverse pt-2 sm:grid-cols-3 sm:divide-x sm:divide-y-0 sm:border-t-0">
            {erreur ? (
              <>
                <DarkKpi label="Signalements reçus" value="—" />
                <DarkKpi label="Numéros suivis" value="—" />
                <DarkKpi label="Analyses effectuées" value="—" />
              </>
            ) : (
              <>
                <DarkKpi label="Signalements reçus" value={stats ? stats.total_signalements : "—"} />
                <DarkKpi label="Numéros suivis" value={stats ? stats.total_numeros_suivis : "—"} />
                <DarkKpi label="Analyses effectuées" value={stats ? stats.total_analyses : "—"} />
              </>
            )}
          </div>
        </div>
      </section>

      {/* Analyse détaillée — sur fond clair */}
      <section className="border-t border-base bg-app">
        <div className="mx-auto flex max-w-content flex-col gap-16 px-5 py-16 sm:px-8 sm:py-24">
          {erreur ? (
            <ErrorState
              message="Le service de statistiques est momentanément indisponible. Réessayez dans quelques instants."
              onRetry={charger}
            />
          ) : !stats ? (
            <LoadingState label="Chargement des statistiques…" />
          ) : (
            <>
              <div className="grid gap-6 lg:grid-cols-2">
                <ChartCard
                  title="Types d'arnaques les plus signalés"
                  description="Quels signalements reviennent le plus souvent ?"
                  data={stats.signalements_par_categorie.map((c) => ({ label: c.categorie__libelle, value: c.total }))}
                  source="Base de signalements TrustLine"
                  periode={`Depuis le lancement — relevé au ${AUJOURDHUI}`}
                />
                <ChartCard
                  title="Statut de modération"
                  description="Où en sont les signalements reçus ?"
                  tone="blue"
                  data={stats.signalements_par_statut.map((s) => ({ label: STATUT_LABEL[s.statut] ?? s.statut, value: s.total }))}
                  source="Base de signalements TrustLine"
                  periode={`Depuis le lancement — relevé au ${AUJOURDHUI}`}
                />
              </div>

              <div>
                <SectionHeading
                  eyebrow="Numéros"
                  title="Quels numéros reviennent le plus dans les signalements ?"
                  description="Numéros masqués — la base publique ne dévoile jamais un numéro complet en dehors de votre propre recherche."
                />
                <div className="mt-8 grid grid-cols-1 gap-10 lg:grid-cols-12 lg:gap-12">
                  <div className="lg:col-span-7">
                    <TopNumeros />
                  </div>
                  <aside className="lg:col-span-5 lg:pt-2 text-sm leading-relaxed text-secondary">
                    <p>
                      Ce classement se limite aux numéros que la communauté a effectivement
                      signalés. Il n&apos;est pas une liste noire officielle : un numéro absent
                      peut rester dangereux, un numéro présent peut être régularisé.
                    </p>
                    <p className="mt-4 border-t border-base pt-4 text-xs text-muted">
                      Mise à jour en continu à chaque nouveau signalement validé.
                    </p>
                  </aside>
                </div>
              </div>
            </>
          )}
        </div>
      </section>
    </>
  );
}
