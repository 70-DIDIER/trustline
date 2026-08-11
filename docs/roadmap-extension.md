# Roadmap — Extension Chrome TrustLine (Manifest V3)

Dossier : `extension/`. Le squelette fonctionnel est déjà en place.

## Déjà fait (scaffold initial)

- [x] `manifest.json` (MV3, permissions minimales, host_permissions `<all_urls>`)
- [x] Icônes 16/48/128 (placeholders générés — à remplacer par la vraie icône si le temps le permet)
- [x] `background/service-worker.js` — vérifie le domaine à chaque changement d'onglet, met à jour le badge (rouge/orange/vert), notifie si dangereux, expose deux messages (`VERIFIER_DOMAINE`, `ANALYSER_TEXTE`) pour le popup et les content scripts
- [x] `content/scanner.js` — affiche un bandeau plein écran si le site est dangereux
- [x] `content/form-guard.js` — intercepte la soumission d'un formulaire contenant un champ sensible (PIN, mot de passe, carte, OTP) sur un site douteux/dangereux
- [x] `popup/` — popup complet (statut du site actuel, champ d'analyse manuelle, stats, bouton signaler), déjà stylé aux couleurs TrustLine

**Mise à jour : branché sur le vrai backend Django** (`github.com/70-DIDIER/trustline`,
pas le FastAPI imaginaire du premier jet). Endpoints réels : `POST /api/liens/analyser/`
et `POST /api/messages/analyser/`, niveaux `faible|suspect|eleve`. Testé en curl côté
backend (voir [`QA-CHECKLIST.md`](QA-CHECKLIST.md)) — reste à tester dans un vrai Chrome.

## Comment tester dès maintenant

1. `cd extension && zip -r -q ../site/public/trustline-extension.zip . -x ".*"` si vous venez de modifier le code (le site sert ce zip pour le téléchargement)
2. `chrome://extensions` → activer le mode développeur → **Charger l'extension non empaquetée** → sélectionner `extension/`
3. Démarrer le backend (`python manage.py runserver` depuis la racine du repo) — sans lui, tout fonctionne en mode dégradé (`niveau_risque: "faible"` par défaut, jamais de crash)

## Jour 1

- [ ] Vérifier que le badge change de couleur sur un vrai exemple (coller un lien type `http://ecobank-tg.xyz/login` dans le popup)
- [ ] Tester `form-guard.js` sur une page de test avec un champ `name="pin"` — confirmer que la popup d'avertissement bloque bien la soumission
- [x] URL du bouton "Signaler ce site" branchée sur `http://127.0.0.1:3000/signaler` — **à changer pour l'URL de prod une fois le site déployé**

## Jour 2

- [ ] Remplacer les icônes placeholder par la vraie icône TrustLine (même geste que celui du site — cercle/bouclier + point or)
- [ ] Tester sur 2-3 vrais sites togolais connus (banque, opérateur) pour vérifier qu'ils remontent bien `sûr` et pas de faux positif — **un faux positif sur orabank.tg pendant la démo tue la crédibilité**
- [ ] Empaqueter en `.zip` (Chrome Web Store non nécessaire — chargement "non empaquetée" suffit pour le jury, mais préparer le zip en secours)
- [ ] Vérifier que rien ne casse si le backend est injoignable pendant la démo (déjà géré côté service worker — à re-tester en debranchant le wifi)

## Ne pas faire (hors scope 48h)

- Publication sur le Chrome Web Store (validation = plusieurs jours)
- Manifest V2 / support Firefox
- Blocage automatique de navigation (`declarativeNetRequest` dynamique) — rester sur bandeau d'avertissement + confirmation, plus simple à défendre en Q&A
