import type { NiveauRisque } from "@/lib/api";

export type VerdictVisuel = NiveauRisque | "inconnu";

const TONE_BG: Record<VerdictVisuel, string> = {
  faible: "bg-safe-soft",
  suspect: "bg-warn-soft",
  eleve: "bg-danger-soft",
  inconnu: "bg-unknown-soft",
};

const TONE_TEXT: Record<VerdictVisuel, string> = {
  faible: "text-safe",
  suspect: "text-warn",
  eleve: "text-danger",
  inconnu: "text-unknown",
};

function Glyphe({ niveau }: { niveau: VerdictVisuel }) {
  switch (niveau) {
    case "faible":
      return (
        <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6">
          <path d="M12 3l7 3v5.2c0 4.8-3 8.7-7 9.8-4-1.1-7-5-7-9.8V6l7-3Z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
          <path d="M8.8 12.2l2.2 2.2 4.2-4.8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );
    case "suspect":
      return (
        <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6">
          <path d="M12 3.8l8.2 14.2H3.8L12 3.8Z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
          <line x1="12" y1="9.5" x2="12" y2="13.3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          <circle cx="12" cy="15.9" r="1" fill="currentColor" />
        </svg>
      );
    case "eleve":
      return (
        <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6">
          <polygon points="7.5,3.3 16.5,3.3 20.7,7.5 20.7,16.5 16.5,20.7 7.5,20.7 3.3,16.5 3.3,7.5" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
          <line x1="12" y1="7.8" x2="12" y2="13.2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
          <circle cx="12" cy="15.9" r="1" fill="currentColor" />
        </svg>
      );
    default:
      return (
        <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6">
          <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.7" />
          <path d="M9.6 9.4a2.4 2.4 0 114.1 1.7c-.9.8-1.7 1.2-1.7 2.4" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
          <circle cx="12" cy="16.2" r="1" fill="currentColor" />
        </svg>
      );
  }
}

export function VerdictIcon({ niveau, size = 56 }: { niveau: VerdictVisuel; size?: number }) {
  return (
    <span
      className={`inline-flex flex-none items-center justify-center rounded-2xl ${TONE_BG[niveau]} ${TONE_TEXT[niveau]}`}
      style={{ width: size, height: size }}
    >
      <Glyphe niveau={niveau} />
    </span>
  );
}
