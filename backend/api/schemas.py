"""
Pydantic schemas for API request/response validation.
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class SensorReading(BaseModel):
    compressor_id: str = Field(..., example="COMP-001")
    suction_pressure: float = Field(..., ge=0, le=100)
    discharge_pressure: float = Field(..., ge=50, le=400)
    vibration_x: float = Field(..., ge=0, le=30)
    vibration_y: float = Field(..., ge=0, le=30)
    bearing_temperature: float = Field(..., ge=20, le=200)
    oil_temperature: float = Field(..., ge=15, le=150)
    rpm: float = Field(..., ge=1000, le=6000)
    flow_rate: float = Field(..., ge=100, le=1500)
    power_consumption: float = Field(..., ge=100, le=1000)
    ambient_temperature: float = Field(..., ge=-20, le=60)
    efficiency_score: float = Field(..., ge=40, le=100)


class AnomalyPredictionResponse(BaseModel):
    compressor_id: str
    is_anomaly: bool
    anomaly_score: float
    health_score: float
    health_category: str
    model_scores: dict[str, float]
    top_drivers: list[dict]
    recommendations: list[dict]


class BatchPredictionRequest(BaseModel):
    readings: list[SensorReading]


class BatchPredictionResponse(BaseModel):
    total: int
    anomalies_detected: int
    anomaly_rate: float
    results: list[AnomalyPredictionResponse]


class DashboardSummary(BaseModel):
    total_compressors: int
    active_anomalies: int
    critical_count: int
    warning_count: int
    healthy_count: int
    minor_degradation_count: int
    average_health_score: float
    anomaly_trend: list[dict]
    health_distribution: dict[str, int]


class CompressorDetail(BaseModel):
    compressor_id: str
    latest_health_score: float
    health_category: str
    sensor_history: list[dict]
    anomaly_timeline: list[dict]
    health_evolution: list[dict]


class ExplainResponse(BaseModel):
    compressor_id: str
    anomaly_score: float
    top_drivers: list[dict]
    severity: str
    recommendations: list[dict]
    component_contributions: dict[str, float]


class HealthScoreResponse(BaseModel):
    compressor_id: str
    health_score: float
    category: str
    component_scores: dict[str, float]
    trend: str
