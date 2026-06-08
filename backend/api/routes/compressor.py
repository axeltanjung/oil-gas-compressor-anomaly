from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.services.inference import inference_service
from backend.services.health_index import compute_health_index

router = APIRouter(prefix="/compressor", tags=["compressor"])


@router.get("/{compressor_id}")
def get_compressor_detail(compressor_id: str, limit: int = 200) -> dict:
    df = inference_service.get_compressor_data(compressor_id, limit)
    if df is None:
        raise HTTPException(status_code=404, detail=f"Compressor {compressor_id} not found")

    latest = df.iloc[-1]
    health = compute_health_index(
        anomaly_score=0.2,
        reconstruction_error=0.1,
        vibration_x=float(latest["vibration_x"]),
        vibration_y=float(latest["vibration_y"]),
        bearing_temperature=float(latest["bearing_temperature"]),
        oil_temperature=float(latest["oil_temperature"]),
        efficiency=float(latest["efficiency_score"]),
    )

    sensor_history = df[["timestamp", "vibration_x", "vibration_y", "bearing_temperature",
                         "oil_temperature", "suction_pressure", "discharge_pressure",
                         "rpm", "flow_rate", "power_consumption", "efficiency_score"]].to_dict(orient="records")

    return {
        "compressor_id": compressor_id,
        "latest_health_score": health["health_score"],
        "health_category": health["category"],
        "total_records": len(df),
        "sensor_history": sensor_history[-limit:],
        "component_scores": health["component_scores"],
    }


@router.get("/{compressor_id}/health-history")
def get_health_history(compressor_id: str, window: int = 100) -> dict:
    df = inference_service.get_compressor_data(compressor_id, window)
    if df is None:
        raise HTTPException(status_code=404, detail=f"Compressor {compressor_id} not found")

    health_scores = []
    for _, row in df.iterrows():
        h = compute_health_index(
            anomaly_score=0.1,
            reconstruction_error=0.1,
            vibration_x=float(row["vibration_x"]),
            vibration_y=float(row["vibration_y"]),
            bearing_temperature=float(row["bearing_temperature"]),
            oil_temperature=float(row["oil_temperature"]),
            efficiency=float(row["efficiency_score"]),
        )
        health_scores.append({
            "timestamp": str(row["timestamp"]),
            "health_score": h["health_score"],
            "category": h["category"],
        })

    return {"compressor_id": compressor_id, "health_history": health_scores}
