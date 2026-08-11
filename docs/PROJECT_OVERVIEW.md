# TrustLine

Prototype développé pendant le Hackathon des Togo IT Days 2026 — « Cyber Innovation Challenge »,
Mission 2 : Stop Arnaques Numériques.

## Structure

```
site/         Site officiel public (Next.js + Tailwind) — en cours
extension/    Extension Chrome (Manifest V3) — squelette fonctionnel prêt à charger
docs/         Roadmaps étape par étape par composant
```

## Démarrer

```bash
cd site && npm install && npm run dev   # http://localhost:3000
```

Extension : `chrome://extensions` → mode développeur → *Charger l'extension non empaquetée* → dossier `extension/`.

## Répartition de l'équipe

| Rôle | Composant |
|---|---|
| Cybersc 1 | Moteur de règles + intégration threat intel |
| Cybersc 2 | Back-office supervision + sécurité (chiffrement, minimisation, loi 2019-014) |
| IA | Collecte du corpus + entraînement + métriques |
| Dev 1 | App Android + bot |
| Dev 2 | API backend + dashboard + démo/vidéo de secours |
| **Web** | Site officiel (`site/`) |
| **Extension** | Extension Chrome (`extension/`) |

## Roadmaps

- [docs/roadmap-site.md](docs/roadmap-site.md)
- [docs/roadmap-extension.md](docs/roadmap-extension.md)

## Conformité

Aucune collecte de répertoire, anonymisation avant stockage, conçu conformément à la loi
togolaise n°2019-014. Voir la section confidentialité du site public.
