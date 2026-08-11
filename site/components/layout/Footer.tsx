import Link from "next/link";
import { Logo } from "@/components/ui/Logo";
import { INSTITUTIONS } from "@/lib/content/institutions";

const PRODUIT = [
  { href: "/verifier", label: "Vérifier" },
  { href: "/signaler", label: "Signaler" },
  { href: "/alertes", label: "Alertes" },
  { href: "/statistiques", label: "Statistiques" },
  { href: "/apprendre", label: "Apprendre" },
];

const RESSOURCES = [
  { href: "/telecharger", label: "Téléchargements" },
  { href: "/api-partenaires", label: "API" },
  { href: "/a-propos", label: "À propos" },
];

const LEGAL = [
  { href: "/a-propos#confidentialite", label: "Confidentialité" },
  { href: "/a-propos#mentions", label: "Mentions" },
  { href: "/a-propos#methodologie", label: "Méthodologie" },
];

export default function Footer() {
  return (
    <footer className="border-t border-base">
      <div className="mx-auto max-w-content px-5 py-14 sm:px-8">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <Logo width={190} />
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted">
              TrustLine — Protection numérique citoyenne : vérification et signalement
              communautaire des arnaques numériques au Togo.
            </p>
          </div>

          <FooterCol title="Produit" links={PRODUIT} />
          <FooterCol title="Ressources" links={RESSOURCES} />
          <FooterCol title="Légal" links={LEGAL} />
        </div>

        <div className="mt-10 border-t border-base pt-8">
          <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted">
            Ressources institutionnelles
          </h3>
          <p className="mb-4 text-xs text-muted">
            Pour aller plus loin — TrustLine n&apos;est affilié à aucun de ces organismes.
          </p>
          <div className="grid gap-4 sm:grid-cols-2">
            {INSTITUTIONS.map((i) => (
              <a
                key={i.href}
                href={i.href}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg border border-base p-4 transition-colors hover:border-strong"
              >
                <span className="text-sm font-semibold text-brand">{i.label} ↗</span>
                <p className="mt-1 text-xs text-muted">{i.desc}</p>
              </a>
            ))}
          </div>
        </div>

        <div className="mt-10 flex flex-wrap items-center justify-between gap-3 border-t border-base pt-6 text-xs text-muted">
          <p className="font-mono uppercase tracking-[0.14em] text-muted">
            Connecter · Protéger · Assurer
          </p>
          <p>© 2026 TrustLine — Conçu au Togo</p>
        </div>
      </div>
    </footer>
  );
}

function FooterCol({ title, links }: { title: string; links: { href: string; label: string }[] }) {
  return (
    <div>
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted">{title}</h3>
      <ul className="flex flex-col gap-2.5 text-sm">
        {links.map((l) => (
          <li key={l.href}>
            <Link href={l.href} className="text-muted hover:text-body">
              {l.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
