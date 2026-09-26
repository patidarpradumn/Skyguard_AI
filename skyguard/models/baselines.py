"""Baseline anomaly detectors for benchmarking against SkyGuard AI.
Implements:
1. Rule-Based Threshold Detector (WMO / IMD QC guidelines)
2. Isolation Forest (Unsupervised tree isolation)
3. Temporal Rolling Z-score Detector
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, Tuple


class RuleBasedQCDetector:
    """Conventional meteorological threshold QC rule detector."""

    def __init__(
        self,
        temp_min_c: float = -40.0,
        temp_max_c: float = 60.0,
        temp_max_rate_15m: float = 6.0,
        pressure_min_hpa: float = 500.0,
        pressure_max_hpa: float = 1080.0,
        pressure_max_rate_15m: float = 4.0,
        rh_min_pct: float = 0.0,
        rh_max_pct: float = 100.0,
        rh_max_rate_15m: float = 30.0,
        stuck_consecutive: int = 6
    ):
        self.temp_min_c = temp_min_c
        self.temp_max_c = temp_max_c
        self.temp_max_rate_15m = temp_max_rate_15m
        self.pressure_min_hpa = pressure_min_hpa
        self.pressure_max_hpa = pressure_max_hpa
        self.pressure_max_rate_15m = pressure_max_rate_15m
        self.rh_min_pct = rh_min_pct
        self.rh_max_pct = rh_max_pct
        self.rh_max_rate_15m = rh_max_rate_15m
        self.stuck_consecutive = stuck_consecutive

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Returns binary anomaly predictions (0: Normal, 1: Anomaly)."""
        df = df.copy()
        n = len(df)
        preds = np.zeros(n, dtype=int)

        # 1. Range violations
        t_out = (df["temperature"] < self.temp_min_c) | (df["temperature"] > self.temp_max_c) | df["temperature"].isna()
        p_out = (df["pressure"] < self.pressure_min_hpa) | (df["pressure"] > self.pressure_max_hpa) | df["pressure"].isna()
        rh_out = (df["relative_humidity"] < self.rh_min_pct) | (df["relative_humidity"] > self.rh_max_pct) | df["relative_humidity"].isna()
        range_fail = t_out | p_out | rh_out

        # 2. Rate of change
        dt = df["temperature"].diff().abs().fillna(0) > self.temp_max_rate_15m
        dp = df["pressure"].diff().abs().fillna(0) > self.pressure_max_rate_15m
        drh = df["relative_humidity"].diff().abs().fillna(0) > self.rh_max_rate_15m
        rate_fail = dt | dp | drh

        # 3. Stuck check
        diff = (df["temperature"] != df["temperature"].shift(1)).cumsum()
        counts = df.groupby(diff)["temperature"].transform("size")
        stuck_fail = counts >= self.stuck_consecutive

        preds[range_fail | rate_fail | stuck_fail] = 1
        return preds


class IsolationForestDetector:
    """Unsupervised Isolation Forest baseline on raw T/P/RH features."""

    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.model = IsolationForest(
            n_estimators=150,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1
        )
        self.is_fitted = False

    def fit(self, df: pd.DataFrame):
        X = df[["temperature", "pressure", "relative_humidity"]].fillna(0.0).values
        self.model.fit(X)
        self.is_fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            self.fit(df)
        X = df[["temperature", "pressure", "relative_humidity"]].fillna(0.0).values
        raw_pred = self.model.predict(X)
        # sklearn returns -1 for anomaly, 1 for inlier
        return np.where(raw_pred == -1, 1, 0)
