import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import CookieBanner from "@/components/layout/CookieBanner";
import AlertBanner from "@/components/layout/AlertBanner";

// Une seule famille, disciplinée sur toute l'interface (Inter) — cf. direction
// "précision, cohérence" plutôt qu'une seconde face display superflue.
const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-sans",
  display: "swap",
});

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "TrustLine — Vérifiez avant d'agir",
    template: "%s — TrustLine",
  },
  description:
    "Vérifiez un numéro, un lien ou un message suspect et signalez les arnaques numériques au Togo. TrustLine aide à identifier les signaux connus d'arnaque.",
  icons: { icon: "/favicon.png", shortcut: "/favicon.png", apple: "/favicon.png" },
  openGraph: {
    title: "TrustLine — Vérifiez avant d'agir",
    description:
      "Protection numérique citoyenne : vérification de numéros, liens et messages, signalement communautaire des arnaques au Togo.",
    url: SITE_URL,
    siteName: "TrustLine",
    locale: "fr_FR",
    type: "website",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "TrustLine" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "TrustLine — Vérifiez avant d'agir",
    description: "Vérifiez un numéro, un lien ou un message suspect avant d'agir.",
    images: ["/og-image.png"],
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className={`${inter.variable}`} style={{ ["--font-display" as string]: "var(--font-sans)" }}>
      <body className="bg-app text-body antialiased">
        <noscript>
          <style>{`.reveal{opacity:1 !important;transform:none !important}`}</style>
        </noscript>
        <Navbar />
        <AlertBanner />
        {children}
        <Footer />
        <CookieBanner />
      </body>
    </html>
  );
}
