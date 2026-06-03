"""
Complete ML Training Pipeline

Orchestrates:
1. Data generation/loading
2. Feature engineering
3. Model training (all 4 models)
4. MLflow logging
5. Model saving
"""
from __future__ import annotations

import json
import numpy as np
import pandas as pd
from pathlib import Path

from backend.utils.config import DATA_DIR, MODELS_DIR, ensure_dirs
from backend.training.synthetic_data_generator import generate_dataset
from backend.training.preprocessing import engineer_features, fit_scaler, transform_features, ALL_FEATURES
from backend.training.mlflow_utils import init_mlflow, log_model_training
from backend.anomaly.isolation_forest import IsolationForestDetector
from backend.anomaly.autoencoder import AutoencoderDetector
from backend.anomaly.vae import VAEDetector
from backend.anomaly.lstm_forecaster import LSTMResidualDetector


def load_or_generate_data() -> pd.DataFrame:
    csv_path = DATA_DIR / "compressor_telemetry.csv"
    if csv_path.exists():
        print(f"Loading existing dataset from {csv_path}")
        return pd.read_csv(csv_path, parse_dates=["timestamp"])
    else:
        print("Generating synthetic dataset...")
        return generate_dataset(csv_path)


def train_isolation_forest(X_scaled: np.ndarray) -> dict:
    print("\n[1/4] Training Isolation Forest...")
    detector = IsolationForestDetector(contamination=0.05)
    metrics = detector.fit(X_scaled, feature_names=ALL_FEATURES)
    detector.save()

    log_model_training(
        "isolation_forest",
        params={"contamination": 0.05, "n_estimators": 200},
        metrics=metrics,
    )
    print(f"  Anomalies detected: {metrics['n_anomalies']}/{metrics['n_samples']}")
    return metrics


def train_autoencoder(X_scaled: np.ndarray) -> dict:
    print("\n[2/4] Training Autoencoder...")
    detector = AutoencoderDetector(input_dim=X_scaled.shape[1], latent_dim=8)
    metrics = detector.fit(X_scaled, epochs=50, batch_size=512)
    detector.save()

    log_model_training(
        "autoencoder",
        params={"input_dim": X_scaled.shape[1], "latent_dim": 8, "epochs": 50},
        metrics=metrics,
    )
    return metrics


def train_vae(X_scaled: np.ndarray) -> dict:
    print("\n[3/4] Training VAE...")
    detector = VAEDetector(input_dim=X_scaled.shape[1], latent_dim=6)
    metrics = detector.fit(X_scaled, epochs=60, batch_size=512)
    detector.save()

    log_model_training(
        "vae",
        params={"input_dim": X_scaled.shape[1], "latent_dim": 6, "epochs": 60, "beta": 1.0},
        metrics=metrics,
    )
    return metrics


def train_lstm(X_scaled: np.ndarray, df: pd.DataFrame) -> dict:
    print("\n[4/4] Training LSTM Forecaster...")
    first_compressor = df[df["compressor_id"] == df["compressor_id"].unique()[0]]
    comp_indices = first_compressor.index[:10000]
    X_comp = X_scaled[comp_indices]

    detector = LSTMResidualDetector(input_dim=X_scaled.shape[1])
    metrics = detector.fit(X_comp, epochs=30, batch_size=256)
    detector.save()

    log_model_training(
        "lstm_forecaster",
        params={"input_dim": X_scaled.shape[1], "hidden_dim": 64, "epochs": 30},
        metrics=metrics,
    )
    return metrics


def run_full_pipeline() -> dict:
    ensure_dirs()
    init_mlflow()

    print("=" * 70)
    print("  COMPRESSOR ANOMALY DETECTION - FULL TRAINING PIPELINE")
    print("=" * 70)

    df = load_or_generate_data()
    print(f"\nDataset: {len(df)} rows, {df['compressor_id'].nunique()} compressors")

    print("\nEngineering features...")
    df_features = engineer_features(df)

    print("Fitting scaler...")
    scaler = fit_scaler(df_features, MODELS_DIR / "scaler.joblib")
    X_scaled = transform_features(df_features, scaler)
    print(f"Feature matrix: {X_scaled.shape}")

    results = {}
    results["isolation_forest"] = train_isolation_forest(X_scaled)
    results["autoencoder"] = train_autoencoder(X_scaled)
    results["vae"] = train_vae(X_scaled)
    results["lstm"] = train_lstm(X_scaled, df)

    summary_path = MODELS_DIR / "training_summary.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2, default=float)

    print("\n" + "=" * 70)
    print("  TRAINING COMPLETE")
    print("=" * 70)
    print(f"\nModels saved to: {MODELS_DIR}")
    print(f"Summary: {summary_path}")
    return results


if __name__ == "__main__":
    run_full_pipeline()
