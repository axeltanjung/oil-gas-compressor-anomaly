"""
Feature engineering and preprocessing for compressor anomaly detection.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import joblib

SENSOR_FEATURES = [
    "suction_pressure",
    "discharge_pressure",
    "vibration_x",
    "vibration_y",
    "bearing_temperature",
    "oil_temperature",
    "rpm",
    "flow_rate",
    "power_consumption",
    "ambient_temperature",
    "efficiency_score",
]

ENGINEERED_FEATURES = [
    "pressure_ratio",
    "vibration_magnitude",
    "temp_differential",
    "power_efficiency_ratio",
    "vibration_x_rolling_std",
    "vibration_y_rolling_std",
    "bearing_temp_rolling_mean",
    "pressure_ratio_rolling_std",
    "efficiency_rate_of_change",
    "vibration_asymmetry",
]

ALL_FEATURES = SENSOR_FEATURES + ENGINEERED_FEATURES


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["pressure_ratio"] = out["discharge_pressure"] / out["suction_pressure"].clip(lower=1)
    out["vibration_magnitude"] = np.sqrt(out["vibration_x"] ** 2 + out["vibration_y"] ** 2)
    out["temp_differential"] = out["bearing_temperature"] - out["oil_temperature"]
    out["power_efficiency_ratio"] = out["power_consumption"] / out["efficiency_score"].clip(lower=1)

    for comp_id in out["compressor_id"].unique():
        mask = out["compressor_id"] == comp_id
        out.loc[mask, "vibration_x_rolling_std"] = out.loc[mask, "vibration_x"].rolling(24, min_periods=1).std()
        out.loc[mask, "vibration_y_rolling_std"] = out.loc[mask, "vibration_y"].rolling(24, min_periods=1).std()
        out.loc[mask, "bearing_temp_rolling_mean"] = out.loc[mask, "bearing_temperature"].rolling(24, min_periods=1).mean()
        out.loc[mask, "pressure_ratio_rolling_std"] = out.loc[mask, "pressure_ratio"].rolling(24, min_periods=1).std()
        out.loc[mask, "efficiency_rate_of_change"] = out.loc[mask, "efficiency_score"].diff().fillna(0)

    out["vibration_asymmetry"] = (out["vibration_x"] - out["vibration_y"]).abs()
    out = out.fillna(0)
    return out


def fit_scaler(df: pd.DataFrame, scaler_path: Path) -> StandardScaler:
    scaler = StandardScaler()
    scaler.fit(df[ALL_FEATURES])
    joblib.dump(scaler, scaler_path)
    return scaler


def transform_features(df: pd.DataFrame, scaler: StandardScaler) -> np.ndarray:
    return scaler.transform(df[ALL_FEATURES])


def load_scaler(scaler_path: Path) -> StandardScaler:
    return joblib.load(scaler_path)
