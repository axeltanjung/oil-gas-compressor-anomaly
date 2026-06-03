# Oil & Gas Compressor Anomaly Detection Platform

> Production-grade, AI-powered anomaly detection system for industrial compressors and turbines.
> Detects **abnormal operating conditions**, **early degradation**, **sensor anomalies**, and **operational drift**
> using unsupervised and semi-supervised machine learning — with a modern dark industrial dashboard.

[![Python](https://img.shields.io/badge/python-3.11-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688)]()
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2-EE4C2C)]()
[![React](https://img.shields.io/badge/React-Vite-61dafb)]()
[![Docker](https://img.shields.io/badge/Docker-compose-2496ED)]()
[![MLflow](https://img.shields.io/badge/MLflow-2.13-0194E2)]()

---

## Table of Contents
1. [Project Background](#project-background)
2. [Business Benefits](#business-benefits)
3. [Domain Knowledge](#domain-knowledge)
4. [AI/ML Architecture](#aiml-architecture)
5. [System Architecture](#system-architecture)
6. [Project Structure](#project-structure)
7. [Quick Start (Docker)](#quick-start-docker)
8. [Local Development](#local-development)
9. [ML Pipeline & Models](#ml-pipeline--models)
10. [MLflow](#mlflow)
11. [API Documentation](#api-documentation)
12. [Dashboard](#dashboard)
13. [Future Improvements](#future-improvements)

---

## Project Background

Compressors are the backbone of Oil & Gas operations. They are critical rotating equipment used in:
- **Gas transportation** — pipeline compression stations
- **LNG facilities** — refrigeration compressors
- **Offshore production** — gas lift and injection
- **Refinery operations** — catalytic cracking, hydroprocessing
- **Pipeline systems** — mainline compression

Unexpected compressor failure causes:
- **Production shutdown** — $500K-$5M/day losses
- **Safety hazards** — high-pressure gas release risks
- **Pressure instability** — cascade effects on downstream equipment
- **Equipment damage** — secondary failures in connected systems
- **Environmental incidents** — gas leaks and emissions

### Why AI-Based Anomaly Detection?

Traditional monitoring relies on **static threshold alarms** (e.g., "alert if vibration > 10 mm/s"). This approach:
- Cannot detect **gradual degradation** until it's too late
- Generates excessive **false alarms** due to load variation
- Misses **multivariate anomalies** that appear normal in individual sensors
- Cannot **adapt** to changing operating conditions

This platform introduces **adaptive, intelligent monitoring** using unsupervised ML that learns normal behavior and identifies deviations before failures occur.

---

## Business Benefits

| Benefit | Impact |
|---------|--------|
| Reduced unplanned downtime | 30-50% reduction in emergency shutdowns |
| Predictive maintenance | Replace time-based with condition-based scheduling |
| Lower maintenance costs | 20-40% reduction through targeted interventions |
| Improved safety | Early detection of hazardous conditions |
| Extended equipment life | 15-25% improvement through early degradation detection |
| Operational efficiency | Optimized performance through continuous monitoring |
| Regulatory compliance | Documented condition monitoring and maintenance records |

---

## Domain Knowledge

### Compressor Operations
- **Centrifugal compressors** convert kinetic energy to pressure through high-speed impellers
- **Reciprocating compressors** use pistons to compress gas in cylinders
- Normal operating envelope: 3400-3800 RPM, 3.5-5.0 pressure ratio

### Key Failure Modes

| Failure Mode | Indicators | Risk Level |
|-------------|-----------|-----------|
| **Cavitation** | Low suction pressure, high vibration, flow instability | High |
| **Bearing failure** | Rising temperature, increasing vibration, metallic debris | Critical |
| **Imbalance/Misalignment** | Vibration at 1x/2x RPM, phase shift | High |
| **Overheating** | Rising bearing and oil temps, reduced efficiency | High |
| **Lubrication degradation** | Gradual temperature rise, bearing noise | Medium |
| **Surge** | Pressure oscillation, flow reversal, high vibration | Critical |
| **Seal degradation** | Gas leakage, pressure loss, temperature change | Medium |

### Vibration Analysis Concepts
- **1X vibration** — imbalance indication
- **2X vibration** — misalignment or looseness
- **Sub-synchronous** — oil whirl/whip (bearing instability)
- **High-frequency** — gear mesh, blade pass, or early bearing damage

---

## AI/ML Architecture

### Unsupervised Learning Approach

In industrial environments, **labeled failure data is extremely scarce** because:
- Failures are rare (MTBF > 10,000 hours)
- Shutdown events are expensive to study
- Many anomalies are never formally labeled

This platform uses **unsupervised and semi-supervised** methods:

```
                    ┌─────────────────────────────────────────────┐
                    │         ANOMALY DETECTION PIPELINE           │
                    └─────────────────────┬───────────────────────┘
                                          │
                    ┌─────────────────────▼───────────────────────┐
                    │            Feature Engineering                │
                    │  Pressure Ratio · Vibration Magnitude         │
                    │  Rolling Statistics · Rate of Change           │
                    └────┬───────────┬───────────┬───────────┬────┘
                         │           │           │           │
                    ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌────▼────┐
                    │Isolation│ │  Auto-  │ │  VAE    │ │  LSTM   │
                    │ Forest  │ │ encoder │ │         │ │Forecast │
                    └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
                         │           │           │           │
                    ┌────▼───────────▼───────────▼───────────▼────┐
                    │          Ensemble Scoring                     │
                    │    Dynamic Thresholding (Rolling/EWMA)         │
                    └─────────────────────┬───────────────────────┘
                                          │
                    ┌─────────────────────▼───────────────────────┐
                    │          Health Index (0-100)                 │
                    │    SHAP Explainability & Recommendations       │
                    └─────────────────────────────────────────────┘
```

### Models

| Model | Purpose | Method |
|-------|---------|--------|
| **Isolation Forest** | Classical baseline | Tree-based anomaly isolation |
| **Autoencoder** | Reconstruction error | Neural network learns normal patterns |
| **VAE** | Probabilistic scoring | Latent space + KL divergence |
| **LSTM Forecaster** | Temporal anomalies | Predict future → detect deviations |

### Adaptive Thresholding
- **Rolling Statistical** — μ ± 3σ over sliding window
- **Percentile-based** — 97.5th percentile rolling threshold
- **EWMA** — Exponentially weighted moving average bands
- **Ensemble** — Majority vote across methods

---

## System Architecture

```
                     ┌──────────────────────────────────────────────┐
                     │           React + Vite Dashboard              │
                     │  Overview · Detail · Insights · Maintenance   │
                     │  TailwindCSS · Recharts · Framer Motion       │
                     └───────────────────────┬──────────────────────┘
                                             │  REST (Axios)
                                             ▼
                     ┌──────────────────────────────────────────────┐
                     │               FastAPI Backend                  │
                     │  /health /anomaly/predict /compressor/{id}     │
                     │  /dashboard/summary /insights/explain          │
                     │  Pydantic · Logging · Error handling           │
                     └───────┬───────────────┬──────────────────────┘
                             │               │
                 ┌───────────▼──┐   ┌────────▼─────────────────────┐
                 │ Model Registry│   │  Services                     │
                 │ IsolationForest│  │  Inference · Health Index     │
                 │ Autoencoder   │   │  Explainability · Thresholding│
                 │ VAE · LSTM    │   │  Maintenance Recommendations  │
                 └───────────────┘   └──────────────────────────────┘
                                             │
                     ┌───────────────────────▼──────────────────────┐
                     │         SQLite + CSV Data Store                │
                     │  Telemetry · Predictions · Health History      │
                     └──────────────────────────────────────────────┘
```

---

## Project Structure

```
oil-gas-compressor-anomaly/
├── backend/
│   ├── api/
│   │   ├── main.py                 # FastAPI entrypoint
│   │   ├── schemas.py              # Pydantic models
│   │   └── routes/
│   │       ├── health.py           # Health check
│   │       ├── predict.py          # Anomaly prediction
│   │       ├── dashboard.py        # Dashboard data
│   │       ├── compressor.py       # Compressor detail
│   │       └── insights.py         # AI insights & maintenance
│   ├── anomaly/
│   │   ├── isolation_forest.py     # Model 1: Isolation Forest
│   │   ├── autoencoder.py          # Model 2: Autoencoder
│   │   ├── vae.py                  # Model 3: VAE
│   │   ├── lstm_forecaster.py      # Model 4: LSTM
│   │   └── dynamic_threshold.py    # Adaptive thresholding
│   ├── training/
│   │   ├── synthetic_data_generator.py
│   │   ├── preprocessing.py        # Feature engineering
│   │   ├── train_pipeline.py       # Full training orchestration
│   │   └── mlflow_utils.py         # MLflow integration
│   ├── explainability/
│   │   └── shap_explainer.py       # SHAP + recommendations
│   ├── services/
│   │   ├── health_index.py         # Composite health scoring
│   │   └── inference.py            # Production inference
│   └── utils/
│       ├── config.py               # Settings & paths
│       └── logging_config.py       # Logging setup
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Router & layout
│   │   ├── pages/
│   │   │   ├── Overview.jsx        # Executive dashboard
│   │   │   ├── CompressorDetail.jsx
│   │   │   ├── AIInsights.jsx      # SHAP explainability
│   │   │   ├── Maintenance.jsx     # Recommendations
│   │   │   └── DataExplorer.jsx    # Raw data visualization
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── KpiCard.jsx
│   │   │   ├── HealthGauge.jsx
│   │   │   └── LoadingState.jsx
│   │   └── lib/
│   │       └── api.js              # Axios client
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Quick Start (Docker)

```bash
# Clone and enter directory
cd oil-gas-compressor-anomaly

# Copy environment file
cp .env.example .env

# Build and start all services
docker-compose up --build

# Access:
# Dashboard:  http://localhost:3000
# API Docs:   http://localhost:8000/docs
# MLflow UI:  http://localhost:5000
```

---

## Local Development

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Generate synthetic data
python -m backend.training.synthetic_data_generator

# Train all models
python -m backend.training.train_pipeline

# Start API server
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard available at http://localhost:5173
```

### MLflow

```bash
mlflow ui --port 5000 --backend-store-uri ./mlflow/mlruns
```

---

## ML Pipeline & Models

### Training Pipeline

```bash
python -m backend.training.train_pipeline
```

This will:
1. Generate/load 150,000+ rows of synthetic telemetry
2. Engineer 21 features (11 raw + 10 derived)
3. Train 4 anomaly detection models
4. Log experiments to MLflow
5. Save models to `models/` directory

### Synthetic Data

The generator creates realistic compressor telemetry with:
- 8 compressor units, hourly readings
- Injected anomaly patterns: cavitation, overheating, imbalance, lubrication issues, pressure instability, sensor drift, sudden spikes

### Model Performance

| Model | Training Time | Anomaly Detection Rate | False Positive Rate |
|-------|--------------|----------------------|-------------------|
| Isolation Forest | ~5s | ~5% (tuned) | Low |
| Autoencoder | ~2min (50 epochs) | Adaptive | Very Low |
| VAE | ~3min (60 epochs) | Probabilistic | Very Low |
| LSTM | ~5min (30 epochs) | Temporal | Low |

---

## MLflow

All training runs are tracked with MLflow:
- **Parameters**: model architecture, hyperparameters
- **Metrics**: loss, threshold, anomaly counts
- **Artifacts**: model files, training summaries

```bash
# View experiments
mlflow ui --port 5000 --backend-store-uri ./mlflow/mlruns
```

---

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive Swagger UI.

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/anomaly/predict` | POST | Single reading prediction |
| `/anomaly/batch` | POST | Batch prediction |
| `/compressor/{id}` | GET | Compressor sensor history |
| `/compressor/{id}/health-history` | GET | Health score timeline |
| `/dashboard/summary` | GET | Executive overview data |
| `/dashboard/anomaly-trend` | GET | Trend data |
| `/insights/explain/{id}` | GET | SHAP explainability |
| `/insights/health-score/{id}` | GET | Current health score |
| `/insights/maintenance-recommendations` | GET | AI maintenance advice |

---

## Dashboard

The dashboard features a modern industrial aesthetic with:
- **Dark theme** with neon accents (SCADA-inspired)
- **Glassmorphism** card styling
- **Animated KPI cards** with Framer Motion
- **Interactive charts** via Recharts
- **Health gauges** with animated SVG arcs
- **Responsive layout** for all screen sizes

### Pages
1. **Executive Overview** — KPIs, health distribution, trend charts, compressor health map
2. **Compressor Detail** — Sensor history, health gauge, tabbed analysis
3. **AI Insights** — SHAP drivers, radar chart, severity scoring, recommendations
4. **Maintenance** — Priority-ranked recommendations with action items
5. **Data Explorer** — Raw sensor data with statistics and filtering

---

## Future Improvements

- **Edge deployment** — TensorRT/ONNX for real-time inference at field devices
- **Online learning** — Continuous model adaptation to evolving operating conditions
- **Digital twin integration** — Physics-informed ML combining first-principles models
- **Reinforcement learning** — Optimal maintenance scheduling optimization
- **Streaming architecture** — Kafka/Flink for sub-second anomaly detection
- **Multi-facility support** — Fleet-wide anomaly detection across sites
- **Natural language reports** — LLM-generated maintenance summaries
- **AR/VR integration** — Augmented reality for field technician guidance

---

## License

This project is for educational and portfolio demonstration purposes.

---

*Built with expertise in Industrial AI, Predictive Maintenance, and Oil & Gas Operations.*
