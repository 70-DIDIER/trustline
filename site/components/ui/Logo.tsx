import Image from "next/image";
import { cn } from "@/lib/utils";

// Logo officiel TrustLine (bouclier + TL + wordmark), fourni par l'équipe.
// public/brand/trustline-logo.png = lockup complet, rogné des marges transparentes
// du fichier source (aucun pixel du dessin n'est modifié). Ratio conservé partout.
const LOCKUP_RATIO = 483 / 208;

export function Logo({
  className,
  priority = false,
  width = 170,
}: {
  className?: string;
  priority?: boolean;
  width?: number;
}) {
  return (
    <Image
      src="/brand/trustline-logo.png"
      alt="TrustLine — Connecter · Protéger · Assurer"
      width={width}
      height={Math.round(width / LOCKUP_RATIO)}
      priority={priority}
      className={cn("h-auto w-full object-contain", className)}
    />
  );
}

// Marque seule (bouclier + TL, sans le wordmark) — usages compacts (ex. favicon-like inline).
const MARK_RATIO = 168 / 216;

export function LogoMark({ className, size = 32 }: { className?: string; size?: number }) {
  return (
    <Image
      src="/brand/trustline-mark.png"
      alt="TrustLine"
      width={Math.round(size * MARK_RATIO)}
      height={size}
      className={cn("h-auto w-auto object-contain", className)}
      style={{ height: size, width: "auto" }}
    />
  );
}
