"""Entraînement du modèle de détection d'arnaques Trustline.

Usage :
    # 1. installer les deps ML
    pip install -r requirements-ml.txt
    # 2. entraîner (depuis la racine du projet)
    python ml/train_model.py

Produit : ml/trustline_model.joblib  (pipeline scikit-learn avec predict_proba).
Ensuite, dans .env : ML_MODEL_PATH=ml/trustline_model.joblib  → le moteur
utilise automatiquement règles + ML (voir apps/scoring/apps.py).

Choix techniques (défendables au jury)
--------------------------------------
* Même normalisation qu'en production (apps.core.utils.normaliser_texte) → pas
  d'écart entraînement/inférence.
* N-grammes de CARACTÈRES (char_wb 3-5) → robustes aux fautes, au sans-accent,
  et au multilingue (éwé) sans vocabulaire figé.
* LogisticRegression → léger, explicable, expose predict_proba (requis par le
  moteur). class_weight="balanced" pour gérer un dataset déséquilibré.
"""
import os
import sys
from pathlib import Path

# --- Bootstrap Django pour réutiliser normaliser_texte -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

import joblib  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import classification_report  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402

from apps.core.utils import normaliser_texte  # noqa: E402

DATASET = BASE_DIR / "ml" / "dataset.csv"
SORTIE = BASE_DIR / "ml" / "trustline_model.joblib"


def construire_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    preprocessor=normaliser_texte,  # accents/casse/espaces gérés
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=1,
                ),
            ),
            (
                "clf",
                LogisticRegression(max_iter=1000, class_weight="balanced"),
            ),
        ]
    )


def main():
    if not DATASET.exists():
        sys.exit(f"Dataset introuvable : {DATASET}")

    df = pd.read_csv(DATASET)
    df = df.dropna(subset=["texte", "label"])
    df["label"] = df["label"].astype(int)
    print(f"Dataset : {len(df)} exemples "
          f"({int(df.label.sum())} arnaques / {int((df.label == 0).sum())} légitimes)")

    # Petit dataset : on stratifie pour garder l'équilibre dans le test.
    X_train, X_test, y_train, y_test = train_test_split(
        df["texte"], df["label"],
        test_size=0.2, stratify=df["label"], random_state=42,
    )

    modele = construire_pipeline()
    modele.fit(X_train, y_train)

    print("\n=== Évaluation (jeu de test) ===")
    print(classification_report(y_test, modele.predict(X_test), zero_division=0))

    joblib.dump(modele, SORTIE)
    print(f"✅ Modèle enregistré : {SORTIE}")
    print("   Active-le avec  ML_MODEL_PATH=ml/trustline_model.joblib  dans .env")


if __name__ == "__main__":
    main()
