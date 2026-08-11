"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getStats, type Stats } from "@/lib/api";
import { Reveal } from "@/components/ui/Reveal";

export function StatsStory() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    getStats().then(setStats).catch(() => setStats(null));
  }, []);

  return (
    <section className="bg-inverse-grad">
      <div className="mx-auto max-w-content px-5 py-24 sm:px-8 sm:py-32">
        <div className="grid grid-cols-1 gap-14 lg:grid-cols-12 lg:gap-10">
          {/* Colonne éditoriale */}
          <Reveal className="lg:col-span-5">
            <span className="font-mono text-xs font-semibold uppercase tracking-[0.16em] text-inverse-muted">
              Les chiffres
            </span>
            <h2 className="text-display-sm mt-4 font-bold leading-[1.12] text-white">
              Les arnaques numériques ne sont plus marginales.
            </h2>
            <p className="mt-6 max-w-md text-base leading-relaxed text-inverse-muted">
              Au Togo, la fraude en ligne a changé d&apos;échelle. TrustLine construit sa
              réponse sur des signalements réels, pas sur des estimations.
            </p>

            <Reveal
              delay={220}
              className="mt-10 inline-flex items-center gap-3 rounded-full border border-inverse bg-white/[0.04] px-4 py-2"
            >
              <span className="h-2 w-2 flex-none rounded-full bg-[var(--color-success)] tl-pulse" />
              <p className="text-sm text-inverse-muted">
                <span className="font-mono font-semibold tabular-nums text-white">
                  {stats ? stats.total_signalements : "—"}
                </span>{" "}
                signalements sur TrustLine.{" "}
                <Link
                  href="/statistiques"
                  className="font-semibold text-white underline-offset-4 hover:underline"
                >
                  Observatoire →
                </Link>
              </p>
            </Reveal>
          </Reveal>

          {/* Colonne data — le chiffre dramatique */}
          <div className="lg:col-span-6 lg:col-start-7">
            <Reveal className="border-b border-inverse pb-9">
              <div className="text-[clamp(3.75rem,9vw,6.5rem)] font-bold leading-[0.9] tracking-tight text-white">
                500<span className="text-[var(--color-success)]">M</span>
              </div>
              <p className="mt-5 max-w-sm text-sm leading-relaxed text-inverse-muted">
                FCFA de préjudice estimé par l&apos;ANCy pour la seule année 2025 — un chiffre
                que l&apos;agence juge elle-même sous-évalué.
              </p>
            </Reveal>

            <div className="mt-9 grid grid-cols-1 gap-9 sm:grid-cols-2">
              <Reveal delay={80}>
                <div className="font-mono text-4xl font-bold tabular-nums text-white">333 000+</div>
                <p className="mt-3 text-sm text-inverse-muted">
                  Incidents de cybersécurité traités au Togo entre 2021 et 2024.
                </p>
              </Reveal>
              <Reveal delay={160}>
                <div className="font-mono text-4xl font-bold tabular-nums text-white">×4,6</div>
                <p className="mt-3 text-sm text-inverse-muted">
                  Progression des cas signalés entre 2021 et 2024.
                </p>
              </Reveal>
            </div>

            <p className="mt-10 text-[0.7rem] leading-relaxed text-inverse-muted">
              Source des chiffres nationaux : Agence Nationale de Cybersécurité (ANCy), 2025.
              TrustLine n&apos;est pas un service de l&apos;ANCy.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
