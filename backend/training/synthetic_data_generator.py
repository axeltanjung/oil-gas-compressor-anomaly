"""
Synthetic Compressor Telemetry Data Generator

Generates realistic industrial compressor sensor data with injected anomalies:
- Normal operations with natural variance
- Gradual degradation patterns
- Cavitation events
- Overheating scenarios
- Imbalance / misalignment
- Lubrication degradation
- Pressure instability
- Sensor noise and drift
- Sudden anomaly spikes
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
NUM_COMPRESSORS = 8
HOURS_PER_COMPRESSOR = 18750
TOTAL_ROWS = NUM_COMPRESSORS * HOURS_PER_COMPRESSOR

COMPRESSOR_IDS = [f"COMP-{str(i).zfill(3)}" for i in range(1, NUM_COMPRESSORS + 1)]

NORMAL_PARAMS = {
    "suction_pressure": (45.0, 2.0),
    "discharge_pressure": (180.0, 5.0),
    "vibration_x": (2.5, 0.4),
    "vibration_y": (2.3, 0.4),
    "bearing_temperature": (65.0, 3.0),
    "oil_temperature": (55.0, 2.5),
    "rpm": (3600.0, 50.0),
    "flow_rate": (850.0, 30.0),
    "power_consumption": (450.0, 20.0),
    "ambient_temperature": (35.0, 5.0),
    "efficiency_score": (92.0, 2.0),
}


def generate_base_data(rng: np.random.Generator, n_hours: int, compressor_id: str) -> pd.DataFrame:
    start = pd.Timestamp("2022-01-01")
    timestamps = pd.date_range(start, periods=n_hours, freq="h")

    data = {"timestamp": timestamps, "compressor_id": compressor_id}

    for feature, (mean, std) in NORMAL_PARAMS.items():
        base = rng.normal(mean, std, n_hours)
        seasonal = np.sin(np.linspace(0, 8 * np.pi, n_hours)) * std * 0.3
        daily_cycle = np.sin(np.linspace(0, n_hours / 24 * 2 * np.pi, n_hours)) * std * 0.2
        data[feature] = base + seasonal + daily_cycle

    data["operating_hours"] = np.arange(n_hours).astype(float)
    data["maintenance_cycles"] = np.floor(np.arange(n_hours) / 2000).astype(int)

    return pd.DataFrame(data)


def inject_gradual_degradation(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(df)
    n_events = rng.integers(2, 5)

    for _ in range(n_events):
        start_idx = rng.integers(0, int(n * 0.7))
        duration = rng.integers(500, 2000)
        end_idx = min(start_idx + duration, n)
        ramp = np.linspace(0, 1, end_idx - start_idx)

        df.loc[start_idx:end_idx - 1, "vibration_x"] += ramp * rng.uniform(1.5, 4.0)
        df.loc[start_idx:end_idx - 1, "vibration_y"] += ramp * rng.uniform(1.0, 3.5)
        df.loc[start_idx:end_idx - 1, "bearing_temperature"] += ramp * rng.uniform(5, 20)
        df.loc[start_idx:end_idx - 1, "efficiency_score"] -= ramp * rng.uniform(3, 10)
        df.loc[start_idx:end_idx - 1, "power_consumption"] += ramp * rng.uniform(20, 60)

    return df


def inject_cavitation(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(df)
    n_events = rng.integers(1, 4)

    for _ in range(n_events):
        start_idx = rng.integers(0, n - 200)
        duration = rng.integers(50, 200)
        end_idx = min(start_idx + duration, n)

        df.loc[start_idx:end_idx - 1, "suction_pressure"] -= rng.uniform(10, 25)
        df.loc[start_idx:end_idx - 1, "vibration_x"] += rng.uniform(3, 8) + rng.normal(0, 1, end_idx - start_idx)
        df.loc[start_idx:end_idx - 1, "vibration_y"] += rng.uniform(2, 6) + rng.normal(0, 0.8, end_idx - start_idx)
        df.loc[start_idx:end_idx - 1, "flow_rate"] -= rng.uniform(50, 150)
        df.loc[start_idx:end_idx - 1, "efficiency_score"] -= rng.uniform(8, 15)

    return df


def inject_overheating(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(df)
    n_events = rng.integers(1, 3)

    for _ in range(n_events):
        start_idx = rng.integers(0, n - 300)
        duration = rng.integers(100, 300)
        end_idx = min(start_idx + duration, n)
        ramp = np.linspace(0, 1, end_idx - start_idx)

        df.loc[start_idx:end_idx - 1, "bearing_temperature"] += ramp * rng.uniform(25, 50)
        df.loc[start_idx:end_idx - 1, "oil_temperature"] += ramp * rng.uniform(15, 35)
        df.loc[start_idx:end_idx - 1, "power_consumption"] += ramp * rng.uniform(30, 80)
        df.loc[start_idx:end_idx - 1, "efficiency_score"] -= ramp * rng.uniform(5, 15)

    return df


def inject_imbalance(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(df)
    n_events = rng.integers(1, 3)

    for _ in range(n_events):
        start_idx = rng.integers(0, n - 400)
        duration = rng.integers(200, 400)
        end_idx = min(start_idx + duration, n)

        freq_noise = np.sin(np.linspace(0, 20 * np.pi, end_idx - start_idx))
        df.loc[start_idx:end_idx - 1, "vibration_x"] += (3.0 + freq_noise * 2.0) * rng.uniform(0.8, 1.5)
        df.loc[start_idx:end_idx - 1, "vibration_y"] += (2.5 + freq_noise * 1.5) * rng.uniform(0.8, 1.5)
        df.loc[start_idx:end_idx - 1, "rpm"] += rng.normal(0, 30, end_idx - start_idx)

    return df


def inject_lubrication_issues(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(df)
    n_events = rng.integers(1, 3)

    for _ in range(n_events):
        start_idx = rng.integers(0, n - 500)
        duration = rng.integers(300, 500)
        end_idx = min(start_idx + duration, n)
        ramp = np.linspace(0, 1, end_idx - start_idx)

        df.loc[start_idx:end_idx - 1, "oil_temperature"] += ramp * rng.uniform(10, 25)
        df.loc[start_idx:end_idx - 1, "bearing_temperature"] += ramp * rng.uniform(8, 20)
        df.loc[start_idx:end_idx - 1, "vibration_x"] += ramp * rng.uniform(0.5, 2.0)
        df.loc[start_idx:end_idx - 1, "power_consumption"] += ramp * rng.uniform(10, 30)

    return df


def inject_pressure_instability(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(df)
    n_events = rng.integers(2, 5)

    for _ in range(n_events):
        start_idx = rng.integers(0, n - 100)
        duration = rng.integers(30, 100)
        end_idx = min(start_idx + duration, n)

        oscillation = np.sin(np.linspace(0, 10 * np.pi, end_idx - start_idx))
        df.loc[start_idx:end_idx - 1, "suction_pressure"] += oscillation * rng.uniform(8, 20)
        df.loc[start_idx:end_idx - 1, "discharge_pressure"] += oscillation * rng.uniform(15, 40)
        df.loc[start_idx:end_idx - 1, "flow_rate"] += oscillation * rng.uniform(30, 80)

    return df


def inject_sensor_drift(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(df)
    sensors = ["suction_pressure", "bearing_temperature", "vibration_x"]
    chosen = rng.choice(sensors)
    drift = np.linspace(0, rng.uniform(5, 15), n) * rng.choice([-1, 1])
    df[chosen] += drift
    return df


def inject_sudden_spikes(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(df)
    n_spikes = rng.integers(5, 20)
    spike_indices = rng.integers(0, n, n_spikes)
    sensors = ["vibration_x", "vibration_y", "bearing_temperature", "discharge_pressure"]

    for idx in spike_indices:
        sensor = rng.choice(sensors)
        multiplier = rng.uniform(2.5, 5.0)
        df.loc[idx, sensor] = df.loc[idx, sensor] * multiplier

    return df


def inject_sensor_noise(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    n = len(df)
    start_idx = rng.integers(0, n - 500)
    duration = rng.integers(200, 500)
    end_idx = min(start_idx + duration, n)

    sensors = ["vibration_x", "vibration_y", "suction_pressure"]
    for sensor in sensors:
        noise = rng.normal(0, NORMAL_PARAMS.get(sensor, (0, 1))[1] * 2, end_idx - start_idx)
        df.loc[start_idx:end_idx - 1, sensor] += noise

    return df


def generate_dataset(output_path: Path | None = None) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    all_frames = []

    anomaly_injectors = [
        inject_gradual_degradation,
        inject_cavitation,
        inject_overheating,
        inject_imbalance,
        inject_lubrication_issues,
        inject_pressure_instability,
        inject_sensor_drift,
        inject_sudden_spikes,
        inject_sensor_noise,
    ]

    for comp_id in COMPRESSOR_IDS:
        df = generate_base_data(rng, HOURS_PER_COMPRESSOR, comp_id)

        n_anomalies = rng.integers(3, 6)
        chosen_injectors = rng.choice(anomaly_injectors, n_anomalies, replace=False)
        for injector in chosen_injectors:
            df = injector(df, rng)

        df["efficiency_score"] = df["efficiency_score"].clip(50, 100)
        df["suction_pressure"] = df["suction_pressure"].clip(10, 80)
        df["discharge_pressure"] = df["discharge_pressure"].clip(100, 300)
        df["vibration_x"] = df["vibration_x"].clip(0.1, 25)
        df["vibration_y"] = df["vibration_y"].clip(0.1, 25)
        df["bearing_temperature"] = df["bearing_temperature"].clip(30, 150)
        df["oil_temperature"] = df["oil_temperature"].clip(25, 120)
        df["rpm"] = df["rpm"].clip(2000, 5000)
        df["flow_rate"] = df["flow_rate"].clip(200, 1200)
        df["power_consumption"] = df["power_consumption"].clip(200, 800)

        all_frames.append(df)

    dataset = pd.concat(all_frames, ignore_index=True)
    dataset = dataset.sort_values(["compressor_id", "timestamp"]).reset_index(drop=True)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dataset.to_csv(output_path, index=False)
        print(f"Dataset saved: {output_path} ({len(dataset)} rows)")

    return dataset


if __name__ == "__main__":
    from backend.utils.config import DATA_DIR, ensure_dirs
    ensure_dirs()
    generate_dataset(DATA_DIR / "compressor_telemetry.csv")
