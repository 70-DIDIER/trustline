"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getAlertes, type AlertePublique } from "@/lib/api";

const DEMO: AlertePublique = {
  categorie: "fraude_financiere",
  libelle: "Faux dépôt mobile money",
  nombre_signalements: 0,
  niveau_risque: "suspect",
  derniere_activite: null,
  types_cibles: {},
};

export default function AlertBanner() {
  const [alerte, setAlerte] = useState<AlertePublique | null>(null);
  const [demo, setDemo] = useState(false);

  useEffect(() => {
    let active = true;
    getAlertes()
      .then((data) => {
        if (!active) return;
        if (data.length > 0) setAlerte(data[0]);
      })
      .catch(() => {
        if (!active) return;
        // Backend injoignable : on ne montre un bandeau que hors production,
        // clairement identifié comme démonstration — jamais comme donnée réelle.
        if (process.env.NODE_ENV === "development") {
          setAlerte(DEMO);
          setDemo(true);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  if (!alerte) return null;

  return (
    <div className="border-b border-base bg-surface">
      <div className="mx-auto flex max-w-content items-center gap-3 px-5 py-2 text-xs sm:px-8 sm:text-sm">
        <span className="inline-flex flex-none items-center gap-1.5 font-semibold text-warn">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--warn)]" />
          ALERTE ACTIVE
        </span>
        <span className="truncate text-muted">
          {alerte.libelle}
          {demo ? " — données de démonstration" : ""}
        </span>
        <Link href="/alertes" className="ml-auto flex-none font-semibold text-brand hover:underline">
          Voir les alertes →
        </Link>
      </div>
    </div>
  );
}
