"""
Model 1: Isolation Forest Anomaly Detection

Classical unsupervised anomaly detection baseline.
Provides anomaly scores and feature importance approximation.
"""
from __future__ import annotations

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from pathlib import Path

from backend.utils.config import MODELS_DIR


class IsolationForestDetector:
    def __init__(self, contamination: float = 0.05, n_estimators: int = 200, random_state: int = 42):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            max_samples="auto",
            random_state=random_state,
            n_jobs=-1,
        )
        self.feature_names: list[str] = []

    def fit(self, X: np.ndarray, feature_names: list[str] | None = None) -> dict:
        self.feature_names = feature_names or [f"f{i}" for i in range(X.shape[1])]
        self.model.fit(X)

        scores = self.model.decision_function(X)
        predictions = self.model.predict(X)
        n_anomalies = (predictions == -1).sum()

        return {
            "n_samples": len(X),
            "n_anomalies": int(n_anomalies),
            "contamination": self.contamination,
            "mean_score": float(scores.mean()),
            "std_score": float(scores.std()),
        }

    def predict(self, X: np.ndarray) -> dict:
        scores = self.model.decision_function(X)
        predictions = self.model.predict(X)
        anomaly_scores = -scores
        normalized_scores = (anomaly_scores - anomaly_scores.min()) / (anomaly_scores.max() - anomaly_scores.min() + 1e-10)

        return {
            "anomaly_labels": predictions,
            "anomaly_scores": normalized_scores,
            "raw_scores": scores,
        }

    def feature_importance(self, X: np.ndarray) -> dict[str, float]:
        importances = {}
        base_scores = self.model.decision_function(X)

        for i, fname in enumerate(self.feature_names):
            X_permuted = X.copy()
            np.random.shuffle(X_permuted[:, i])
            permuted_scores = self.model.decision_function(X_permuted)
            importances[fname] = float(np.abs(base_scores - permuted_scores).mean())

        total = sum(importances.values()) + 1e-10
        return {k: v / total for k, v in sorted(importances.items(), key=lambda x: -x[1])}

    def save(self, path: Path | None = None):
        path = path or MODELS_DIR / "isolation_forest.joblib"
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: Path | None = None) -> "IsolationForestDetector":
        path = path or MODELS_DIR / "isolation_forest.joblib"
        return joblib.load(path)
