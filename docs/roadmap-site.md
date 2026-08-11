# Roadmap — Site officiel TrustLine (Next.js)

Dossier : `site/`. Stack : Next.js 14 (App Router) + Tailwind + tokens TrustLine.
Backend réel : Django + DRF (`github.com/70-DIDIER/trustline`), déjà branché via `lib/api.ts`.

## Fait

- [x] Projet Next.js + Tailwind + TypeScript configuré, vulnérabilité Next.js patchée
- [x] Redesign : fond blanc dominant, accents indigo/or en touches fines, cartes avec ombre légère
- [x] Tokens de couleur clair/sombre (`app/globals.css`)
- [x] Nav sticky + bandeau défilant de signalements (`Navbar`, `Ticker`)
- [x] Hero **interactif** : détecte numéro/lien/message et appelle le bon endpoint réel
- [x] Bande de statistiques ANCy (source externe, citée) + bande "TrustLine en direct" (`/api/stats/`)
- [x] 3 piliers, couverture des canaux, catalogue de 9 types d'arnaques
- [x] Section extension avec vrai lien de téléchargement (`/trustline-extension.zip`) + étapes de sideload
- [x] Page `/signaler` avec formulaire complet → `POST /api/signalements/`, réputation affichée en retour
- [x] Section confidentialité (loi 2019-014) + bandeau "à propos" honnête
- [x] Footer + bandeau cookies (redesignés)
- [x] `lib/api.ts` — client typé pour tous les endpoints publics du backend réel

Détail des tests effectués : voir [`QA-CHECKLIST.md`](QA-CHECKLIST.md).

## Reste à faire

- [ ] Tester au clavier (focus visible) et en dark mode dans un vrai navigateur
- [ ] Page `/alertes` (campagnes actives) — pas d'endpoint backend dédié pour l'instant, à voir avec l'équipe backend si utile
- [ ] Déployer (Vercel, ou `npm run build && npm run start` en local si le wifi du Palais est trop instable)
- [ ] Mettre à jour `NEXT_PUBLIC_API_URL` vers l'URL de prod du backend une fois déployé
- [ ] Remettre à jour le lien "Signaler ce site" du popup extension (actuellement `127.0.0.1:3000` en dur)

## Ne pas faire (hors scope 48h)

- Système de compte utilisateur complet (auth, sessions) — l'icône compte reste un placeholder visuel assumé
- Blog / CMS
- Multi-langue (français uniquement pour la démo)
