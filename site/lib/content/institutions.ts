// Vérifiées manuellement via recherche web avant intégration — jamais de lien deviné.
export interface Institution {
  href: string;
  label: string;
  desc: string;
}

export const INSTITUTIONS: Institution[] = [
  {
    href: "https://ancy.gouv.tg/",
    label: "Agence Nationale de la Cybersécurité (ANCy)",
    desc: "Autorité togolaise en charge de la stratégie nationale de cybersécurité.",
  },
  {
    href: "https://cert.tg/",
    label: "CERT.tg",
    desc: "Centre national de réponse aux incidents de cybersécurité au Togo.",
  },
];
