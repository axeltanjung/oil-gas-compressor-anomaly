"""
Compressor Health Index Scoring System

Composite 0-100 health score combining:
- Anomaly score from multiple models
- Reconstruction error
- Vibration severity
- Temperature abnormality
- Operational instability

Categories:
- 76-100: Healthy
- 51-75: Minor Degradation
- 26-50: Warning
- 0-25: Critical
"""
from __future__ import annotations

import numpy as np


HEALTH_WEIGHTS = {
    "anomaly_score": 0.25,
    "reconstruction_error": 0.20,
    "vibration_severity": 0.20,
    "temperature_abnormality": 0.15,
    "operational_instability": 0.10,
    "efficiency_degradation": 0.10,
}

NORMAL_RANGES = {
    "vibration_x": (0.5, 5.0),
    "vibration_y": (0.5, 5.0),
    "bearing_temperature": (45.0, 85.0),
    "oil_temperature": (40.0, 75.0),
    "efficiency_score": (85.0, 100.0),
    "pressure_ratio": (3.0, 5.5),
    "rpm": (3400, 3800),
}


def compute_vibration_severity(vibration_x: float, vibration_y: float) -> float:
    magnitude = np.sqrt(vibration_x**2 + vibration_y**2)
    if magnitude < 3.5:
        return 0.0
    elif magnitude < 5.0:
        return (magnitude - 3.5) / 1.5 * 0.3
    elif magnitude < 8.0:
        return 0.3 + (magnitude - 5.0) / 3.0 * 0.4
    else:
        return min(1.0, 0.7 + (magnitude - 8.0) / 5.0 * 0.3)


def compute_temperature_abnormality(bearing_temp: float, oil_temp: float) -> float:
    bearing_score = 0.0
    if bearing_temp > 85:
        bearing_score = min(1.0, (bearing_temp - 85) / 40)
    elif bearing_temp < 45:
        bearing_score = min(1.0, (45 - bearing_temp) / 20)

    oil_score = 0.0
    if oil_temp > 75:
        oil_score = min(1.0, (oil_temp - 75) / 30)

    return max(bearing_score, oil_score) * 0.7 + min(bearing_score, oil_score) * 0.3


def compute_operational_instability(pressure_ratio_std: float, rpm_std: float) -> float:
    pressure_score = min(1.0, pressure_ratio_std / 1.0)
    rpm_score = min(1.0, rpm_std / 100.0)
    return pressure_score * 0.6 + rpm_score * 0.4


def compute_efficiency_degradation(efficiency: float) -> float:
    if efficiency >= 90:
        return 0.0
    elif efficiency >= 80:
        return (90 - efficiency) / 10 * 0.4
    elif efficiency >= 70:
        return 0.4 + (80 - efficiency) / 10 * 0.3
    else:
        return min(1.0, 0.7 + (70 - efficiency) / 20 * 0.3)


def compute_health_index(
    anomaly_score: float,
    reconstruction_error: float,
    vibration_x: float,
    vibration_y: float,
    bearing_temperature: float,
    oil_temperature: float,
    pressure_ratio_std: float = 0.0,
    rpm_std: float = 0.0,
    efficiency: float = 92.0,
) -> dict:
    vib_severity = compute_vibration_severity(vibration_x, vibration_y)
    temp_abnormality = compute_temperature_abnormality(bearing_temperature, oil_temperature)
    op_instability = compute_operational_instability(pressure_ratio_std, rpm_std)
    eff_degradation = compute_efficiency_degradation(efficiency)

    norm_anomaly = min(1.0, anomaly_score)
    norm_recon = min(1.0, reconstruction_error)

    component_scores = {
        "anomaly_score": norm_anomaly,
        "reconstruction_error": norm_recon,
        "vibration_severity": vib_severity,
        "temperature_abnormality": temp_abnormality,
        "operational_instability": op_instability,
        "efficiency_degradation": eff_degradation,
    }

    weighted_degradation = sum(
        component_scores[k] * HEALTH_WEIGHTS[k] for k in HEALTH_WEIGHTS
    )

    health_score = max(0, min(100, 100 * (1 - weighted_degradation)))

    if health_score >= 76:
        category = "Healthy"
    elif health_score >= 51:
        category = "Minor Degradation"
    elif health_score >= 26:
        category = "Warning"
    else:
        category = "Critical"

    return {
        "health_score": round(health_score, 1),
        "category": category,
        "component_scores": {k: round(v, 4) for k, v in component_scores.items()},
        "weighted_degradation": round(weighted_degradation, 4),
    }


def batch_health_index(
    anomaly_scores: np.ndarray,
    reconstruction_errors: np.ndarray,
    vibration_x: np.ndarray,
    vibration_y: np.ndarray,
    bearing_temps: np.ndarray,
    oil_temps: np.ndarray,
    efficiency_scores: np.ndarray,
) -> list[dict]:
    results = []
    for i in range(len(anomaly_scores)):
        result = compute_health_index(
            anomaly_score=float(anomaly_scores[i]),
            reconstruction_error=float(reconstruction_errors[i]),
            vibration_x=float(vibration_x[i]),
            vibration_y=float(vibration_y[i]),
            bearing_temperature=float(bearing_temps[i]),
            oil_temperature=float(oil_temps[i]),
            efficiency=float(efficiency_scores[i]),
        )
        results.append(result)
    return results
