"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getAlertes, type AlertePublique } from "@/lib/api";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { CONTENU_CATEGORIES } from "@/lib/content/categories";
import { formatRelatif } from "@/lib/utils";
import { Reveal } from "@/components/ui/Reveal";
import { EmptyState, LoadingState } from "@/components/ui/States";

export function AlertsSection() {
  const [alertes, setAlertes] = useState<AlertePublique[] | null>(null);
  const [erreur, setErreur] = useState(false);

  useEffect(() => {
    getAlertes().then(setAlertes).catch(() => setErreur(true));
  }, []);

  if (erreur) return null;

  const [principale, ...reste] = alertes ?? [];

  return (
    <section className="border-y border-base bg-surface-alt">
      <div className="mx-auto max-w-content px-5 py-20 sm:px-8 sm:py-28">
        <Reveal className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <span className="font-mono text-xs font-semibold uppercase tracking-[0.14em] text-muted">Alertes</span>
            <h2 className="text-display-sm mt-4 font-bold text-body">
              Les menaces récemment signalées.
            </h2>
          </div>
          <Link href="/alertes" className="text-sm font-semibold text-brand hover:underline">
            Voir l&apos;observatoire des alertes →
          </Link>
        </Reveal>

        <div className="mt-12">
          {!alertes ? (
            <LoadingState label="Chargement des alertes…" />
          ) : !principale ? (
            <EmptyState title="Aucune alerte active pour le moment" />
          ) : (
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
              <Reveal className="lg:col-span-7">
                <Link
                  href="/alertes"
                  className="flex h-full flex-col justify-between rounded-lg border border-base bg-app p-8 transition-colors hover:border-strong"
                >
                  <div className="flex items-center justify-between">
                    <RiskBadge niveau={principale.niveau_risque} />
                    <span className="text-xs text-muted">{formatRelatif(principale.derniere_activite)}</span>
                  </div>
                  <div className="mt-6">
                    <h3 className="text-display-sm font-bold text-body">{principale.libelle}</h3>
                    <p className="mt-3 max-w-md text-sm leading-relaxed text-secondary">
                      {(CONTENU_CATEGORIES[principale.categorie] ?? CONTENU_CATEGORIES.autre).description}
                    </p>
                  </div>
                  <p className="mt-8 text-xs text-muted">
                    {principale.nombre_signalements} signalement{principale.nombre_signalements > 1 ? "s" : ""} communautaire{principale.nombre_signalements > 1 ? "s" : ""}
                  </p>
                </Link>
              </Reveal>

              <ul className="flex flex-col gap-3 lg:col-span-5">
                {reste.slice(0, 3).map((a, i) => (
                  <Reveal key={a.categorie} as="li" delay={i * 90}>
                    <Link
                      href="/alertes"
                      className="flex items-center justify-between gap-4 rounded-lg border border-base bg-app p-5 transition-colors hover:border-strong"
                    >
                      <div>
                        <p className="text-sm font-semibold text-body">{a.libelle}</p>
                        <p className="mt-0.5 text-xs text-muted">{formatRelatif(a.derniere_activite)}</p>
                      </div>
                      <RiskBadge niveau={a.niveau_risque} size="sm" />
                    </Link>
                  </Reveal>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
