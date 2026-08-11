"""Entraînement du modèle de détection d'arnaques Trustline.

Usage :
    # 1. installer les deps ML (une seule fois)
    pip install -r requirements-ml.txt

    # 2. entraîner (depuis la racine du projet)
    python ml/train_model.py                          # utilise ml/dataset.csv
    python ml/train_model.py --dataset chemin/vers/mon_dataset.csv
    python ml/train_model.py --dataset mon.csv --out ml/trustline_model.joblib

Le CSV doit avoir 2 colonnes :  texte,label
    - texte : le message (français, éwé, mélange… peu importe)
    - label : 1 = arnaque, 0 = légitime
⚠️ Encode le fichier en UTF-8 (sinon les lettres éwé ɔ ɖ ƒ ŋ se cassent).

Produit un pipeline scikit-learn (avec predict_proba). Active-le ensuite via
ML_MODEL_PATH dans .env (voir apps/scoring/apps.py).

Choix techniques (défendables au jury)
--------------------------------------
* Même normalisation qu'en production (apps.core.utils.normaliser_texte).
* N-grammes de CARACTÈRES (char_wb 3-5) → robustes aux fautes, au sans-accent,
  et au MULTILINGUE (français + éwé) sans vocabulaire figé.
* LogisticRegression → léger, explicable, expose predict_proba.
"""
import argparse
import os
import sys
from pathlib import Path

# --- Bootstrap Django pour réutiliser normaliser_texte -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# La console Windows est en cp1252 : sans cela, les emoji des messages de fin
# font planter le script APRÈS l'écriture du modèle, ce qui laisse croire à un
# échec de l'entraînement.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

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


def charger_dataset(chemin: Path) -> pd.DataFrame:
    if not chemin.exists():
        sys.exit(f"❌ Dataset introuvable : {chemin}")
    # UTF-8 d'abord (pour l'éwé) ; repli latin-1 si le fichier vient d'Excel.
    try:
        df = pd.read_csv(chemin, encoding="utf-8")
    except UnicodeDecodeError:
        print("⚠️ Fichier non-UTF-8 → lecture en latin-1 (pense à ré-enregistrer en UTF-8).")
        df = pd.read_csv(chemin, encoding="latin-1")

    manquantes = {"texte", "label"} - set(df.columns)
    if manquantes:
        sys.exit(
            f"❌ Colonnes manquantes : {manquantes}. "
            f"Le CSV doit avoir l'entête exact : texte,label"
        )
    df = df.dropna(subset=["texte", "label"])
    df["texte"] = df["texte"].astype(str)
    df["label"] = df["label"].astype(int)
    return df


def main():
    parser = argparse.ArgumentParser(description="Entraîne le modèle Trustline.")
    parser.add_argument("--dataset", default=str(BASE_DIR / "ml" / "dataset.csv"))
    parser.add_argument("--out", default=str(BASE_DIR / "ml" / "trustline_model.joblib"))
    parser.add_argument("--test-size", type=float, default=0.2)
    args = parser.parse_args()

    df = charger_dataset(Path(args.dataset))
    n_arnaque = int(df.label.sum())
    n_legit = int((df.label == 0).sum())
    print(f"Dataset : {len(df)} exemples ({n_arnaque} arnaques / {n_legit} légitimes)")

    if n_arnaque < 5 or n_legit < 5:
        print("⚠️ Une classe a très peu d'exemples : résultats peu fiables.")

    # Stratifier pour garder l'équilibre ; repli si une classe est trop petite.
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            df["texte"], df["label"],
            test_size=args.test_size, stratify=df["label"], random_state=42,
        )
    except ValueError:
        print("⚠️ Stratification impossible (classe trop petite) → split simple.")
        X_train, X_test, y_train, y_test = train_test_split(
            df["texte"], df["label"], test_size=args.test_size, random_state=42,
        )

    modele = construire_pipeline()
    modele.fit(X_train, y_train)

    print("\n=== Évaluation (jeu de test) ===")
    print(classification_report(y_test, modele.predict(X_test), zero_division=0))

    joblib.dump(modele, args.out)
    print(f"✅ Modèle enregistré : {args.out}")
    print(f"   Active-le avec  ML_MODEL_PATH={args.out}  dans .env")


if __name__ == "__main__":
    main()
