# Checklist QA — TrustLine (site + extension + backend)

Statut au 10 août 2026, soir du Jour 1. Colonne **Vérifié** = testé réellement par moi
(backend Django local, `curl`, build Next.js, dev server). Colonne **À vérifier par vous**
= nécessite un navigateur / un humain (je n'ai pas accès à Chrome depuis mon environnement).

Backend local démarré pour ces tests : `venv` + SQLite + données de démo (7 numéros,
8→9 signalements, 4 messages). Site en dev sur `:3000`, backend sur `:8000`.

---

## 1. Backend (Django) — fondations

| # | Test | Vérifié | Détail |
|---|---|---|---|
| 1.1 | `python manage.py migrate` sans erreur | ✅ | 8 apps migrées, SQLite |
| 1.2 | `seed_demo_data` insère des données réalistes | ✅ | 7 numéros, 7 catégories, 8 signalements, 4 messages |
| 1.3 | Compte admin créé | ✅ | `admin` / voir `.env` local — **à changer avant la démo publique** |
| 1.4 | `GET /api/health/` répond | ✅ | `{"status":"ok",...}` |
| 1.5 | CORS autorise `localhost:3000` | ✅ | `access-control-allow-origin: *` confirmé en curl |
| 1.6 | Swagger UI accessible | ⬜ | `http://127.0.0.1:8000/api/docs/` — à ouvrir dans un navigateur |

## 2. Backend — endpoints métier (tous testés en curl contre la vraie DB)

| # | Endpoint | Vérifié | Résultat observé |
|---|---|---|---|
| 2.1 | `POST /api/numeros/verifier/` (numéro signalé) | ✅ | `eleve`, score 77→88 après un nouveau signalement |
| 2.2 | `POST /api/messages/analyser/` (arnaque type) | ✅ | `eleve`, score 100, indices explicites |
| 2.3 | `POST /api/signalements/` (créer) | ✅ | id retourné, `reputation_cible` mis à jour en direct |
| 2.4 | `GET /api/stats/` | ✅ | `total_signalements` passe de 8 à 9 après le test 2.3 — **preuve que l'écriture DB se répercute immédiatement** |
| 2.5 | `POST /api/liens/analyser/` | ⬜ | Schéma vérifié dans le code, pas rejoué en curl — à tester une fois l'extension chargée |
| 2.6 | `POST /api/ussd/simulate/`, `/api/bot/verifier/`, `/api/webhook/gupshup/` | ⬜ | Hors périmètre de ce passage (site + extension uniquement) |
| 2.7 | `POST /api/token/` + endpoints `/api/admin/*` (JWT) | ⬜ | Non utilisés par le site public actuel — nécessaires seulement si vous branchez un dashboard admin |

## 3. Site public (`site/`) — pages

| # | Test | Vérifié | Détail |
|---|---|---|---|
| 3.1 | `npm run build` sans erreur | ✅ | 3 routes générées (`/`, `/signaler`, `/_not-found`) |
| 3.2 | `npm run dev` démarre et sert `/` | ✅ | `GET / 200` |
| 3.3 | `/signaler` répond | ✅ | `GET /signaler 200` |
| 3.4 | `npm audit` — vulnérabilité critique Next.js | ✅ corrigée | 14.2.5 → 14.2.35 |
| 3.5 | Rendu en clair **et** en sombre (bascule OS) | ⬜ | Tokens CSS en place (`prefers-color-scheme`), à confirmer visuellement |
| 3.6 | Focus clavier visible sur tous les boutons/inputs | ⬜ | Style `:focus-visible` global défini — à re-tester au clavier |

## 4. Site public — chaque bouton, un par un

| # | Élément | Où | Action attendue | Vérifié |
|---|---|---|---|---|
| 4.1 | Champ « Analyser » (hero) | `/` | Détecte numéro/lien/message, appelle le bon endpoint, affiche score + recommandation + indices | ✅ logique + endpoints confirmés séparément — **à cliquer en vrai dans un navigateur pour voir le rendu** |
| 4.2 | Recherche rapide (nav) | `/` toutes pages | Scroll + focus vers le champ Analyser, préremplit la valeur tapée | ⬜ comportement JS à confirmer au clic |
| 4.3 | Icône compte (nav) | toutes pages | Ne fait rien, `title="bientôt disponible"` — **volontairement inactif, ce n'est pas un bug** | ✅ par design |
| 4.4 | « Signaler une arnaque » (nav + hero + Steps + footer) | toutes pages | Mène vers `/signaler` | ✅ `Link` Next.js vérifié dans le code |
| 4.5 | Formulaire de signalement | `/signaler` | Envoie à `POST /api/signalements/`, affiche la référence + réputation mise à jour | ✅ rejoué en curl avec le payload exact envoyé par le formulaire — id 9 retourné |
| 4.6 | « Télécharger l'extension (.zip) » | `/` #extension | Télécharge `trustline-extension.zip` | ✅ `GET /trustline-extension.zip → 200`, zip vérifié (16 fichiers, bons chemins) |
| 4.7 | Bandeau cookies « Accepter »/« Refuser » | toutes pages | Ferme le bandeau | ✅ `useState` simple, comportement trivial |
| 4.8 | Stats en direct (bandeau sous le hero) | `/` | Récupère `/api/stats/`, s'affiche seulement si le backend répond, sinon disparaît sans erreur visible | ✅ logique de fallback silencieux vérifiée dans le code |
| 4.9 | Liens du footer (`#extension`, `#types`, `#confidentialite`) | `/signaler` → retour `/` | Ancres vers la page d'accueil | ⬜ à cliquer pour confirmer le scroll |

## 5. Extension Chrome (`extension/`)

Je ne peux pas ouvrir Chrome depuis mon environnement — **cette section est à valider par vous**,
mais le code a été corrigé pour correspondre exactement au backend réel (avant, il ciblait
des endpoints imaginaires `/v1/...` qui n'existaient pas).

| # | Test | À vérifier par vous |
|---|---|---|
| 5.1 | Chargement non empaquetée (`chrome://extensions`) | ⬜ Le dossier `extension/` charge sans erreur de manifest |
| 5.2 | Badge de couleur sur un onglet | ⬜ Ouvrir un site quelconque → badge doit rester vide (site inconnu = « faible » par défaut, pas de faux positif) |
| 5.3 | Popup — statut du site actuel | ⬜ Doit afficher un chip Sûr/Douteux/Dangereux via `POST /api/liens/analyser/` |
| 5.4 | Popup — champ « Analyser » manuel | ⬜ Coller un texte d'arnaque type (voir §2.2) → doit afficher la recommandation réelle |
| 5.5 | Popup — « Signaler ce site » | ⬜ Ouvre `http://127.0.0.1:3000/signaler` dans un nouvel onglet |
| 5.6 | `form-guard.js` — formulaire avec champ `name="pin"` | ⬜ Sur une page de test, la soumission doit être interceptée si le site est douteux/dangereux |
| 5.7 | Comportement hors-ligne | ✅ (dans le code) | `service-worker.js` capture l'échec réseau et retourne `niveau_risque: "faible"` sans planter — **ne crée jamais un faux verdict dangereux par erreur réseau** |
| 5.8 | Icônes 16/48/128 présentes | ✅ | Générées (placeholder indigo/or), à remplacer par la vraie icône si le temps le permet |

**Important — avant de charger l'extension pour de vrai :** le `.zip` servi par le site
(`site/public/trustline-extension.zip`) doit être régénéré à chaque modification du dossier
`extension/` :
```bash
cd extension && zip -r -q ../site/public/trustline-extension.zip . -x ".*"
```

## 6. Cohérence des données (bout en bout)

| # | Test | Vérifié |
|---|---|---|
| 6.1 | Un signalement créé via le formulaire du site apparaît immédiatement dans `/api/stats/` | ✅ 8 → 9 confirmé en direct |
| 6.2 | La réputation d'un numéro augmente avec un nouveau déclarant distinct | ✅ score 77 → 88, `nombre_signalements` 4 → 5 |
| 6.3 | Un déclarant unique ne peut pas faire basculer un numéro en « élevé » à lui seul | ✅ règle documentée et implémentée côté backend (`apps/signalements/reputation.py`) — non re-testée isolément ici |
| 6.4 | Les catégories affichées dans le formulaire correspondent exactement aux codes acceptés par l'API | ✅ `CATEGORIES` dans `lib/api.ts` copié depuis `apps/core/constants.py` |

## 7. Ce qui reste à faire avant la démo finale (Jour 2)

- [ ] Ouvrir le site et l'extension dans un vrai Chrome, dérouler chaque ligne « ⬜ » ci-dessus
- [ ] Remplacer le mot de passe admin de démo avant toute exposition publique
- [ ] Décider si `/api/liens/analyser/` doit être rejoué en curl (ou juste validé via l'extension)
- [ ] Une fois le site déployé (Vercel ou autre), mettre à jour `NEXT_PUBLIC_API_URL` et le lien
      « Signaler ce site » du popup (actuellement `127.0.0.1:3000`, codé en dur pour le dev)
- [ ] Vérifier le comportement si le backend tombe pendant la démo : le site ne doit jamais
      afficher une page blanche — c'est déjà géré (`try/catch` partout dans `lib/api.ts`),
      mais à tester en coupant réellement le serveur backend une fois pour voir le message d'erreur

## 8. Ce qui n'a volontairement pas été touché

- Le moteur de détection (`apps/scoring/`), le modèle de données, l'admin Django, le webhook
  Gupshup : **aucune modification**, comme convenu — c'est le domaine du backend.
- Aucun commit ni push n'a été fait sur `github.com/70-DIDIER/trustline` : tout est en local,
  prêt à être relu avant envoi.
