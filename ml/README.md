# Modèle ML Trustline

Le moteur fonctionne **sans ML** (règles). Ce dossier permet d'entraîner un
modèle qui vient *compléter* les règles, sans toucher aux endpoints.

## Entraîner

```bash
# depuis la racine du projet
pip install -r requirements-ml.txt
python ml/train_model.py
```
Produit `ml/trustline_model.joblib` et affiche un rapport de performance.

## Activer dans l'API

Dans `.env` :
```env
ML_MODEL_PATH=ml/trustline_model.joblib
ML_POIDS=0.5
```
Redémarre le serveur : au démarrage, `apps/scoring/apps.py::ready()` charge le
modèle et le branche sur le moteur. Tous les endpoints (messages, bot, WhatsApp,
USSD) utilisent alors **règles + ML**. Si le fichier est absent ou illisible →
retour automatique au mode règles (aucune erreur).

## Enrichir le dataset

`ml/dataset.csv` — colonnes `texte,label` (`1` = arnaque, `0` = légitime).
Ajoute de vrais exemples togolais (FR + éwé, avec/sans accents) pour améliorer le
modèle, puis relance l'entraînement.

## Rappels

- Garde un modèle **simple** (LogisticRegression / NaiveBayes) tant que le
  dataset est petit — plus explicable et moins de surapprentissage.
- Le ML **complète** les règles, il ne les remplace pas : les règles restent le
  filet de sécurité explicable.
- Le modèle est un pipeline scikit-learn exposant `predict_proba` (attendu par
  `apps/scoring/engine.py`).
