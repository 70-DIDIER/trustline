import { Button, ButtonLink } from "@/components/ui/Button";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { VerdictIcon } from "./VerdictIcon";
import type { NiveauRisque } from "@/lib/api";
import type { VerdictNormalise } from "./types";

const RISQUE_TITRE: Record<NiveauRisque, string> = {
  faible: "Aucun signal d'arnaque connu",
  suspect: "Signaux à surveiller",
  eleve: "Risque élevé",
};

const RISQUE_INTRO: Record<NiveauRisque, string> = {
  faible: "Cet élément ne présente aucun signal associé à une arnaque connue à ce jour.",
  suspect: "Cet élément présente certains signaux à surveiller. Restez prudent.",
  eleve: "Ce contenu présente plusieurs signaux associés à des tentatives d'arnaque.",
};

const CONSEILS: Record<NiveauRisque, string[]> = {
  faible: [
    "Restez tout de même attentif si la demande évolue par la suite.",
    "Signalez si vous recevez un message inhabituel de ce contact.",
  ],
  suspect: [
    "Ne communiquez aucune information sensible dans l'immédiat.",
    "Vérifiez l'information auprès du service officiel concerné.",
    "Signalez si vous avez un doute persistant.",
  ],
  eleve: [
    "Ne payez pas.",
    "Ne communiquez jamais votre code PIN ou OTP.",
    "Vérifiez auprès du service officiel — jamais via le contact reçu.",
    "Signalez ce contenu pour protéger les autres utilisateurs.",
  ],
};

export function VerificationResult({
  verdict,
  onReset,
}: {
  verdict: VerdictNormalise;
  onReset: () => void;
}) {
  return (
    <div className="reveal rounded-xl border border-base bg-app p-6 text-left sm:p-8">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-4">
          <VerdictIcon niveau={verdict.niveau_risque} />
          <div>
            <RiskBadge niveau={verdict.niveau_risque} size="lg" />
            <h3 className="font-display mt-2 text-xl font-bold text-body sm:text-2xl">
              {RISQUE_TITRE[verdict.niveau_risque]}
            </h3>
          </div>
        </div>
        <span className="flex-none font-mono text-sm text-muted tabular-nums">
          {verdict.score}<span className="text-muted">/100</span>
        </span>
      </div>
      <p className="mt-4 text-sm leading-relaxed text-muted sm:text-[0.95rem]">
        {RISQUE_INTRO[verdict.niveau_risque]}
      </p>

      {verdict.indices.length > 0 ? (
        <div className="mt-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted">Signaux détectés</p>
          <ul className="mt-2.5 flex flex-col gap-2">
            {verdict.indices.map((indice) => (
              <li key={indice} className="flex items-start gap-2.5 text-sm text-body">
                <svg viewBox="0 0 20 20" fill="none" className="mt-0.5 h-4 w-4 flex-none text-safe">
                  <path d="M5 10.5l3.2 3.2L15 6.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                {indice}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="mt-5 rounded-md border border-base bg-surface-2 p-4">
        <p className="text-sm text-body">{verdict.recommandation}</p>
      </div>

      {verdict.meta.length > 0 ? (
        <dl className="mt-5 grid grid-cols-2 gap-x-4 gap-y-3 border-t border-base pt-5 sm:grid-cols-3">
          {verdict.meta.map((m) => (
            <div key={m.label}>
              <dt className="text-[0.7rem] uppercase tracking-wide text-muted">{m.label}</dt>
              <dd className="mt-0.5 text-sm font-medium text-body">{m.value}</dd>
            </div>
          ))}
        </dl>
      ) : null}

      <div className="mt-6 border-t border-base pt-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">Que faire maintenant ?</p>
        <ol className="mt-2.5 flex flex-col gap-1.5">
          {CONSEILS[verdict.niveau_risque].map((c, i) => (
            <li key={c} className="flex gap-2.5 text-sm text-body">
              <span className="font-mono text-muted">{i + 1}.</span>
              {c}
            </li>
          ))}
        </ol>
      </div>

      <div className="mt-7 flex flex-wrap gap-3">
        <ButtonLink
          href={`/signaler?type=${verdict.type}&cible=${encodeURIComponent(verdict.cible)}`}
          variant="primary"
        >
          Signaler
        </ButtonLink>
        <Button variant="outline" onClick={onReset}>
          Nouvelle vérification
        </Button>
      </div>
    </div>
  );
}
