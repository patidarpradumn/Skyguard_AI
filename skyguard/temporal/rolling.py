"""Rolling temporal statistical features for AWS time series."""

import numpy as np
import pandas as pd
from typing import List, Dict, Any


class RollingTemporalFeatures:
    """Computes multi-scale window statistics: EWMA, rolling mean, std, z-scores, min, max, range."""

    def __init__(self, windows: List[int] = [4, 12, 24, 96]): # 1h, 3h, 6h, 24h at 15-min sampling
        self.windows = windows

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Group by station to prevent inter-station leakage
        processed = []
        for _, group in df.groupby("station_id"):
            g = group.copy().sort_values("timestamp")
            
            for param in ["temperature", "pressure", "relative_humidity"]:
                # EWMA (short-term smoothing)
                g[f"{param}_ewma_4"] = g[param].ewm(span=4, adjust=False).mean()
                g[f"{param}_ewma_24"] = g[param].ewm(span=24, adjust=False).mean()

                for w in self.windows:
                    roll = g[param].rolling(window=w, min_periods=max(1, w // 4))
                    g[f"{param}_roll_mean_{w}"] = roll.mean()
                    g[f"{param}_roll_std_{w}"] = roll.std().fillna(1e-5)
                    g[f"{param}_roll_min_{w}"] = roll.min()
                    g[f"{param}_roll_max_{w}"] = roll.max()
                    g[f"{param}_roll_range_{w}"] = g[f"{param}_roll_max_{w}"] - g[f"{param}_roll_min_{w}"]
                    
                    # Rolling Z-score
                    g[f"{param}_zscore_{w}"] = (g[param] - g[f"{param}_roll_mean_{w}"]) / (g[f"{param}_roll_std_{w}"] + 1e-4)

            processed.append(g)

        return pd.concat(processed, ignore_index=True)
