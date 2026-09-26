"""Rolling multivariate correlation and thermodynamic coherence metrics."""

import numpy as np
import pandas as pd
from typing import Dict, Any


class MultivariateCoherenceEngine:
    """Computes rolling pairwise correlations between T, P, RH and evaluates physical joint dynamics."""

    def __init__(self, window: int = 16): # 4 hours
        self.window = window

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        processed = []
        for _, group in df.groupby("station_id"):
            g = group.copy().sort_values("timestamp")
            
            # Rolling correlations
            roll = g[["temperature", "pressure", "relative_humidity"]].rolling(window=self.window, min_periods=4)
            # corr(T, RH) is physically expected to be negative (-0.7 to -0.9) during diurnal heating
            g["corr_temp_rh_16"] = g["temperature"].rolling(self.window).corr(g["relative_humidity"]).fillna(0.0)
            g["corr_temp_press_16"] = g["temperature"].rolling(self.window).corr(g["pressure"]).fillna(0.0)
            g["corr_press_rh_16"] = g["pressure"].rolling(self.window).corr(g["relative_humidity"]).fillna(0.0)

            # Multivariate joint gradient consistency:
            # During convective rain/squalls, dT < 0 and dRH > 0 and dP can be dynamic.
            # In a faulty sensor spike, dT >> 0 while dRH ~ 0 and dP ~ 0.
            # We construct a ratio of isolated variance:
            dt = g["temperature"].diff().fillna(0).abs()
            drh = g["relative_humidity"].diff().fillna(0).abs()
            dp = g["pressure"].diff().fillna(0).abs()

            total_activity = dt + (drh / 5.0) + (dp * 2.0) + 1e-4
            g["isolated_temp_fraction"] = dt / total_activity
            g["isolated_press_fraction"] = (dp * 2.0) / total_activity
            g["isolated_rh_fraction"] = (drh / 5.0) / total_activity

            processed.append(g)

        return pd.concat(processed, ignore_index=True)
