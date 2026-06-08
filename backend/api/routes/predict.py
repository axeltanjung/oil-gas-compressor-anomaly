from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.services.inference import inference_service
from backend.explainability.shap_explainer import generate_maintenance_recommendations

router = APIRouter(prefix="/anomaly", tags=["anomaly"])


@router.post("/predict")
def predict_anomaly(reading: dict) -> dict:
    try:
        result = inference_service.predict_single(reading)
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])

        recommendations = generate_maintenance_recommendations(
            {"top_drivers": [
                {"feature": k, "contribution": v}
                for k, v in sorted(result.get("component_scores", {}).items(), key=lambda x: -x[1])[:5]
            ]},
            reading,
        )
        result["recommendations"] = recommendations
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
def batch_predict(payload: dict) -> dict:
    readings = payload.get("readings", [])
    if not readings:
        raise HTTPException(status_code=400, detail="No readings provided")

    results = inference_service.predict_batch(readings)
    anomalies = [r for r in results if r.get("is_anomaly")]

    return {
        "total": len(results),
        "anomalies_detected": len(anomalies),
        "anomaly_rate": len(anomalies) / max(len(results), 1),
        "results": results,
    }
