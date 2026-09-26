"""Temporal baseline predictor and anomaly scorer."""

import numpy as np
import pandas as pd
from typing import Dict, Any
from skyguard.temporal.rolling import RollingTemporalFeatures
from skyguard.temporal.diurnal import DiurnalCycleEngine


class TemporalEngine:
    """Combines rolling multi-scale stats and diurnal baselines to produce continuous temporal anomaly scores."""

    def __init__(self):
        self.rolling = RollingTemporalFeatures()
        self.diurnal = DiurnalCycleEngine()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.diurnal.compute_diurnal_deviation(df)
        df = self.rolling.transform(df)

        # Composite temporal anomaly score based on extreme z-scores
        z_temp = np.abs(df["temperature_zscore_12"].fillna(0.0))
        z_press = np.abs(df["pressure_zscore_12"].fillna(0.0))
        z_rh = np.abs(df["relative_humidity_zscore_12"].fillna(0.0))

        max_z = np.maximum(z_temp, np.maximum(z_press, z_rh))
        # Sigmoid transform to map z-score to [0, 1] probability
        df["temporal_anomaly_score"] = 1.0 / (1.0 + np.exp(-1.2 * (max_z - 3.0)))
        return df
