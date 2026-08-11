import type { NiveauRisque } from "@/lib/api";
import { cn } from "@/lib/utils";

export const RISK_LABEL: Record<NiveauRisque, string> = {
  faible: "Sûr",
  suspect: "Douteux",
  eleve: "Dangereux",
};

const RISK_TONE: Record<NiveauRisque, string> = {
  faible: "bg-safe-soft",
  suspect: "bg-warn-soft",
  eleve: "bg-danger-soft",
};

const RISK_DOT: Record<NiveauRisque, string> = {
  faible: "bg-[var(--safe)]",
  suspect: "bg-[var(--warn)]",
  eleve: "bg-[var(--danger)]",
};

export function RiskBadge({
  niveau,
  size = "md",
  className,
}: {
  niveau: NiveauRisque;
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  const sizeClass =
    size === "lg" ? "px-4 py-2 text-sm" : size === "sm" ? "px-2 py-0.5 text-[0.68rem]" : "px-3 py-1 text-xs";
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full font-bold uppercase tracking-wide",
        RISK_TONE[niveau],
        sizeClass,
        className
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", RISK_DOT[niveau])} aria-hidden="true" />
      {RISK_LABEL[niveau]}
    </span>
  );
}
