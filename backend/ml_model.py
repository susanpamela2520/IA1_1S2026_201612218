"""
ml_model.py - Carga y uso del modelo de clasificación de señas
"""
import pickle
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

MODEL_PATH = Path("../models/model.pkl")
SCALER_PATH = Path("../models/scaler.pkl")
ENCODER_PATH = Path("../models/label_encoder.pkl")


class SignClassifier:
    """Wrapper del modelo de ML para clasificación de señas en tiempo real."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self._load()

    def _load(self) -> None:
        """Intenta cargar el modelo, scaler y encoder desde disco."""
        try:
            if MODEL_PATH.exists() and ENCODER_PATH.exists():
                with open(MODEL_PATH, "rb") as f:
                    self.model = pickle.load(f)
                with open(ENCODER_PATH, "rb") as f:
                    self.label_encoder = pickle.load(f)
                if SCALER_PATH.exists():
                    with open(SCALER_PATH, "rb") as f:
                        self.scaler = pickle.load(f)
                print(f"[ml_model] ✅ Modelo cargado: {MODEL_PATH}")
            else:
                print("[ml_model] ⚠️  Modelo no encontrado — entrena primero con scripts/train_model.py")
        except Exception as e:
            print(f"[ml_model] ❌ Error cargando modelo: {e}")

    def reload(self) -> None:
        """Recarga el modelo desde disco (útil tras reentrenamiento)."""
        self._load()

    def predict(
        self, features: np.ndarray, threshold: float = 0.70
    ) -> Tuple[Optional[str], float]:
        """
        Clasifica los landmarks extraídos de la mano.

        Parameters
        ----------
        features : ndarray (63,)
        threshold : umbral mínimo de confianza

        Returns
        -------
        (label, confidence)  —  label es None si confianza < threshold
        """
        if self.model is None:
            return None, 0.0

        X = features.reshape(1, -1)
        if self.scaler is not None:
            X = self.scaler.transform(X)

        try:
            proba = self.model.predict_proba(X)[0]
            confidence = float(np.max(proba))
            if confidence < threshold:
                return None, confidence
            idx = int(np.argmax(proba))
            label = self.label_encoder.inverse_transform([idx])[0]
            return label, confidence
        except Exception as e:
            print(f"[ml_model] Error en predicción: {e}")
            return None, 0.0

    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    @property
    def classes(self) -> list:
        if self.label_encoder is None:
            return []
        return self.label_encoder.classes_.tolist()


# Singleton global
classifier = SignClassifier()
