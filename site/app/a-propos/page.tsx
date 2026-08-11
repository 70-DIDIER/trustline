import type { Metadata } from "next";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { Logo } from "@/components/ui/Logo";

export const metadata: Metadata = {
  title: "À propos",
  description: "Le problème, notre approche, l'architecture et la protection des données de TrustLine.",
};

const ARCHITECTURE = [
  "Frontend Next.js — ne décide jamais lui-même si un contenu est une arnaque",
  "API backend (Django REST Framework) — validation, orchestration, anti-abus",
  "Moteur de détection — règles explicables + modèle ML optionnel",
  "Base de données — signalements, réputation, référentiels",
];

const APPROCHE = [
  { titre: "Multicanal", texte: "Un même moteur derrière le web, l'extension, l'USSD et le SMS — le canal ne change rien à la protection." },
  { titre: "Intelligence collective", texte: "La réputation d'un numéro se construit à partir de plusieurs déclarants distincts, jamais d'un seul avis isolé." },
  { titre: "Vérification avant tout", texte: "Le doute doit pouvoir être levé en quelques secondes, avant d'agir — pas après." },
];

const CONFIDENTIALITE = [
  { titre: "Signalement accessible", texte: "Aucun compte requis, aucun jargon technique." },
  { titre: "Protection des citoyens", texte: "Priorité donnée à des conseils actionnables, pas seulement à un score." },
  { titre: "Conformité", texte: "Conçu conformément à la loi togolaise n°2019-014 sur la protection des données à caractère personnel." },
  { titre: "Sans aspiration de répertoire", texte: "Contrairement à d'autres solutions d'identification d'appelant, aucun carnet d'adresses n'est collecté." },
];

export default function AProposPage() {
  return (
    <main className="mx-auto max-w-content px-5 py-16 sm:px-8 sm:py-24">
      <span className="mb-3 block font-mono text-xs font-semibold uppercase tracking-[0.14em] text-muted">
        À propos
      </span>
      <h1 className="text-display-sm max-w-2xl font-bold text-body">
        Construire un espace numérique plus sûr.
      </h1>

      <div className="mt-16 flex flex-col gap-16">
        <section className="grid gap-10 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <SectionHeading eyebrow="Le problème" title="Les arnaques progressent vite au Togo" />
            <p className="mt-4 text-sm leading-relaxed text-secondary">
              Phishing, faux dépôts mobile money, usurpations d&apos;identité : ces arnaques
              circulent principalement par SMS, appel et réseaux sociaux — des canaux que les
              outils de sécurité classiques, pensés pour le web desktop, ne couvrent pas.
            </p>
          </div>
          <div className="lg:col-span-6 lg:col-start-7">
            <SectionHeading eyebrow="Notre approche" title="Vérifier, signaler, protéger" />
            <ul className="mt-4 flex flex-col gap-4">
              {APPROCHE.map((a) => (
                <li key={a.titre} className="text-sm text-secondary">
                  <span className="font-semibold text-body">{a.titre}.</span> {a.texte}
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section>
          <SectionHeading
            eyebrow="Notre technologie"
            title="Le frontend ne décide jamais seul"
            description="Chaque verdict provient du moteur de détection backend — jamais d'une logique dupliquée côté client."
          />
          <ol className="mt-6 flex max-w-2xl flex-col gap-2">
            {ARCHITECTURE.map((a, i) => (
              <li key={a} className="flex items-center gap-3 rounded-md border border-base bg-app px-4 py-3 text-sm text-body">
                <span className="font-mono text-xs text-brand">{i + 1}</span>
                {a}
                {i < ARCHITECTURE.length - 1 ? <span className="ml-auto text-muted">↓</span> : null}
              </li>
            ))}
          </ol>
        </section>

        <section id="confidentialite">
          <SectionHeading eyebrow="Confidentialité" title="Ce que nous ne faisons jamais" />
          <ul className="mt-6 grid gap-3 sm:grid-cols-2">
            {CONFIDENTIALITE.map((a) => (
              <li key={a.titre} className="rounded-lg border border-base bg-app p-4">
                <p className="text-sm font-semibold text-body">{a.titre}</p>
                <p className="mt-1 text-sm text-secondary">{a.texte}</p>
              </li>
            ))}
          </ul>
        </section>

        <section id="methodologie">
          <SectionHeading
            eyebrow="Ressources"
            title="D'où viennent les informations affichées"
            description="Les statistiques de TrustLine proviennent exclusivement des signalements et analyses réalisés sur la plateforme. Les chiffres nationaux cités (page d'accueil) sont attribués à leur source — l'ANCy — et ne sont jamais présentés comme des données TrustLine."
          />
        </section>

        <section>
          <SectionHeading eyebrow="Équipe" title="Un projet de hackathon" />
          <p className="mt-4 max-w-2xl text-sm leading-relaxed text-secondary">
            TrustLine est un prototype conçu par une équipe pluridisciplinaire (cybersécurité,
            intelligence artificielle, développement web et mobile) pendant le Hackathon des
            Togo IT Days 2026 — « Cyber Innovation Challenge ». Ce n&apos;est ni un service
            gouvernemental, ni un produit commercial disponible au public : TrustLine n&apos;est
            affilié à aucune institution officielle et ne prétend à aucun partenariat qui
            n&apos;existe pas.
          </p>
        </section>

        <section id="mentions">
          <SectionHeading eyebrow="Mentions" title="Mentions légales" />
          <p className="mt-4 max-w-2xl text-sm leading-relaxed text-secondary">
            Prototype développé dans le cadre d&apos;un hackathon. Les statistiques et alertes
            affichées reflètent les données réellement enregistrées par la plateforme au moment
            de la consultation. Aucune donnée personnelle n&apos;est collectée au-delà de ce qui
            est strictement nécessaire au fonctionnement du service.
          </p>
        </section>

        <section className="flex flex-col items-center gap-5 border-t border-base pt-16 text-center">
          <div className="w-[190px] max-w-full">
            <Logo width={190} />
          </div>
          <p className="font-mono text-sm uppercase tracking-[0.18em] text-muted">
            Connecter · Protéger · Assurer
          </p>
        </section>
      </div>
    </main>
  );
}
