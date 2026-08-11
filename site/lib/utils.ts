export type TypeEntree = "numero" | "lien" | "message";

// Détection heuristique du type d'entrée collée dans un champ "Analyser" générique.
export function detecterTypeEntree(valeur: string): TypeEntree {
  const v = valeur.trim();
  const chiffres = v.replace(/[^0-9]/g, "");
  if (chiffres.length >= 8 && chiffres.length <= 15 && chiffres.length / v.length > 0.6) {
    return "numero";
  }
  if (/^https?:\/\//i.test(v) || /^[a-z0-9-]+(\.[a-z0-9-]+)+(\/\S*)?$/i.test(v)) {
    return "lien";
  }
  return "message";
}

// Identifiant déclarant anonyme, persistant sur l'appareil (pas de compte requis,
// pas de PII — juste assez pour que l'anti-abus du backend détecte les déclarants distincts).
export function getDeclarantId(): string {
  if (typeof window === "undefined") return "server";
  const KEY = "trustline_declarant_id";
  let id = window.localStorage.getItem(KEY);
  if (!id) {
    id = `web-${crypto.randomUUID()}`;
    window.localStorage.setItem(KEY, id);
  }
  return id;
}

// Masque un numéro pour tout affichage PUBLIC (listes, statistiques, alertes).
// Ne jamais utiliser sur un numéro que l'utilisateur vient lui-même de saisir.
// +22890112233 -> +228 90 •• •• 33   |   90112233 -> 90 •• •• 33
export function maskNumero(numero: string): string {
  const digits = numero.replace(/[^0-9]/g, "");
  if (digits.length < 6) return numero;

  const indicatif = numero.startsWith("+228") ? "+228" : "";
  const local = indicatif ? digits.slice(3) : digits; // 8 chiffres attendus (Togo)

  const debut = local.slice(0, 2);
  const fin = local.slice(-2);
  const milieu = local.slice(2, -2);
  const milieuMasque = milieu.replace(/../g, "•• ").trim();

  return [indicatif, debut, milieuMasque, fin].filter(Boolean).join(" ");
}

export function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Intl.DateTimeFormat("fr-FR", { day: "2-digit", month: "short", year: "numeric" }).format(
    new Date(iso)
  );
}

export function formatDateHeure(iso: string | null): string {
  if (!iso) return "—";
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

export function formatRelatif(iso: string | null): string {
  if (!iso) return "—";
  const diffMs = Date.now() - new Date(iso).getTime();
  const diffMin = Math.round(diffMs / 60000);
  if (diffMin < 1) return "à l'instant";
  if (diffMin < 60) return `il y a ${diffMin} min`;
  const diffH = Math.round(diffMin / 60);
  if (diffH < 24) return `il y a ${diffH} h`;
  const diffJ = Math.round(diffH / 24);
  if (diffJ < 30) return `il y a ${diffJ} j`;
  return formatDate(iso);
}

export function cn(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(" ");
}
