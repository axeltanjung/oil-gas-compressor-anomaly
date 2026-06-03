"""
FastAPI application entrypoint.

Run:
    uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import health, predict, dashboard, compressor, insights
from backend.utils.config import settings
from backend.utils.logging_config import get_logger

log = get_logger("api")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=(
        "AI-powered anomaly detection platform for industrial compressors. "
        "Detects abnormal operating conditions, early degradation, and sensor anomalies "
        "using Isolation Forest, Autoencoder, VAE, and LSTM models."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = (time.time() - start) * 1000
    log.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, elapsed)
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(health.router)
app.include_router(predict.router)
app.include_router(dashboard.router)
app.include_router(compressor.router)
app.include_router(insights.router)


@app.get("/", tags=["root"])
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "endpoints": [
            "/health",
            "/anomaly/predict",
            "/anomaly/batch",
            "/compressor/{id}",
            "/dashboard/summary",
            "/dashboard/anomaly-trend",
            "/insights/explain/{id}",
            "/insights/health-score/{id}",
            "/insights/maintenance-recommendations",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host=settings.api_host, port=settings.api_port, reload=True)
