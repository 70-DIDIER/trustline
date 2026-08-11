"use client";

import { useEffect, useState } from "react";
import { getStats, type Stats } from "@/lib/api";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { EmptyState, LoadingState } from "@/components/ui/States";
import { maskNumero } from "@/lib/utils";

export function TopNumeros() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [erreur, setErreur] = useState(false);

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch(() => setErreur(true));
  }, []);

  if (erreur) return null; // section secondaire : on n'affiche pas d'erreur bruyante ici
  if (!stats) return <LoadingState label="Chargement des numéros signalés…" />;

  if (stats.top_numeros_signales.length === 0) {
    return <EmptyState title="Aucun numéro signalé pour le moment" description="Les numéros signalés par la communauté apparaîtront ici." />;
  }

  return (
    <div className="overflow-hidden rounded-lg border border-base">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[360px] text-left text-sm">
          <thead className="bg-surface-2 text-xs uppercase tracking-wide text-muted">
            <tr>
              <th className="px-4 py-3 font-semibold">Numéro</th>
              <th className="px-4 py-3 font-semibold">Niveau</th>
              <th className="px-4 py-3 text-right font-semibold">Signal.</th>
            </tr>
          </thead>
          <tbody>
            {stats.top_numeros_signales.map((n) => (
              <tr key={n.numero} className="border-t border-base bg-app">
                <td className="whitespace-nowrap px-4 py-3 font-mono text-body">{maskNumero(n.numero)}</td>
                <td className="px-4 py-3"><RiskBadge niveau={n.niveau_risque} size="sm" /></td>
                <td className="px-4 py-3 text-right font-mono tabular-nums text-body">{n.nombre_signalements}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="border-t border-base bg-app px-4 py-2.5 text-[0.72rem] text-muted">
        Numéros masqués — la base publique n&apos;affiche jamais un numéro complet en dehors de
        votre propre recherche.
      </p>
    </div>
  );
}
