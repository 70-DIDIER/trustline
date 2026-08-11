import type { Metadata } from "next";
import { AlertesClient } from "./AlertesClient";

export const metadata: Metadata = {
  title: "Alertes en cours",
  description: "Les campagnes et méthodes d'arnaque actuellement signalées par la communauté au Togo.",
};

export default function AlertesPage() {
  return (
    <main className="mx-auto max-w-content px-5 py-16 sm:px-8 sm:py-24">
      <div className="max-w-2xl">
        <span className="mb-3 block font-mono text-xs font-semibold uppercase tracking-[0.14em] text-muted">
          Observatoire
        </span>
        <h1 className="text-display-sm font-bold text-body">Alertes en cours</h1>
        <p className="mt-4 text-sm leading-relaxed text-secondary">
          Les catégories d&apos;arnaque actuellement signalées par la communauté — dérivées en
          direct des signalements reçus, jamais d&apos;affirmations statistiques nationales.
        </p>
      </div>
      <div className="mt-12">
        <AlertesClient />
      </div>
    </main>
  );
}
