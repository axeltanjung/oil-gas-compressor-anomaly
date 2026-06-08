from __future__ import annotations
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Compressor Anomaly Detection Platform"
    version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    mlflow_tracking_uri: str = "./mlflow/mlruns"
    database_url: str = "sqlite:///./data/compressor.db"
    anomaly_contamination: float = 0.05
    health_critical_threshold: int = 25
    health_warning_threshold: int = 50
    health_minor_threshold: int = 75

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
EXPORTS_DIR = BASE_DIR / "exports"
MLFLOW_DIR = BASE_DIR / "mlflow"


def ensure_dirs():
    for d in [DATA_DIR, MODELS_DIR, EXPORTS_DIR, MLFLOW_DIR]:
        d.mkdir(parents=True, exist_ok=True)
