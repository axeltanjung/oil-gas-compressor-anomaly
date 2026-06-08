"""
MLflow integration for experiment tracking and model registry.
"""
from __future__ import annotations

import mlflow
from pathlib import Path

from backend.utils.config import MLFLOW_DIR


def init_mlflow():
    MLFLOW_DIR.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(f"file://{MLFLOW_DIR / 'mlruns'}")
    mlflow.set_experiment("compressor-anomaly-detection")


def log_model_training(model_name: str, params: dict, metrics: dict, artifacts: dict | None = None):
    with mlflow.start_run(run_name=f"train_{model_name}"):
        mlflow.set_tag("model_type", model_name)
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)

        if artifacts:
            for name, path in artifacts.items():
                if Path(path).exists():
                    mlflow.log_artifact(path, artifact_path=name)


def log_batch_inference(model_name: str, n_samples: int, n_anomalies: int, metrics: dict):
    with mlflow.start_run(run_name=f"inference_{model_name}"):
        mlflow.set_tag("run_type", "inference")
        mlflow.set_tag("model_type", model_name)
        mlflow.log_param("n_samples", n_samples)
        mlflow.log_metric("n_anomalies", n_anomalies)
        mlflow.log_metric("anomaly_rate", n_anomalies / max(n_samples, 1))
        mlflow.log_metrics(metrics)
