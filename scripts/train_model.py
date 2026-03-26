"""
train_model.py — Entrenamiento y evaluación del modelo de clasificación de señas
=================================================================================
Ejecutar después de collect_data.py.

Uso:
    python train_model.py

Salida:
    models/model.pkl          → mejor modelo entrenado
    models/scaler.pkl         → StandardScaler ajustado
    models/label_encoder.pkl  → LabelEncoder
    models/training_results.json → métricas de todos los algoritmos
"""
import csv
import json
import pickle
import warnings
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC

warnings.filterwarnings("ignore")

DATASET_PATH = Path(__file__).parent.parent / "dataset" / "landmarks.csv"
MODELS_DIR = Path(__file__).parent.parent / "models"

# ─── Cargar dataset ───────────────────────────────────────────────────────────

def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset no encontrado en {DATASET_PATH}.\n"
            "Ejecuta primero: python scripts/collect_data.py"
        )

    X, y = [], []
    with open(DATASET_PATH, newline="") as f:
        reader = csv.reader(f)
        next(reader)        # saltar header
        for row in reader:
            if row:
                X.append([float(v) for v in row[:-1]])
                y.append(row[-1])

    if len(X) == 0:
        raise ValueError("El dataset está vacío.")

    return np.array(X, dtype=np.float32), np.array(y)


# ─── Entrenamiento ────────────────────────────────────────────────────────────

def train():
    print("=" * 60)
    print("  HandTalk AI — Entrenamiento del Modelo")
    print("=" * 60)

    print("\n🔄 Cargando dataset...")
    X, y = load_dataset()

    classes, counts = np.unique(y, return_counts=True)
    print(f"   Muestras totales : {len(X)}")
    print(f"   Número de clases : {len(classes)}")
    for c, n in zip(classes, counts):
        print(f"     {c:<20} {n} muestras")

    # Encoding y escalado
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_enc, test_size=0.20, random_state=42, stratify=y_enc
    )

    # ─── Modelos candidatos ───────────────────────────────────────────────────
    candidates = {
        "Random Forest":      RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
        "SVM (RBF)":          SVC(kernel="rbf", C=10, gamma="scale", probability=True, random_state=42),
        "KNN (k=7)":          KNeighborsClassifier(n_neighbors=7, weights="distance"),
        "Logistic Regression": LogisticRegression(C=1.0, max_iter=1000, random_state=42),
    }

    print("\n📊 Evaluando algoritmos (cross-validation 5-fold)...\n")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    results = {}
    best_name, best_model, best_score = "", None, 0.0

    for name, clf in candidates.items():
        cv_scores = cross_val_score(clf, X_scaled, y_enc, cv=cv, scoring="accuracy", n_jobs=-1)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

        acc   = accuracy_score(y_test, y_pred)
        prec  = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec   = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1    = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        cv_m  = float(cv_scores.mean())
        cv_s  = float(cv_scores.std())

        results[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "cv_mean": round(cv_m, 4),
            "cv_std": round(cv_s, 4),
        }

        marker = ""
        if acc > best_score:
            best_score, best_name, best_model = acc, name, clf
            marker = "  ← MEJOR"

        print(f"  {name}:{marker}")
        print(f"    Test Accuracy : {acc:.4f}   CV: {cv_m:.4f} ± {cv_s:.4f}")
        print(f"    Precision     : {prec:.4f}   Recall: {rec:.4f}   F1: {f1:.4f}\n")

    # ─── Reporte detallado del mejor ──────────────────────────────────────────
    print(f"🏆 Mejor modelo: {best_name}  (accuracy test: {best_score:.4f})")
    y_pred_best = best_model.predict(X_test)
    print("\n📋 Classification Report:\n")
    print(classification_report(y_test, y_pred_best, target_names=le.classes_))

    cm = confusion_matrix(y_test, y_pred_best)
    print("📐 Matriz de Confusión:")
    print(cm)

    # ─── Reentrenar el mejor en TODO el dataset ───────────────────────────────
    print("\n🔁 Reentrenando mejor modelo en dataset completo...")
    best_model.fit(X_scaled, y_enc)

    # ─── Guardar artefactos ───────────────────────────────────────────────────
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    with open(MODELS_DIR / "model.pkl", "wb") as f:
        pickle.dump(best_model, f)
    with open(MODELS_DIR / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open(MODELS_DIR / "label_encoder.pkl", "wb") as f:
        pickle.dump(le, f)

    training_meta = {
        "best_model": best_name,
        "best_accuracy_test": best_score,
        "classes": le.classes_.tolist(),
        "n_samples": len(X),
        "n_features": X.shape[1],
        "all_results": results,
    }
    with open(MODELS_DIR / "training_results.json", "w") as f:
        json.dump(training_meta, f, indent=2, ensure_ascii=False)

    print("\n✅ Artefactos guardados:")
    print(f"   {MODELS_DIR}/model.pkl")
    print(f"   {MODELS_DIR}/scaler.pkl")
    print(f"   {MODELS_DIR}/label_encoder.pkl")
    print(f"   {MODELS_DIR}/training_results.json")
    print("\n🚀 Puedes iniciar el backend: cd backend && uvicorn main:app --reload")


if __name__ == "__main__":
    train()
