import type { Metadata } from "next";
import { VerificationBox } from "@/components/verification/VerificationBox";
import { TopNumeros } from "@/components/numbers/TopNumeros";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { RiskBadge } from "@/components/ui/RiskBadge";

export const metadata: Metadata = {
  title: "Vérifier",
  description: "Vérifiez un numéro, un lien ou un message suspect avant d'agir.",
};

const MODES = [
  { n: "01", titre: "Numéro", desc: "Réputation communautaire et liste blanche officielle." },
  { n: "02", titre: "Lien", desc: "Domaine, typosquat, réputation de la source." },
  { n: "03", titre: "Message", desc: "Signaux textuels : urgence, demande de code, gain." },
];

export default function VerifierPage() {
  return (
    <main>
      <div className="mx-auto grid max-w-content grid-cols-1 gap-10 px-5 py-16 sm:px-8 sm:py-24 lg:grid-cols-12">
        <div className="lg:col-span-5">
          <span className="font-mono text-xs font-semibold uppercase tracking-[0.14em] text-muted">
            Vérification
          </span>
          <h1 className="text-display-sm mt-4 font-bold text-body">Vérifier avant d&apos;agir.</h1>
          <ul className="mt-8 flex flex-col gap-5">
            {MODES.map((m) => (
              <li key={m.n} className="flex gap-4">
                <span className="font-mono text-xs text-muted">{m.n}</span>
                <div>
                  <p className="text-sm font-semibold text-body">{m.titre}</p>
                  <p className="mt-0.5 text-sm text-secondary">{m.desc}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="lg:col-span-7">
          <VerificationBox />
        </div>
      </div>

      <div className="border-t border-base bg-surface-alt">
        <div className="mx-auto max-w-content px-5 py-16 sm:px-8 sm:py-20">
          <SectionHeading
            eyebrow="Numéros signalés"
            title="Les numéros les plus signalés par la communauté"
            description="Base construite uniquement à partir de signalements volontaires et de sources publiques — jamais par aspiration de répertoire."
          />
          <div className="mt-10 grid grid-cols-1 gap-10 lg:grid-cols-12 lg:gap-12">
            <div className="lg:col-span-7">
              <TopNumeros />
            </div>
            <aside className="lg:col-span-5 lg:pt-2">
              <h3 className="text-sm font-bold text-body">Comment lire ce classement</h3>
              <dl className="mt-4 flex flex-col gap-3">
                <div className="flex items-start gap-3">
                  <span className="mt-0.5 flex-none"><RiskBadge niveau="eleve" size="sm" /></span>
                  <dd className="text-sm text-secondary">
                    Plusieurs signalements concordants et récents. Ne rappelez pas, ne répondez pas.
                  </dd>
                </div>
                <div className="flex items-start gap-3">
                  <span className="mt-0.5 flex-none"><RiskBadge niveau="suspect" size="sm" /></span>
                  <dd className="text-sm text-secondary">
                    Quelques signaux isolés. Restez prudent tant que le contexte n&apos;est pas clair.
                  </dd>
                </div>
                <div className="flex items-start gap-3">
                  <span className="mt-0.5 flex-none"><RiskBadge niveau="faible" size="sm" /></span>
                  <dd className="text-sm text-secondary">
                    Aucun signalement à ce jour — l&apos;absence de risque connu n&apos;est pas une garantie.
                  </dd>
                </div>
              </dl>
              <p className="mt-6 border-t border-base pt-4 text-xs leading-relaxed text-muted">
                Le classement reflète uniquement l&apos;activité communautaire du moment. Un numéro
                peut disparaître de la liste dès que les signalements cessent.
              </p>
            </aside>
          </div>
        </div>
      </div>
    </main>
  );
}
