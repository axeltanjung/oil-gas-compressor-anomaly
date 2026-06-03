"""
SHAP-based Explainability for Anomaly Detection

Provides:
- Feature contribution analysis for anomalies
- Top anomaly drivers identification
- Sensor contribution ranking
- Anomaly decomposition
"""
from __future__ import annotations

import numpy as np
import shap
from sklearn.ensemble import IsolationForest

from backend.training.preprocessing import ALL_FEATURES


class AnomalyExplainer:
    def __init__(self):
        self.explainer = None
        self.feature_names = ALL_FEATURES
        self.background_data: np.ndarray | None = None

    def fit(self, model: IsolationForest, background_data: np.ndarray):
        self.background_data = background_data[:500]
        self.explainer = shap.TreeExplainer(model)

    def explain(self, X: np.ndarray, top_k: int = 5) -> list[dict]:
        shap_values = self.explainer.shap_values(X)
        explanations = []

        for i in range(len(X)):
            feature_contributions = {}
            for j, fname in enumerate(self.feature_names):
                feature_contributions[fname] = float(shap_values[i, j])

            sorted_features = sorted(feature_contributions.items(), key=lambda x: abs(x[1]), reverse=True)
            top_drivers = sorted_features[:top_k]

            explanations.append({
                "top_drivers": [{"feature": f, "contribution": c} for f, c in top_drivers],
                "all_contributions": feature_contributions,
                "anomaly_severity": float(np.sum(np.abs(shap_values[i]))),
            })

        return explanations

    def global_importance(self, X: np.ndarray) -> dict[str, float]:
        shap_values = self.explainer.shap_values(X[:1000])
        mean_abs_shap = np.abs(shap_values).mean(axis=0)

        importance = {}
        for i, fname in enumerate(self.feature_names):
            importance[fname] = float(mean_abs_shap[i])

        return dict(sorted(importance.items(), key=lambda x: -x[1]))

    def anomaly_decomposition(self, X: np.ndarray, anomaly_indices: np.ndarray) -> dict:
        anomaly_data = X[anomaly_indices]
        if len(anomaly_data) == 0:
            return {"error": "No anomalies to explain"}

        shap_values = self.explainer.shap_values(anomaly_data[:100])
        mean_contributions = np.abs(shap_values).mean(axis=0)

        decomposition = {}
        for i, fname in enumerate(self.feature_names):
            decomposition[fname] = float(mean_contributions[i])

        total = sum(decomposition.values()) + 1e-10
        normalized = {k: v / total for k, v in decomposition.items()}

        return {
            "absolute_contributions": decomposition,
            "relative_contributions": normalized,
            "top_sensors": sorted(normalized.items(), key=lambda x: -x[1])[:5],
        }


def generate_maintenance_recommendations(explanation: dict, feature_values: dict) -> list[dict]:
    recommendations = []
    sensor_actions = {
        "vibration_x": {"action": "Inspect rotor balance and alignment", "component": "Rotating Assembly"},
        "vibration_y": {"action": "Check bearing condition and mounting", "component": "Bearings"},
        "bearing_temperature": {"action": "Inspect bearing lubrication and cooling", "component": "Bearing System"},
        "oil_temperature": {"action": "Check lubrication system and oil quality", "component": "Lubrication System"},
        "suction_pressure": {"action": "Inspect suction valves and inlet conditions", "component": "Suction System"},
        "discharge_pressure": {"action": "Check discharge valves and backpressure", "component": "Discharge System"},
        "rpm": {"action": "Inspect drive system and speed controller", "component": "Drive Train"},
        "flow_rate": {"action": "Check for blockages and valve positions", "component": "Flow Path"},
        "power_consumption": {"action": "Inspect electrical systems and load", "component": "Electrical System"},
        "efficiency_score": {"action": "Comprehensive performance assessment needed", "component": "Overall System"},
        "vibration_magnitude": {"action": "Full vibration analysis recommended", "component": "Rotating Equipment"},
        "pressure_ratio": {"action": "Check compression ratio and valve conditions", "component": "Compression System"},
        "temp_differential": {"action": "Inspect cooling system effectiveness", "component": "Thermal System"},
        "vibration_x_rolling_std": {"action": "Investigate vibration instability pattern", "component": "Dynamic Balance"},
        "vibration_y_rolling_std": {"action": "Investigate lateral vibration trend", "component": "Structural Integrity"},
        "bearing_temp_rolling_mean": {"action": "Monitor bearing temperature trend", "component": "Bearing Health"},
        "pressure_ratio_rolling_std": {"action": "Investigate pressure fluctuations", "component": "Process Stability"},
        "efficiency_rate_of_change": {"action": "Investigate degradation rate", "component": "Performance"},
        "vibration_asymmetry": {"action": "Check for misalignment or coupling issues", "component": "Alignment"},
        "power_efficiency_ratio": {"action": "Assess energy efficiency decline", "component": "Energy System"},
        "ambient_temperature": {"action": "Review environmental compensation", "component": "Environmental"},
    }

    for driver in explanation.get("top_drivers", [])[:5]:
        feature = driver["feature"]
        contribution = driver["contribution"]
        action_info = sensor_actions.get(feature, {"action": f"Investigate {feature}", "component": "Unknown"})

        severity = "HIGH" if abs(contribution) > 0.3 else "MEDIUM" if abs(contribution) > 0.1 else "LOW"

        recommendations.append({
            "feature": feature,
            "component": action_info["component"],
            "action": action_info["action"],
            "severity": severity,
            "contribution_score": abs(contribution),
        })

    return recommendations
