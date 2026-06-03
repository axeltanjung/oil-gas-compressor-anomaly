"""
Dynamic Thresholding System

Implements adaptive anomaly thresholds:
- Rolling statistical threshold
- Percentile-based threshold
- EWMA-based threshold
- Dynamic confidence bands
"""
from __future__ import annotations

import numpy as np
import pandas as pd


class RollingThreshold:
    def __init__(self, window: int = 168, n_sigma: float = 3.0):
        self.window = window
        self.n_sigma = n_sigma

    def compute(self, scores: np.ndarray) -> dict:
        series = pd.Series(scores)
        rolling_mean = series.rolling(self.window, min_periods=1).mean()
        rolling_std = series.rolling(self.window, min_periods=1).std().fillna(0)

        upper_bound = rolling_mean + self.n_sigma * rolling_std
        lower_bound = rolling_mean - self.n_sigma * rolling_std

        is_anomaly = (scores > upper_bound.values).astype(int)

        return {
            "threshold": upper_bound.values,
            "lower_bound": lower_bound.values,
            "rolling_mean": rolling_mean.values,
            "is_anomaly": is_anomaly,
        }


class PercentileThreshold:
    def __init__(self, window: int = 168, percentile: float = 97.5):
        self.window = window
        self.percentile = percentile

    def compute(self, scores: np.ndarray) -> dict:
        series = pd.Series(scores)
        threshold = series.rolling(self.window, min_periods=1).quantile(self.percentile / 100.0)
        is_anomaly = (scores > threshold.values).astype(int)

        return {
            "threshold": threshold.values,
            "is_anomaly": is_anomaly,
        }


class EWMAThreshold:
    def __init__(self, span: int = 168, n_sigma: float = 3.0):
        self.span = span
        self.n_sigma = n_sigma

    def compute(self, scores: np.ndarray) -> dict:
        series = pd.Series(scores)
        ewma_mean = series.ewm(span=self.span).mean()
        ewma_std = series.ewm(span=self.span).std().fillna(0)

        upper_bound = ewma_mean + self.n_sigma * ewma_std
        lower_bound = ewma_mean - self.n_sigma * ewma_std

        is_anomaly = (scores > upper_bound.values).astype(int)

        return {
            "threshold": upper_bound.values,
            "lower_bound": lower_bound.values,
            "ewma_mean": ewma_mean.values,
            "is_anomaly": is_anomaly,
        }


class DynamicConfidenceBands:
    def __init__(self, window: int = 336, confidence: float = 0.95):
        self.window = window
        self.confidence = confidence
        self.z_score = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}.get(confidence, 1.96)

    def compute(self, scores: np.ndarray) -> dict:
        series = pd.Series(scores)
        rolling_mean = series.rolling(self.window, min_periods=1).mean()
        rolling_std = series.rolling(self.window, min_periods=1).std().fillna(0)

        upper = rolling_mean + self.z_score * rolling_std
        lower = rolling_mean - self.z_score * rolling_std

        is_anomaly = ((scores > upper.values) | (scores < lower.values)).astype(int)

        return {
            "upper_band": upper.values,
            "lower_band": lower.values,
            "center": rolling_mean.values,
            "is_anomaly": is_anomaly,
        }


class AdaptiveThresholdEngine:
    def __init__(self):
        self.rolling = RollingThreshold()
        self.percentile = PercentileThreshold()
        self.ewma = EWMAThreshold()
        self.confidence = DynamicConfidenceBands()

    def evaluate_all(self, scores: np.ndarray) -> dict:
        return {
            "rolling": self.rolling.compute(scores),
            "percentile": self.percentile.compute(scores),
            "ewma": self.ewma.compute(scores),
            "confidence_bands": self.confidence.compute(scores),
        }

    def ensemble_decision(self, scores: np.ndarray, min_votes: int = 2) -> dict:
        results = self.evaluate_all(scores)
        votes = np.zeros(len(scores))

        for method_result in results.values():
            votes += method_result["is_anomaly"]

        final_anomaly = (votes >= min_votes).astype(int)

        return {
            "is_anomaly": final_anomaly,
            "vote_count": votes.astype(int),
            "methods": results,
        }
