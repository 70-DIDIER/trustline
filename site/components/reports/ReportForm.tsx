"use client";

import { useEffect, useState } from "react";
import { ApiError, CANAUX_RECEPTION, CATEGORIES, TYPES_CIBLE, creerSignalement } from "@/lib/api";
import type { Signalement, TypeCible } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Label, Select, Textarea } from "@/components/ui/Input";
import { ErrorState } from "@/components/ui/States";
import { cn, getDeclarantId } from "@/lib/utils";
import { ReportSuccess } from "./ReportSuccess";

const TOTAL_ETAPES = 4;

const PLACEHOLDER: Record<TypeCible, string> = {
  numero: "+228 90 11 22 33",
  sms: "Collez le texte du SMS reçu…",
  lien: "https://…",
  site: "https://…",
  message: "Collez le message reçu (WhatsApp, réseau social…)",
};

export function ReportForm() {
  const [etape, setEtape] = useState(1);
  const [typeCible, setTypeCible] = useState<TypeCible>("numero");
  const [cible, setCible] = useState("");
  const [categorie, setCategorie] = useState(CATEGORIES[0].code);
  const [canal, setCanal] = useState<string>(CANAUX_RECEPTION[0]);
  const [commentaire, setCommentaire] = useState("");
  const [envoi, setEnvoi] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const [resultat, setResultat] = useState<Signalement | null>(null);

  // Préremplissage depuis le résultat de vérification (?type=...&cible=...).
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const t = params.get("type");
    const c = params.get("cible");
    if (t === "numero" || t === "lien" || t === "message") {
      setTypeCible(t === "lien" ? "lien" : t === "message" ? "message" : "numero");
    }
    if (c) setCible(c);
  }, []);

  function suivant() {
    setErreur(null);
    if (etape === 2 && !cible.trim()) {
      setErreur("Merci de renseigner l'élément à signaler.");
      return;
    }
    setEtape((e) => Math.min(e + 1, TOTAL_ETAPES));
  }

  function precedent() {
    setErreur(null);
    setEtape((e) => Math.max(e - 1, 1));
  }

  async function envoyer() {
    setEnvoi(true);
    setErreur(null);
    try {
      const res = await creerSignalement({
        type_cible: typeCible,
        cible: cible.trim(),
        categorie,
        declarant_id: getDeclarantId(),
        commentaire: `Reçu via : ${canal}.${commentaire.trim() ? " " + commentaire.trim() : ""}`,
      });
      setResultat(res);
    } catch (err) {
      setErreur(err instanceof ApiError ? err.message : "Une erreur est survenue lors de l'envoi.");
    } finally {
      setEnvoi(false);
    }
  }

  function reinitialiser() {
    setResultat(null);
    setEtape(1);
    setCible("");
    setCommentaire("");
    setErreur(null);
  }

  if (resultat) return <ReportSuccess signalement={resultat} onNew={reinitialiser} />;

  return (
    <div className="rounded-xl border border-base bg-app p-6 sm:p-8">
      <ol className="mb-7 flex items-center gap-2" aria-label="Progression du signalement">
        {Array.from({ length: TOTAL_ETAPES }, (_, i) => i + 1).map((n) => (
          <li key={n} className="flex flex-1 flex-col gap-1.5">
            <span
              className={cn(
                "h-1.5 rounded-full transition-colors",
                n <= etape ? "bg-brand" : "bg-surface-2"
              )}
            />
          </li>
        ))}
      </ol>

      {etape === 1 ? (
        <fieldset>
          <legend className="font-display text-lg font-bold text-body">Que souhaitez-vous signaler ?</legend>
          <div className="mt-5 grid gap-2.5 sm:grid-cols-2">
            {TYPES_CIBLE.map((t) => (
              <button
                key={t.code}
                type="button"
                onClick={() => setTypeCible(t.code)}
                className={cn(
                  "rounded-lg border px-4 py-3.5 text-left text-sm font-semibold transition-colors",
                  typeCible === t.code
                    ? "border-[var(--brand-soft)] bg-trustline-primary/10 text-body"
                    : "border-base bg-app text-muted hover:text-body"
                )}
              >
                {t.label}
              </button>
            ))}
          </div>
        </fieldset>
      ) : null}

      {etape === 2 ? (
        <fieldset className="flex flex-col gap-4">
          <legend className="font-display text-lg font-bold text-body">Informations</legend>
          <div>
            <Label htmlFor="cible">Élément concerné</Label>
            <Textarea
              id="cible"
              rows={3}
              value={cible}
              onChange={(e) => setCible(e.target.value)}
              placeholder={PLACEHOLDER[typeCible]}
              className="mt-1.5"
            />
          </div>
          <div>
            <Label htmlFor="commentaire">Description (facultatif)</Label>
            <Textarea
              id="commentaire"
              rows={2}
              value={commentaire}
              onChange={(e) => setCommentaire(e.target.value)}
              placeholder="Tout détail utile pour la modération…"
              className="mt-1.5"
            />
          </div>
        </fieldset>
      ) : null}

      {etape === 3 ? (
        <fieldset className="flex flex-col gap-4">
          <legend className="font-display text-lg font-bold text-body">Contexte</legend>
          <div>
            <Label htmlFor="categorie">Catégorie de l&apos;arnaque</Label>
            <Select id="categorie" value={categorie} onChange={(e) => setCategorie(e.target.value)} className="mt-1.5">
              {CATEGORIES.map((c) => (
                <option key={c.code} value={c.code}>{c.label}</option>
              ))}
            </Select>
          </div>
          <div>
            <Label htmlFor="canal">Comment avez-vous reçu cette arnaque ?</Label>
            <Select id="canal" value={canal} onChange={(e) => setCanal(e.target.value)} className="mt-1.5">
              {CANAUX_RECEPTION.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </Select>
          </div>
        </fieldset>
      ) : null}

      {etape === 4 ? (
        <div>
          <h2 className="font-display text-lg font-bold text-body">Confirmation</h2>
          <p className="mt-2 text-sm text-muted">
            Votre signalement contribue à protéger les autres utilisateurs.
          </p>
          <dl className="mt-5 flex flex-col gap-3 rounded-lg border border-base bg-app p-4 text-sm">
            <Row label="Type" value={TYPES_CIBLE.find((t) => t.code === typeCible)?.label ?? typeCible} />
            <Row label="Élément" value={cible || "—"} />
            <Row label="Catégorie" value={CATEGORIES.find((c) => c.code === categorie)?.label ?? categorie} />
            <Row label="Reçu via" value={canal} />
          </dl>
        </div>
      ) : null}

      {erreur ? (
        <div className="mt-5">
          <ErrorState message={erreur} />
        </div>
      ) : null}

      <div className="mt-7 flex items-center justify-between gap-3">
        <Button variant="outline" onClick={precedent} disabled={etape === 1 || envoi}>
          Précédent
        </Button>
        {etape < TOTAL_ETAPES ? (
          <Button variant="primary" onClick={suivant}>
            Continuer
          </Button>
        ) : (
          <Button variant="primary" onClick={envoyer} disabled={envoi}>
            {envoi ? "Envoi…" : "Envoyer le signalement"}
          </Button>
        )}
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <dt className="text-muted">{label}</dt>
      <dd className="max-w-[65%] truncate text-right font-medium text-body">{value}</dd>
    </div>
  );
}
