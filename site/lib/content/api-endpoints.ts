// Documentation semi-automatique : endpoints copiés du schéma DRF réel du backend
// (config/urls.py + apps/*/urls.py). Le schéma OpenAPI complet et à jour reste
// disponible en direct sur /api/docs/ (Swagger) et /api/schema/.

export interface EndpointDoc {
  methode: "GET" | "POST";
  chemin: string;
  resume: string;
  requete?: string;
  reponse: string;
}

export const ENDPOINTS: EndpointDoc[] = [
  {
    methode: "GET",
    chemin: "/api/health/",
    resume: "Vérifier que le service est disponible.",
    reponse: `{
  "status": "ok",
  "service": "trustline",
  "time": "2026-08-10T21:59:05.099817+00:00"
}`,
  },
  {
    methode: "POST",
    chemin: "/api/numeros/verifier/",
    resume: "Vérifier un numéro (liste blanche + réputation communautaire).",
    requete: `{ "numero": "+22890112233" }`,
    reponse: `{
  "numero": "+22890112233",
  "score": 77,
  "niveau_risque": "eleve",
  "est_liste_blanche": false,
  "organisation": null,
  "nombre_signalements": 4,
  "categories": ["demande_otp_pin", "fraude_financiere"],
  "indices": ["4 signalement(s) communautaire(s)."],
  "recommandation": "Numéro à haut risque : signalé par la communauté…"
}`,
  },
  {
    methode: "POST",
    chemin: "/api/messages/analyser/",
    resume: "Analyser un SMS ou un message libre.",
    requete: `{ "contenu": "Felicitations! Vous avez gagne 500000 FCFA, envoyez votre code OTP" }`,
    reponse: `{
  "score": 100,
  "niveau_risque": "eleve",
  "indices": ["Demande d'un code OTP / PIN.", "Promesse de gain."],
  "recommandation": "Danger élevé : très probablement une arnaque…",
  "categories": ["demande_otp_pin", "faux_concours"],
  "liens_extraits": [],
  "numeros_extraits": []
}`,
  },
  {
    methode: "POST",
    chemin: "/api/liens/analyser/",
    resume: "Analyser une URL avant de l'ouvrir.",
    requete: `{ "url": "http://ecobank-tg.xyz/login" }`,
    reponse: `{
  "url": "http://ecobank-tg.xyz/login",
  "domaine": "ecobank-tg.xyz",
  "score": 78,
  "niveau_risque": "suspect",
  "indices": ["Domaine imitant une marque connue (typosquat)."],
  "recommandation": "Ne saisissez aucune donnée sur ce site."
}`,
  },
  {
    methode: "POST",
    chemin: "/api/signalements/",
    resume: "Créer un signalement communautaire (numéro, SMS, lien, message).",
    requete: `{
  "type_cible": "numero",
  "cible": "90112233",
  "categorie": "demande_otp_pin",
  "declarant_id": "web-anonyme-abc123"
}`,
    reponse: `{
  "id": 9,
  "statut": "en_attente",
  "message": "Merci, votre signalement a bien été enregistré.",
  "reputation_cible": { "numero": "+22890112233", "score_risque": 88, "niveau_risque": "eleve" }
}`,
  },
  {
    methode: "GET",
    chemin: "/api/stats/",
    resume: "Statistiques publiques agrégées.",
    reponse: `{
  "total_signalements": 9,
  "total_numeros_suivis": 7,
  "total_analyses": 6,
  "signalements_par_categorie": [ { "categorie__code": "fraude_financiere", "total": 3 } ]
}`,
  },
  {
    methode: "GET",
    chemin: "/api/alertes/",
    resume: "Alertes publiques (catégories actives, dérivées des signalements réels).",
    reponse: `[
  { "categorie": "fraude_financiere", "libelle": "Fraude financière", "nombre_signalements": 3, "niveau_risque": "eleve" }
]`,
  },
];
