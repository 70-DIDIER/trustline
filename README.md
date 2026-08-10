# Trustline — Backend (TOGOSHIELD)

Plateforme intelligente, multicanale et inclusive de **détection, prévention et
signalement des arnaques numériques** pour les citoyens togolais.
_Hackathon Togo IT Days 2026 — Mission 2 « Stop Arnaques Numériques »._

Inspiré du modèle communautaire de **Truecaller**, mais élargi à une question plus
large : _« Puis-je faire confiance à cette interaction numérique ? »_ (numéro, SMS,
lien, site, message), et pensé **multicanal** (Web, USSD, extension navigateur, bot de
messagerie) pour ne pas exclure les utilisateurs sans smartphone.

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
| `POST` | `/api/ussd/simulate/` | Simuler un parcours USSD |
| `POST` | `/api/bot/verifier/` | Webhook bot (verdict conversationnel) |
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

### Brancher un modèle ML (scikit-learn) plus tard
Aucune réécriture des endpoints :
```python
from apps.scoring.engine import MoteurDetection
moteur = MoteurDetection(ml_model=mon_modele, poids_ml=0.5)  # predict_proba OU callable
```

---

## 🛡️ Réputation communautaire & anti-abus

`apps/signalements/reputation.py` — **un signalement isolé ne peut jamais** faire
basculer un numéro en « risque élevé ». Le score combine :

- le **nombre de déclarants distincts** (plafond dur : 1 déclarant → « suspect » max) ;
- la **récence** des signalements (décroissance exponentielle, demi-vie ~30 jours) ;
- la **diversité des catégories** signalées.

_Démo (`seed_demo_data`) : 4 déclarants → **ELEVE**, 3 → **SUSPECT**, 1 seul → **FAIBLE**._

---

## 🗂️ Structure du projet

```
config/                 # settings, urls, wsgi/asgi
apps/
  core/                 # référentiels (catégories, liste blanche, logs) + utils partagés
  scoring/              # MoteurDetection (règles + interface ML)
  numeros/              # vérification / consultation de numéros
  signalements/         # signalement communautaire + réputation
  messages/             # analyse SMS / messages (label "messages_app")
  liens/                # analyse de liens / sites (extension Chrome)
  ussd/                 # simulateur USSD
  bot/                  # webhook bot de messagerie
  moderation/           # statistiques du dashboard
tests/                  # tests pytest (scoring + API end-to-end)
```

---

## 🧪 Tests

```bash
pytest
```
Couvre le moteur de détection et les endpoints principaux (health, numéros, messages,
signalements, liens, USSD, bot).

---

## 🔐 Sécurité & choix

- **Rate limiting** sur les endpoints publics (throttling DRF adossé au cache).
- **Validation stricte** des entrées via les serializers DRF.
- **JWT** pour les endpoints d'administration / modération.
- **Aucune collecte de carnet d'adresses** — la réputation repose uniquement sur les
  signalements volontaires et la liste blanche. Les déclarants sont anonymisés.
```
