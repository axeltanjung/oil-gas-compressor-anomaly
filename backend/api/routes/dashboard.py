from __future__ import annotations

from fastapi import APIRouter
import pandas as pd
import numpy as np

from backend.services.health_index import compute_health_index
from backend.utils.config import DATA_DIR

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary() -> dict:
    csv_path = DATA_DIR / "compressor_telemetry.csv"
    if not csv_path.exists():
        return {"error": "No data available. Run training pipeline first."}

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    compressors = df["compressor_id"].unique().tolist()

    health_data = {"Healthy": 0, "Minor Degradation": 0, "Warning": 0, "Critical": 0}
    compressor_health = []

    for comp_id in compressors:
        comp_df = df[df["compressor_id"] == comp_id].tail(1).iloc[0]
        health = compute_health_index(
            anomaly_score=np.random.uniform(0, 0.4),
            reconstruction_error=np.random.uniform(0, 0.3),
            vibration_x=float(comp_df["vibration_x"]),
            vibration_y=float(comp_df["vibration_y"]),
            bearing_temperature=float(comp_df["bearing_temperature"]),
            oil_temperature=float(comp_df["oil_temperature"]),
            efficiency=float(comp_df["efficiency_score"]),
        )
        health_data[health["category"]] += 1
        compressor_health.append({
            "compressor_id": comp_id,
            "health_score": health["health_score"],
            "category": health["category"],
        })

    total_anomalies = health_data["Warning"] + health_data["Critical"]

    return {
        "total_compressors": len(compressors),
        "active_anomalies": total_anomalies,
        "critical_count": health_data["Critical"],
        "warning_count": health_data["Warning"],
        "healthy_count": health_data["Healthy"],
        "minor_degradation_count": health_data["Minor Degradation"],
        "average_health_score": round(np.mean([c["health_score"] for c in compressor_health]), 1),
        "health_distribution": health_data,
        "compressor_health": compressor_health,
    }


@router.get("/anomaly-trend")
def anomaly_trend() -> dict:
    csv_path = DATA_DIR / "compressor_telemetry.csv"
    if not csv_path.exists():
        return {"error": "No data available."}

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    df["date"] = df["timestamp"].dt.date.astype(str)

    daily = df.groupby("date").agg(
        avg_vibration=("vibration_x", "mean"),
        avg_bearing_temp=("bearing_temperature", "mean"),
        avg_efficiency=("efficiency_score", "mean"),
    ).reset_index()

    return {"trend": daily.tail(30).to_dict(orient="records")}
