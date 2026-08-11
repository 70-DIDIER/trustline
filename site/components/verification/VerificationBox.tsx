"use client";

import { useState } from "react";
import { analyserLien, analyserMessage, ApiError, verifierNumero } from "@/lib/api";
import { detecterTypeEntree, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";
import { VerificationResult } from "./VerificationResult";
import { VerdictIcon } from "./VerdictIcon";
import type { ModeVerification, VerdictNormalise } from "./types";

const MODES: { value: ModeVerification; label: string; placeholder: string }[] = [
  { value: "auto", label: "Détection auto", placeholder: "Numéro, lien ou message suspect…" },
  { value: "numero", label: "Numéro", placeholder: "+228 XX XX XX XX" },
  { value: "lien", label: "Lien", placeholder: "https://…" },
  { value: "message", label: "Message", placeholder: "« Vous avez reçu un message… »" },
];

export function VerificationBox({ compact = false }: { compact?: boolean }) {
  const [mode, setMode] = useState<ModeVerification>("auto");
  const [valeur, setValeur] = useState("");
  const [statut, setStatut] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [erreur, setErreur] = useState<string | null>(null);
  const [verdict, setVerdict] = useState<VerdictNormalise | null>(null);

  async function analyser(e: React.FormEvent) {
    e.preventDefault();
    const texte = valeur.trim();
    if (!texte || statut === "loading") return;

    setStatut("loading");
    setErreur(null);

    const type = mode === "auto" ? detecterTypeEntree(texte) : mode;

    try {
      let normalise: VerdictNormalise;

      if (type === "numero") {
        const v = await verifierNumero(texte);
        normalise = {
          type: "numero",
          cible: v.numero,
          niveau_risque: v.niveau_risque,
          score: v.score,
          indices: v.indices,
          recommandation: v.recommandation,
          meta: [
            v.est_liste_blanche ? { label: "Statut", value: "Numéro officiel vérifié" } : null,
            v.organisation ? { label: "Organisation", value: v.organisation } : null,
            { label: "Signalements", value: String(v.nombre_signalements) },
            v.date_dernier_signalement
              ? { label: "Dernier signalement", value: formatDate(v.date_dernier_signalement) }
              : null,
          ].filter(Boolean) as { label: string; value: string }[],
        };
      } else if (type === "lien") {
        const url = /^https?:\/\//i.test(texte) ? texte : `https://${texte}`;
        const v = await analyserLien(url);
        normalise = {
          type: "lien",
          cible: v.url,
          niveau_risque: v.niveau_risque,
          score: v.score,
          indices: v.indices,
          recommandation: v.recommandation,
          meta: v.domaine ? [{ label: "Domaine", value: v.domaine }] : [],
        };
      } else {
        const v = await analyserMessage(texte);
        normalise = {
          type: "message",
          cible: texte,
          niveau_risque: v.niveau_risque,
          score: v.score,
          indices: v.indices,
          recommandation: v.recommandation,
          meta: v.categories.length ? [{ label: "Catégories", value: v.categories.join(", ") }] : [],
        };
      }

      setVerdict(normalise);
      setStatut("done");
    } catch (err) {
      setErreur(err instanceof ApiError ? err.message : "Une erreur inattendue est survenue.");
      setStatut("error");
    }
  }

  function reinitialiser() {
    setVerdict(null);
    setStatut("idle");
    setErreur(null);
    setValeur("");
  }

  if (verdict && statut === "done") {
    return <VerificationResult verdict={verdict} onReset={reinitialiser} />;
  }

  return (
    <div className={cn("rounded-xl border border-base bg-app p-5 sm:p-7", compact ? "" : "shadow-soft")}>
      <div className="flex flex-wrap gap-1.5">
        {MODES.map((m) => (
          <button
            key={m.value}
            type="button"
            onClick={() => setMode(m.value)}
            className={cn(
              "rounded-full px-3.5 py-1.5 text-xs font-semibold transition-colors",
              mode === m.value ? "bg-brand text-on-brand" : "bg-surface-2 text-muted hover:text-body"
            )}
          >
            {m.label}
          </button>
        ))}
      </div>

      <form onSubmit={analyser} className="mt-4 flex flex-col gap-3 sm:flex-row">
        <input
          type="text"
          value={valeur}
          onChange={(e) => setValeur(e.target.value)}
          placeholder={MODES.find((m) => m.value === mode)?.placeholder}
          aria-label="Numéro, lien ou message à analyser"
          className="w-full flex-1 rounded-lg border border-base bg-app px-4 py-3.5 text-[0.95rem] text-body outline-none placeholder:text-muted focus:border-[var(--brand-soft)]"
        />
        <Button type="submit" size="lg" disabled={statut === "loading"} className="sm:flex-none">
          {statut === "loading" ? "Analyse…" : "Analyser"}
        </Button>
      </form>

      <p className="mt-3 text-xs text-muted">
        Exemples : <span className="font-mono">+228 XX XX XX XX</span> · <span className="font-mono">https://…</span> ·
        « Vous avez reçu un message… »
      </p>

      {statut === "loading" ? (
        <div className="mt-5">
          <p className="mb-2 text-xs font-medium text-muted">Analyse en cours…</p>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-2">
            <div className="tl-progress-bar h-full rounded-full bg-brand" />
          </div>
        </div>
      ) : null}

      {statut === "error" && erreur ? (
        <div className="mt-5 flex items-start gap-4 rounded-lg border border-base bg-unknown-soft p-4">
          <VerdictIcon niveau="inconnu" size={44} />
          <div className="flex-1">
            <p className="text-sm font-semibold text-body">Analyse indisponible</p>
            <p className="mt-1 text-sm text-muted">{erreur}</p>
            <Button variant="outline" size="md" className="mt-3" onClick={() => setStatut("idle")}>
              Réessayer
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
