import type { Metadata } from "next";
import { ReportForm } from "@/components/reports/ReportForm";

export const metadata: Metadata = {
  title: "Signaler une arnaque",
  description: "Signalez un numéro, un lien ou un message suspect à la communauté TrustLine.",
};

export default function SignalerPage() {
  return (
    <main className="mx-auto max-w-xl px-5 py-16 sm:px-8 sm:py-24">
      <span className="mb-3 block font-mono text-xs font-semibold uppercase tracking-[0.14em] text-muted">
        Signalement
      </span>
      <h1 className="text-display-sm font-bold text-body">
        Votre signalement peut protéger quelqu&apos;un d&apos;autre.
      </h1>
      <p className="mt-4 text-sm leading-relaxed text-secondary">
        Trente secondes, aucun compte requis. Un seul signalement isolé ne suffit jamais à
        classer un numéro « dangereux » — c&apos;est le nombre de déclarants distincts qui
        compte.
      </p>
      <div className="mt-10">
        <ReportForm />
      </div>
    </main>
  );
}
