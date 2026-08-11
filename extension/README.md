# TrustLine — Extension navigateur (Manifest V3)

Couche de sécurité personnelle dans le navigateur : détecter les arnaques
numériques (phishing, faux gains, faux Mobile Money, liens dangereux, numéros
suspects…) **avant** qu'elles ne coûtent quelque chose. `Connecter · Protéger · Assurer`.

Éthique, privée, explicable, non intrusive. Elle **protège** l'utilisateur — elle
ne prend jamais le contrôle du navigateur.

## Architecture

```
extension/
├── manifest.json              # MV3, permissions minimales
├── src/
│   ├── lib/        config, verdict (mapping backend↔normalisé), (messaging)
│   ├── detection/  url.js, message.js, engine.js  ← moteur LOCAL, pur, testé
│   ├── api/        client.js   ← appels backend (cache, dedup, timeout, échec gracieux)
│   ├── storage/    store.js    ← chrome.storage.local (réglages, historique, id anonyme)
│   ├── background/ service-worker.js  ← routeur de messages typé, badge, notifications
│   ├── content/    selectors.js, ui.js (Shadow DOM), generic.js, whatsapp.js, gmail.js, outlook.js
│   ├── popup/       popup.{html,css,js}
│   └── options/     options.{html,css,js}  (+ centre de confidentialité)
├── public/icons/   16/32/48/128
├── fixtures/       pages de démonstration (aucune vraie page malveillante)
├── tests/          detection.test.js  (node --test)
└── scripts/        lint.mjs, build.mjs
```

Le **frontend ne décide jamais seul** : le verdict vient du moteur local
(déterministe, multi-signaux) **et** du moteur backend TrustLine (Django/DRF).
L'IA n'est jamais l'unique barrière (§50).

## Installation (développement)

```bash
# 1. Backend TrustLine lancé (depuis la racine du repo) :
python manage.py runserver          # http://127.0.0.1:8000

# 2. Charger l'extension :
Chrome → chrome://extensions → Mode développeur → « Charger l'extension non empaquetée »
        → sélectionner le dossier extension/   (ou dist/ après `npm run build`)
```

`src/lib/config.js` centralise l'URL de l'API (`API_BASE`). En production, changez-la
et ajoutez le domaine à `host_permissions` dans `manifest.json`.

## Scripts

```bash
npm run lint    # vérifie la syntaxe de tout src/ (node --check, sans dépendance)
npm test        # tests unitaires du moteur de détection (node --test)
npm run build   # génère dist/ + trustline-extension.zip
```

## Permissions Chrome (principe du moindre privilège)

| Permission | Pourquoi |
|---|---|
| `storage` | Réglages + historique **local** |
| `notifications` | Alerte uniquement en cas de **risque élevé** |
| `activeTab` | « Analyser cette page » sur clic de l'utilisateur |
| `host_permissions: http/https` | Pré-scan local des liens + intégrations WhatsApp/Gmail/Outlook |

**Jamais demandé** : `tabs` large, `history`, `cookies`, `webRequest`, `clipboard`,
`bookmarks`, `downloads`, `management`.

## Données

**Analysé (à la demande)** : le message/email **visible**, l'URL d'un lien ou de la
page active, un numéro saisi. **Local uniquement** : réglages, historique, pré-scan
des liens. **Jamais collecté** : conversations complètes, boîte mail entière, contacts,
cookies, mots de passe, frappes clavier, écran. Rien n'est envoyé au serveur sans une
analyse ou un signalement **déclenché par l'utilisateur** (consentement explicite pour
les signalements).

## API

Réutilise le backend existant. Endpoint unifié ajouté :
`POST /api/extension/analyser/` → `{ type: "url|message|email|phone", content, context }`
(dispatch vers `analyser_lien` / `analyser_message` / `verifier_numero`, aucune logique
dupliquée). Signalements : `POST /api/signalements/`.

## Fonctionnalités par plateforme

- **WhatsApp Web** — détection passive des messages visibles suspects, puis analyse à la
  demande (chip flottant « message à vérifier », panneau explicable, signalement consenti).
- **Gmail / Outlook** — indicateur sur l'email ouvert (expéditeur, objet, corps visible,
  liens) ; abstraction `MailProvider` pour isoler les sélecteurs.
- **Web** — pré-scan local des liens, **avertissement avant navigation** uniquement sur les
  liens à risque (ne casse jamais un lien sûr). Badge d'onglet selon l'heuristique locale.
- **Popup** — statut, stats du jour (local), analyse manuelle (numéro/lien/message/email),
  historique local, signalement.

Toute l'UI injectée est en **Shadow DOM** (n'altère pas WhatsApp/Gmail). Contenu analysé
rendu via `textContent` (anti-XSS). Le contenu d'un message est traité comme **donnée non
fiable** : une tentative de manipulation (« ignore previous instructions ») est comptée
comme un signal, jamais exécutée (§69).

## Démonstration jury

Servez les fixtures en HTTP pour que le content script générique s'y applique :

```bash
cd extension/fixtures && python3 -m http.server 8080
```

- `http://localhost:8080/fake-site.html` — cliquer le lien → avertissement TrustLine.
- `http://localhost:8080/whatsapp-mock.html` — cliquer le lien, ou coller le message dans la popup.
- `http://localhost:8080/gmail-mock.html` — idem pour un email de phishing.

L'intégration **native** WhatsApp/Gmail (chip contextuel) s'affiche sur les vrais domaines
(`web.whatsapp.com`, `mail.google.com`) lors de la réception d'un contenu suspect.

## Limites connues

- Sélecteurs WhatsApp/Gmail/Outlook « best-effort » : si le DOM change, l'intégration
  échoue proprement (« indisponible ») sans rien casser. Outlook est le moins éprouvé.
- Pas de Side Panel ni de bundler/TypeScript : JS natif volontaire (robustesse démo,
  zéro étape de build à casser). Les tests couvrent le moteur de détection.
- En production, restreindre le CORS backend aux origines nécessaires.
