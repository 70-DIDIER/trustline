import type { Metadata } from "next";
import { Badge } from "@/components/ui/Badge";
import { CANAUX } from "@/lib/content/canaux";

export const metadata: Metadata = {
  title: "Téléchargements",
  description: "Les différents canaux d'accès à TrustLine : application, extension, USSD, SMS.",
};

const ICONES: Record<string, React.ReactNode> = {
  android: (
    <>
      <rect x="7" y="2" width="10" height="20" rx="2" />
      <path d="M11 18h2" />
    </>
  ),
  chrome: (
    <>
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="3" />
      <path d="M12 3v6M5.2 16.5l5.2-3M18.8 16.5l-5.2-3" />
    </>
  ),
  ussd: (
    <>
      <rect x="4" y="2" width="16" height="20" rx="2" />
      <path d="M9 6h6M9 18h.01" />
    </>
  ),
  sms: (
    <>
      <path d="M4 4h16v16H4z" />
      <path d="M4 6l8 6 8-6" />
    </>
  ),
};

export default function TelechargerPage() {
  return (
    <main className="mx-auto max-w-content px-5 py-16 sm:px-8 sm:py-24">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <span className="font-mono text-xs font-semibold uppercase tracking-[0.14em] text-muted lg:col-span-12">
          Canaux
        </span>
        <h1 className="text-display-sm font-bold text-body lg:col-span-6">
          TrustLine ne dépend pas d&apos;un seul appareil.
        </h1>
        <p className="text-sm leading-relaxed text-secondary lg:col-span-4 lg:col-start-9">
          Quel que soit votre téléphone — smartphone récent ou appareil à touches — un canal
          TrustLine est accessible.
        </p>
      </div>

      <div className="mt-14 grid gap-5 sm:grid-cols-2">
        {CANAUX.map((c) => (
          <div key={c.id} className="flex flex-col gap-4 rounded-lg border border-base bg-app p-6">
            <div className="flex items-start justify-between gap-3">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="h-9 w-9 text-brand">
                {ICONES[c.id]}
              </svg>
              <Badge tone={c.disponible ? "safe" : "neutral"}>
                {c.disponible ? "Disponible" : "Bientôt"}
              </Badge>
            </div>
            <div>
              <h3 className="text-lg font-bold text-body">{c.titre}</h3>
              <p className="mt-1 text-sm text-secondary">{c.resume}</p>
            </div>
            <p className="text-xs leading-relaxed text-muted">{c.detail}</p>
            {c.action ? (
              <a
                href={c.action.href}
                download
                className="mt-auto inline-flex items-center justify-center rounded-sm bg-brand px-4 py-2.5 text-sm font-semibold text-on-brand"
              >
                {c.action.label}
              </a>
            ) : null}
          </div>
        ))}
      </div>
    </main>
  );
}
