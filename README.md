# Trustline — Backend (TOGOSHIELD)

Plateforme intelligente, multicanale et inclusive de **détection, prévention et
signalement des arnaques numériques** pour les citoyens togolais.
_Hackathon Togo IT Days 2026 — Mission 2 « Stop Arnaques Numériques »._

Inspiré du modèle communautaire de **Truecaller**, mais élargi à une question plus
large : _« Puis-je faire confiance à cette interaction numérique ? »_ (numéro, SMS,
lien, site, message), et pensé **multicanal** (Web, USSD, extension navigateur, bot de
messagerie) pour ne pas exclure les utilisateurs sans smartphone.

> Ce fichier documente le **backend** (ce dossier racine). Le **site public** vit dans
> [`site/`](site/) (Next.js) et l'**extension Chrome** dans [`extension/`](extension/) —
> voir [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md) pour la vue d'ensemble et
> [`docs/roadmap-site.md`](docs/roadmap-site.md) / [`docs/roadmap-extension.md`](docs/roadmap-extension.md)
> pour l'avancement de chaque composant.

---

## 🧱 Stack technique

| Élément | Choix |
|---|---|
| Framework | Django 5 + Django REST Framework |
| Base de données | PostgreSQL 18 (**fallback SQLite** par défaut) |
| Cache / rate limiting | Redis (**fallback cache mémoire** par défaut) |
| Auth API (admin/modération) | JWT (`djangorestframework-simplejwt`) |
| Documentation API | `drf-spectacular` (Swagger / OpenAPI) |
| Variables d'env | `django-environ` |

> ⚙️ **Sans Docker.** Le projet tourne en local directement. Grâce aux fallbacks,
> un coéquipier peut cloner et lancer le serveur en 2 minutes **sans installer
> PostgreSQL ni Redis**. Ceux-ci se branchent plus tard via `.env`, sans changer le code.

---

## 🚀 Démarrage rapide (local)

```bash
# 1. Environnement virtuel
python -m venv .venv
.\.venv\Scripts\activate          # Windows (PowerShell)
# source .venv/bin/activate       # Linux / macOS

# 2. Dépendances
pip install -r requirements.txt

# 3. Configuration (optionnel — des défauts sains existent)
copy .env.example .env            # Windows
# cp .env.example .env            # Linux / macOS

# 4. Base de données + données de démo
python manage.py migrate
python manage.py seed_demo_data   # arnaques Mobile Money togolaises réalistes

# 5. Compte administrateur (dashboard + endpoints protégés)
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```

Le serveur tourne sur <http://127.0.0.1:8000/>.

### Passer à PostgreSQL / Redis (optionnel)
Dans `.env`, décommentez :
```env
DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/trustline
CACHE_URL=redis://127.0.0.1:6379/1
```
puis relancez `migrate`. Aucun changement de code nécessaire.

---

## 📚 Documentation de l'API

- **Swagger UI** : <http://127.0.0.1:8000/api/docs/>
- **Schéma OpenAPI** : <http://127.0.0.1:8000/api/schema/>
- **Dashboard admin** : <http://127.0.0.1:8000/admin/>

### Format de réponse normalisé (tous les verdicts)
```json
{
  "score": 0-100,
  "niveau_risque": "faible | suspect | eleve",
  "indices": ["raisons explicatives…"],
  "recommandation": "conseil court à afficher"
}
```

### Endpoints principaux (P0)

| Méthode | Endpoint | Rôle |
|---|---|---|
| `GET`  | `/api/health/` | Vérifier que le service tourne |
| `POST` | `/api/numeros/verifier/` | Vérifier un numéro (liste blanche + réputation) |
| `GET`  | `/api/numeros/{numero}/` | Consulter un numéro en base |
| `POST` | `/api/messages/analyser/` | Analyser un SMS / message |
| `POST` | `/api/liens/analyser/` | Analyser un lien / site (extension Chrome) |
| `POST` | `/api/signalements/` | Signaler + mettre à jour la réputation |
| `POST` | `/api/ussd/simulate/` | Simuler un parcours USSD (JSON, pour le front) |
| `POST` | `/api/ussd/africastalking/` | Webhook USSD réel (passerelle Africa's Talking) |
| `POST` | `/api/bot/verifier/` | Webhook bot (verdict conversationnel) |
| `POST` | `/api/webhook/gupshup/` | Webhook WhatsApp entrant (Gupshup) — voir section dédiée |
| `GET`  | `/api/stats/` | Statistiques agrégées (dashboard) |
| `POST` | `/api/token/` | Obtenir un token JWT (admin/modération) |

### Exemples (PowerShell / curl)
```bash
# Analyser un SMS d'arnaque
curl -X POST http://127.0.0.1:8000/api/messages/analyser/ \
  -H "Content-Type: application/json" \
  -d '{"contenu":"Felicitations! Vous avez gagne 500000 FCFA, envoyez votre code OTP"}'

# Vérifier un numéro
curl -X POST http://127.0.0.1:8000/api/numeros/verifier/ \
  -H "Content-Type: application/json" -d '{"numero":"+22890112233"}'

# Signaler un numéro
curl -X POST http://127.0.0.1:8000/api/signalements/ \
  -H "Content-Type: application/json" \
  -d '{"type_cible":"numero","cible":"90112233","categorie":"demande_otp_pin","declarant_id":"user-42"}'
```

---

## 🧠 Moteur de détection (v1 — règles, ML-ready)

Le cœur est `apps/scoring/` :

- **`rules.py`** — règles pondérées, transparentes et explicables : demande OTP/PIN,
  urgence artificielle, promesse de gain, demande de transfert, usurpation de service
  officiel, lien raccourci/suspect.
- **`engine.py`** — la classe `MoteurDetection` combine le **score des règles**, la
  **réputation communautaire** injectée, et un **modèle ML optionnel**.
- **`lexique_ewe.py`** — lexique **éwé** fusionné automatiquement dans les règles
  (base à valider par un locuteur natif). Ajouter une langue = ajouter un lexique,
  sans toucher au moteur.

### Robustesse aux SMS réels
`apps/core/utils.normaliser_texte` normalise le texte **avant** les règles :
suppression des accents, minuscules, espaces insécables/zero-width. Un vrai SMS
togolais tapé « à l'arrache » (`FELICITATIONS envoyez votre code otp`, sans accents,
en majuscules) est détecté aussi sûrement que sa version soignée. Les lettres
spéciales éwé (ɔ ɖ ƒ ŋ ʋ) sont préservées, avec tolérance de la variante ASCII clavier.

### Brancher un modèle ML (scikit-learn)
Aucune réécriture des endpoints. Le moteur accepte un modèle sklearn
(`predict_proba`) ou un simple callable :
```python
from apps.scoring.engine import MoteurDetection
moteur = MoteurDetection(ml_model=mon_modele, poids_ml=0.5)
```
En pratique, tout est scaffoldé dans **`ml/`** :
```bash
pip install -r requirements-ml.txt      # deps ML (séparées, hors serveur)
python ml/train_model.py                # entraîne -> ml/trustline_model.joblib
# puis dans .env :  ML_MODEL_PATH=ml/trustline_model.joblib
```
Au démarrage, `apps/scoring/apps.py::ready()` charge le modèle et l'active
automatiquement (mélange règles + ML). Fichier absent → retour au mode règles.
Détails : **`ml/README.md`**.

---

## 💬 Intégration WhatsApp (Gupshup Sandbox)

Trustline peut être interrogé **directement depuis WhatsApp** : l'utilisateur colle le
message suspect, le bot renvoie le verdict. Le pont est assuré par le webhook
`POST /api/webhook/gupshup/`, qui réutilise exactement la même logique que
`/api/bot/verifier/` (factorisée dans `apps/bot/services.py::analyser_pour_bot`).

**Principe :** Gupshup pousse le message WhatsApp entrant sur le webhook → Trustline
analyse le texte → la réponse est renvoyée à l'utilisateur via l'API sortante de Gupshup.

### 1. Configurer la clé API dans `.env`
```env
GUPSHUP_API_KEY=ta_cle_gupshup_sandbox
GUPSHUP_SOURCE=917834811114        # numéro sandbox Gupshup (défaut fourni)
GUPSHUP_APP_NAME=TrustLine
```

### 2. Exposer le webhook publiquement
Gupshup doit pouvoir atteindre ton serveur. En local, utilise un tunnel :
```bash
# exemple avec ngrok
ngrok http 8000
```
En production, c'est ton domaine VPS (voir `DEPLOY.md`).

### 3. Déclarer l'URL du webhook côté Gupshup
Dans la console Gupshup (**Sandbox → Callback URL**), renseigne :
```
https://<ton-domaine-ou-tunnel>/api/webhook/gupshup/
```

### 4. Tester
Envoie « join <mot-sandbox> » au numéro sandbox depuis ton WhatsApp, puis colle un
message d'arnaque. Tu peux aussi simuler l'appel entrant sans WhatsApp :
```bash
curl -X POST http://127.0.0.1:8000/api/webhook/gupshup/ \
  -H "Content-Type: application/json" \
  -d '{
    "app":"TrustLine","type":"message",
    "payload":{
      "source":"22890429399","type":"text",
      "payload":{"text":"Felicitations vous avez gagne 500000 FCFA, envoyez votre code OTP"},
      "sender":{"phone":"22890429399","name":"Kofi"}
    }
  }'
```

### Comportement (robuste pour un webhook)
- **Répond toujours HTTP 200** (accusé de réception) — Gupshup ne réémet pas en boucle.
- **Envoi WhatsApp asynchrone** (thread) : l'accusé part immédiatement.
- **Salutation** (« salut », « hello », « bonjour », « aide », « menu », « ? ») → renvoie un
  **guide d'utilisation** brandé Trustline (un vrai SMS commençant par « Bonjour… » reste analysé).
- **Message à risque** → verdict brandé *Trustline* + CTA : vérifier sur l'app/site Trustline,
  signaler au CERT-TG / ANCY.
- **Message sans texte** (image seule) → réponse « je ne peux analyser que du texte ».
- **Erreur / timeout Gupshup** → journalisée, jamais propagée.
- **Logs clairs** à chaque étape (logger `trustline.gupshup`, visibles dans la console).
- **CSRF désactivé** (webhook externe, `authentication_classes = []`).

---

## 🛡️ Réputation communautaire & anti-abus

`apps/signalements/reputation.py` — **un signalement isolé ne peut jamais** faire
basculer un numéro en « risque élevé ». Le score combine :

- le **nombre de déclarants distincts** (plafond dur : 1 déclarant → « suspect » max) ;
- la **récence** des signalements (décroissance exponentielle, demi-vie ~30 jours) ;
- la **diversité des catégories** signalées.

_Démo (`seed_demo_data`) : 4 déclarants → **ELEVE**, 3 → **SUSPECT**, 1 seul → **FAIBLE**._

---

## 🛠️ API d'administration (dashboard back-office)

En plus de l'admin Django natif (`/admin/`), une **API REST d'administration** permet à un
front-end (Next.js) de construire son propre dashboard. **Tous ces endpoints exigent un
token JWT d'un compte staff** (`Authorization: Bearer <token>`), obtenu via `POST /api/token/`.

| Méthode | Endpoint | Rôle |
|---|---|---|
| `GET` | `/api/admin/signalements/` | Lister/filtrer (`?statut=`, `?categorie=`, `?type_cible=`, `?search=`, `?ordering=`) |
| `POST` | `/api/admin/signalements/{id}/moderer/` | Modérer : `{"action":"valide\|conteste\|rejete"}` → recalcule la réputation |
| `POST` | `/api/admin/signalements/moderer-lot/` | Modérer plusieurs : `{"ids":[...],"action":"..."}` |
| `GET` | `/api/admin/signalements/export/` | Export CSV des signalements (filtres appliqués) |
| `GET` | `/api/admin/numeros/` | Lister les numéros (`?niveau_risque=`, `?search=`, `?ordering=`) |
| `POST` | `/api/admin/numeros/{id}/liste-blanche/` | Ajouter à la liste blanche |
| `GET` | `/api/admin/numeros/{id}/signalements/` | Signalements liés à ce numéro |
| `GET`/`POST`/`DELETE` | `/api/admin/liste-blanche/` | CRUD des numéros officiels |
| `GET` | `/api/admin/messages/` | Messages analysés (`?verdict=`, `?search=`) |
| `GET` | `/api/admin/logs/` | Logs d'analyse (`?type_cible=`, `?source=`, `?search=`) |
| `GET` | `/api/admin/categories/` | Référentiel des catégories |
| `GET` | `/api/stats/` | Synthèse dashboard (public) |

Les listes sont **paginées** (`?page=`, 20/page), **cherchables** (`?search=`) et
**triables** (`?ordering=-date_creation`). Exemple :
```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"motdepasse"}' | jq -r .access)

curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8000/api/admin/signalements/?statut=en_attente"
```

---

## 📟 USSD réel (Africa's Talking sandbox)

L'endpoint `POST /api/ussd/africastalking/` est un **webhook pour une vraie passerelle
USSD**. Il reçoit le format Africa's Talking (form-urlencoded : `sessionId`, `serviceCode`,
`phoneNumber`, `text`) et répond en **texte brut** préfixé `CON ` (menu, session ouverte) ou
`END ` (fin). Il réutilise la même logique que le simulateur JSON (`traiter_ussd`).

### Tester avec le simulateur Africa's Talking
1. **Exposer le serveur local** :
   ```bash
   ngrok http 8000     # -> https://xxxx.ngrok-free.app
   ```
2. Dans le **sandbox AT** (Créer un canal USSD), renseigne la **Callback URL** :
   ```
   https://xxxx.ngrok-free.app/api/ussd/africastalking/
   ```
   AT t'attribue un code de test (ex. `*384*NNNN#`).
3. **Lance le simulateur USSD** d'AT : saisis un numéro, compose le code → le menu Trustline
   s'affiche, servi par ton serveur (regarde les logs `runserver`).

### Tester en local (format AT)
```bash
curl -X POST http://127.0.0.1:8000/api/ussd/africastalking/ \
  -d "sessionId=abc&phoneNumber=+22890000111&text=1*90112233"
# -> END Numéro +22890112233  Risque: ELEVE (77/100) ...
```

> ℹ️ Le sandbox/simulateur AT est un **vrai flux USSD de bout en bout via leur passerelle**
> — mais ce n'est pas encore une SIM composant un code court togolais. Passer sur un code
> réel en production nécessite le processus « go live » d'Africa's Talking + la couverture
> opérateur.

---

## 🗂️ Structure du projet

```
config/                 # settings, urls, wsgi/asgi
apps/
  core/                 # référentiels (catégories, liste blanche, logs) + utils partagés
  scoring/              # MoteurDetection (règles + lexique éwé + interface ML)
  numeros/              # vérification / consultation de numéros
  signalements/         # signalement communautaire + réputation
  messages/             # analyse SMS / messages (label "messages_app")
  liens/                # analyse de liens / sites (extension Chrome)
  ussd/                 # simulateur USSD
  bot/                  # bot messagerie : services.py (logique partagée) + webhooks.py (Gupshup)
  moderation/           # API admin REST (JWT) : signalements, numéros, liste blanche, stats
ml/                     # entraînement du modèle ML (train_model.py, dataset.csv) — optionnel
tests/                  # tests pytest (scoring, API end-to-end, webhook Gupshup, ML)
DEPLOY.md               # runbook de déploiement VPS (Nginx + Gunicorn + HTTPS)
```

---

## 🧪 Tests

```bash
pytest
```
**35 tests** couvrant :
- le **moteur de détection** (règles, robustesse sans-accents/majuscules/espaces, lexique éwé) ;
- les **endpoints** end-to-end (health, numéros + formats variés, messages, signalements
  anti-abus, liens, USSD, bot) ;
- le **webhook WhatsApp Gupshup** (parsing, cas limites, envoi sortant) ;
- le **chargement du modèle ML** (fallback règles si absent).

---

## 🔐 Sécurité & choix

- **Rate limiting** sur les endpoints publics (throttling DRF adossé au cache).
- **Validation stricte** des entrées via les serializers DRF.
- **JWT** pour les endpoints d'administration / modération.
- **Aucune collecte de carnet d'adresses** — la réputation repose uniquement sur les
  signalements volontaires et la liste blanche. Les déclarants sont anonymisés.
- **Durcissement HTTPS automatique en prod** (`DEBUG=False`) : redirection SSL,
  cookies `Secure`, HSTS, `CSRF_TRUSTED_ORIGINS`, `SECURE_PROXY_SSL_HEADER` (Nginx),
  `X_FRAME_OPTIONS=DENY`. Neutre en dev, surchargeable via `.env`.

---

## 🚢 Déploiement

Runbook complet pour un VPS Ubuntu (sans Docker) : **`DEPLOY.md`**
— Gunicorn + Nginx + PostgreSQL + Redis + systemd + Let's Encrypt.
