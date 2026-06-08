"""
Inference service for anomaly detection.
Loads trained models and provides prediction capabilities.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

from backend.utils.config import MODELS_DIR, DATA_DIR
from backend.training.preprocessing import engineer_features, load_scaler, transform_features
from backend.anomaly.isolation_forest import IsolationForestDetector
from backend.anomaly.autoencoder import AutoencoderDetector
from backend.anomaly.vae import VAEDetector
from backend.services.health_index import compute_health_index


class InferenceService:
    def __init__(self):
        self._if_model = None
        self._ae_model = None
        self._vae_model = None
        self._scaler = None
        self._loaded = False

    def load_models(self):
        if self._loaded:
            return

        scaler_path = MODELS_DIR / "scaler.joblib"
        if_path = MODELS_DIR / "isolation_forest.joblib"
        ae_path = MODELS_DIR / "autoencoder.pt"
        vae_path = MODELS_DIR / "vae.pt"

        if scaler_path.exists():
            self._scaler = load_scaler(scaler_path)
        if if_path.exists():
            self._if_model = IsolationForestDetector.load(if_path)
        if ae_path.exists():
            self._ae_model = AutoencoderDetector.load(ae_path)
        if vae_path.exists():
            self._vae_model = VAEDetector.load(vae_path)

        self._loaded = True

    def predict_single(self, reading: dict) -> dict:
        self.load_models()

        df = pd.DataFrame([reading])
        df_features = engineer_features(df)

        if self._scaler is None:
            return {"error": "Models not trained yet. Run training pipeline first."}

        X_scaled = transform_features(df_features, self._scaler)

        model_scores = {}
        if self._if_model:
            if_result = self._if_model.predict(X_scaled)
            model_scores["isolation_forest"] = float(if_result["anomaly_scores"][0])

        if self._ae_model:
            ae_result = self._ae_model.predict(X_scaled)
            model_scores["autoencoder"] = float(ae_result["anomaly_scores"][0])

        if self._vae_model:
            vae_result = self._vae_model.predict(X_scaled)
            model_scores["vae"] = float(vae_result["anomaly_probability"][0])

        ensemble_score = np.mean(list(model_scores.values())) if model_scores else 0.0
        is_anomaly = ensemble_score > 0.6

        health = compute_health_index(
            anomaly_score=ensemble_score,
            reconstruction_error=model_scores.get("autoencoder", 0.0),
            vibration_x=reading.get("vibration_x", 2.5),
            vibration_y=reading.get("vibration_y", 2.3),
            bearing_temperature=reading.get("bearing_temperature", 65.0),
            oil_temperature=reading.get("oil_temperature", 55.0),
            efficiency=reading.get("efficiency_score", 92.0),
        )

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(ensemble_score, 4),
            "health_score": health["health_score"],
            "health_category": health["category"],
            "model_scores": {k: round(v, 4) for k, v in model_scores.items()},
            "component_scores": health["component_scores"],
        }

    def predict_batch(self, readings: list[dict]) -> list[dict]:
        return [self.predict_single(r) for r in readings]

    def get_compressor_data(self, compressor_id: str, limit: int = 500) -> pd.DataFrame | None:
        csv_path = DATA_DIR / "compressor_telemetry.csv"
        if not csv_path.exists():
            return None
        df = pd.read_csv(csv_path, parse_dates=["timestamp"])
        comp_data = df[df["compressor_id"] == compressor_id].tail(limit)
        return comp_data if not comp_data.empty else None


inference_service = InferenceService()
