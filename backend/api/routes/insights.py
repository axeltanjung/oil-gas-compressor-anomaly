from __future__ import annotations

from fastapi import APIRouter, HTTPException
from backend.services.inference import inference_service
from backend.services.health_index import compute_health_index
from backend.explainability.shap_explainer import generate_maintenance_recommendations
from backend.utils.config import DATA_DIR

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/explain/{compressor_id}")
def explain_anomaly(compressor_id: str) -> dict:
    df = inference_service.get_compressor_data(compressor_id, 1)
    if df is None:
        raise HTTPException(status_code=404, detail=f"Compressor {compressor_id} not found")

    latest = df.iloc[-1]
    health = compute_health_index(
        anomaly_score=0.3,
        reconstruction_error=0.2,
        vibration_x=float(latest["vibration_x"]),
        vibration_y=float(latest["vibration_y"]),
        bearing_temperature=float(latest["bearing_temperature"]),
        oil_temperature=float(latest["oil_temperature"]),
        efficiency=float(latest["efficiency_score"]),
    )

    explanation = {
        "top_drivers": [
            {"feature": k, "contribution": v}
            for k, v in sorted(health["component_scores"].items(), key=lambda x: -x[1])[:5]
        ]
    }

    recommendations = generate_maintenance_recommendations(explanation, latest.to_dict())

    severity = "HIGH" if health["health_score"] < 30 else "MEDIUM" if health["health_score"] < 60 else "LOW"

    return {
        "compressor_id": compressor_id,
        "anomaly_score": health["weighted_degradation"],
        "health_score": health["health_score"],
        "severity": severity,
        "top_drivers": explanation["top_drivers"],
        "recommendations": recommendations,
        "component_contributions": health["component_scores"],
    }


@router.get("/health-score/{compressor_id}")
def get_health_score(compressor_id: str) -> dict:
    df = inference_service.get_compressor_data(compressor_id, 10)
    if df is None:
        raise HTTPException(status_code=404, detail=f"Compressor {compressor_id} not found")

    latest = df.iloc[-1]
    health = compute_health_index(
        anomaly_score=0.15,
        reconstruction_error=0.1,
        vibration_x=float(latest["vibration_x"]),
        vibration_y=float(latest["vibration_y"]),
        bearing_temperature=float(latest["bearing_temperature"]),
        oil_temperature=float(latest["oil_temperature"]),
        efficiency=float(latest["efficiency_score"]),
    )

    if len(df) > 1:
        prev = df.iloc[-2]
        prev_health = compute_health_index(
            anomaly_score=0.15,
            reconstruction_error=0.1,
            vibration_x=float(prev["vibration_x"]),
            vibration_y=float(prev["vibration_y"]),
            bearing_temperature=float(prev["bearing_temperature"]),
            oil_temperature=float(prev["oil_temperature"]),
            efficiency=float(prev["efficiency_score"]),
        )
        trend = "improving" if health["health_score"] > prev_health["health_score"] else "declining"
    else:
        trend = "stable"

    return {
        "compressor_id": compressor_id,
        "health_score": health["health_score"],
        "category": health["category"],
        "component_scores": health["component_scores"],
        "trend": trend,
    }


@router.get("/maintenance-recommendations")
def maintenance_recommendations() -> dict:
    import pandas as pd
    csv_path = DATA_DIR / "compressor_telemetry.csv"
    if not csv_path.exists():
        return {"error": "No data available."}

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    compressors = df["compressor_id"].unique()

    all_recommendations = []
    for comp_id in compressors:
        comp_df = df[df["compressor_id"] == comp_id].tail(1).iloc[0]
        health = compute_health_index(
            anomaly_score=0.2,
            reconstruction_error=0.15,
            vibration_x=float(comp_df["vibration_x"]),
            vibration_y=float(comp_df["vibration_y"]),
            bearing_temperature=float(comp_df["bearing_temperature"]),
            oil_temperature=float(comp_df["oil_temperature"]),
            efficiency=float(comp_df["efficiency_score"]),
        )

        if health["health_score"] < 75:
            explanation = {
                "top_drivers": [
                    {"feature": k, "contribution": v}
                    for k, v in sorted(health["component_scores"].items(), key=lambda x: -x[1])[:3]
                ]
            }
            recs = generate_maintenance_recommendations(explanation, comp_df.to_dict())
            all_recommendations.append({
                "compressor_id": comp_id,
                "health_score": health["health_score"],
                "priority": "HIGH" if health["health_score"] < 30 else "MEDIUM",
                "recommendations": recs,
            })

    all_recommendations.sort(key=lambda x: x["health_score"])
    return {"recommendations": all_recommendations}
