"""Diurnal solar harmonic modeling and expected temporal baselines."""

import numpy as np
import pandas as pd
from typing import Dict, Any


class DiurnalCycleEngine:
    """Models 24-hour diurnal cycle variations and temporal cyclical features."""

    @staticmethod
    def extract_time_features(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        ts = pd.to_datetime(df["timestamp"], utc=True)

        hour = ts.dt.hour + ts.dt.minute / 60.0
        month = ts.dt.month

        # Cyclical encoding of hour-of-day (sine/cosine transforms)
        df["hour_sin"] = np.sin(2 * np.pi * hour / 24.0)
        df["hour_cos"] = np.cos(2 * np.pi * hour / 24.0)

        # Cyclical encoding of month-of-year
        df["month_sin"] = np.sin(2 * np.pi * month / 12.0)
        df["month_cos"] = np.cos(2 * np.pi * month / 12.0)

        return df

    def compute_diurnal_deviation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Computes deviation from typical hourly mean per station."""
        df = self.extract_time_features(df)
        df["hour_int"] = pd.to_datetime(df["timestamp"], utc=True).dt.hour

        processed = []
        for _, group in df.groupby("station_id"):
            g = group.copy()
            # Calculate hourly mean baseline
            hourly_means = g.groupby("hour_int")[["temperature", "pressure", "relative_humidity"]].transform("mean")
            hourly_stds = g.groupby("hour_int")[["temperature", "pressure", "relative_humidity"]].transform("std").fillna(1.0)

            for col in ["temperature", "pressure", "relative_humidity"]:
                g[f"{col}_diurnal_dev"] = g[col] - hourly_means[col]
                g[f"{col}_diurnal_z"] = (g[col] - hourly_means[col]) / (hourly_stds[col] + 1e-4)

            processed.append(g)

        out_df = pd.concat(processed, ignore_index=True)
        return out_df.drop(columns=["hour_int"])
