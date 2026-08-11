import type { Metadata } from "next";
import { API_BASE } from "@/lib/api";
import { ENDPOINTS } from "@/lib/content/api-endpoints";
import { Badge } from "@/components/ui/Badge";
import { ButtonLink } from "@/components/ui/Button";

export const metadata: Metadata = {
  title: "API partenaires",
  description: "Intégrez la vérification TrustLine à vos services : banques, opérateurs, fintech, CERT.",
};

const CIBLES = ["Banques", "Opérateurs", "Fintech", "Entreprises", "CERT", "Institutions"];

const ERREURS = [
  { code: "400", label: "Requête invalide", desc: "Champ manquant ou mal formé (voir le détail retourné par le serializer)." },
  { code: "404", label: "Ressource introuvable", desc: "Numéro inconnu de la base (GET /numeros/{numero}/)." },
  { code: "429", label: "Trop de requêtes", desc: "Limite de débit atteinte (throttling par IP / utilisateur)." },
];

export default function ApiPartenairesPage() {
  return (
    <main className="mx-auto max-w-content px-5 py-16 sm:px-8 sm:py-24">
      <span className="mb-3 block font-mono text-xs font-semibold uppercase tracking-[0.14em] text-muted">
        Intégration
      </span>
      <h1 className="text-display-sm max-w-2xl font-bold text-body">
        Intégrez la vérification TrustLine à vos services.
      </h1>
      <p className="mt-4 max-w-2xl text-sm leading-relaxed text-secondary">
        L&apos;API publique de détection est ouverte à toute organisation souhaitant vérifier un
        numéro, un lien ou un message avant d&apos;interagir avec un usager.
      </p>

      <div className="mt-6 flex flex-wrap gap-2">
        {CIBLES.map((c) => (
          <Badge key={c} tone="neutral">{c}</Badge>
        ))}
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <ButtonLink href={`${API_BASE}/docs/`} external variant="primary">
          Documentation Swagger interactive ↗
        </ButtonLink>
        <ButtonLink href={`${API_BASE}/schema/`} external variant="outline">
          Schéma OpenAPI ↗
        </ButtonLink>
      </div>

      <p className="mt-4 max-w-2xl text-xs text-muted">
        Les endpoints ci-dessous sont reproduits depuis l&apos;implémentation réelle du backend.
        Pour la référence exhaustive et toujours à jour (schémas, codes d&apos;erreur,
        authentification), utilisez la documentation Swagger ci-dessus.
      </p>

      <div className="mt-10 flex flex-col gap-4">
        {ENDPOINTS.map((e) => (
          <div key={e.chemin} className="rounded-lg border border-base bg-app p-6">
            <div className="flex flex-wrap items-center gap-3">
              <span
                className={
                  e.methode === "GET"
                    ? "rounded bg-safe-soft px-2 py-0.5 font-mono text-xs font-bold"
                    : "rounded bg-trustline-primary/15 px-2 py-0.5 font-mono text-xs font-bold text-brand"
                }
              >
                {e.methode}
              </span>
              <code className="font-mono text-sm text-body">{e.chemin}</code>
            </div>
            <p className="mt-2 text-sm text-muted">{e.resume}</p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {e.requete ? (
                <div>
                  <p className="mb-1.5 text-[0.7rem] font-semibold uppercase tracking-wide text-muted">Requête</p>
                  <pre className="overflow-x-auto rounded-lg border border-inverse bg-inverse-surface p-3.5 font-mono text-xs leading-relaxed text-[#dbe3f1]">{e.requete}</pre>
                </div>
              ) : null}
              <div className={e.requete ? "" : "sm:col-span-2"}>
                <p className="mb-1.5 text-[0.7rem] font-semibold uppercase tracking-wide text-muted">Réponse</p>
                <pre className="overflow-x-auto rounded-lg border border-inverse bg-inverse-surface p-3.5 font-mono text-xs leading-relaxed text-[#dbe3f1]">{e.reponse}</pre>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-10">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted">Codes d&apos;erreur</p>
        <div className="overflow-hidden rounded-lg border border-base">
          {ERREURS.map((e) => (
            <div key={e.code} className="flex items-center gap-4 border-b border-base bg-app px-4 py-3 text-sm last:border-b-0">
              <code className="w-10 flex-none font-mono font-bold text-danger">{e.code}</code>
              <span className="w-40 flex-none font-semibold text-body">{e.label}</span>
              <span className="text-muted">{e.desc}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-10 rounded-lg border border-dashed border-base bg-app p-6">
        <p className="text-sm text-secondary">
          Prototype de hackathon : rate limiting actif sur les endpoints publics, aucune clé
          d&apos;API n&apos;est requise pour l&apos;instant. Pour une intégration en production,
          contactez l&apos;équipe TrustLine.
        </p>
      </div>
    </main>
  );
}
