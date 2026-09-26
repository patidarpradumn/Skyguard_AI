"""Unit standardizer and conversion utilities for meteorological observations."""

import numpy as np
import pandas as pd
from typing import Dict, Any, Union


class MeteorologicalNormalizer:
    """Standardizes units and cleans sentinel/invalid representations."""

    @staticmethod
    def fahrenheit_to_celsius(f: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
        return (f - 32.0) * (5.0 / 9.0)

    @staticmethod
    def inhg_to_hpa(inhg: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
        return inhg * 33.863886666667

    @staticmethod
    def pa_to_hpa(pa: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
        return pa / 100.0

    @staticmethod
    def kelvin_to_celsius(k: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
        return k - 273.15

    @classmethod
    def clean_sentinels(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Replaces common telemetry sentinel values (-999, 999, 9999, 999.9, -99.9) with NaN."""
        df = df.copy()
        sentinels = [-999.0, -999, 999.0, 999, 9999.0, 9999, -9999.0, 999.9, -99.9, -99999.0]
        numeric_cols = ["temperature", "pressure", "relative_humidity"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].replace(sentinels, np.nan)
        return df

    @classmethod
    def standardize_units(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Heuristically detects and converts non-standard units if present."""
        df = df.copy()
        df = cls.clean_sentinels(df)

        # Detect temperature in Kelvin or Fahrenheit
        if "temperature" in df.columns:
            mean_temp = df["temperature"].dropna().mean()
            if mean_temp > 200.0:  # Kelvin
                df["temperature"] = cls.kelvin_to_celsius(df["temperature"])
            elif mean_temp > 70.0 and mean_temp < 150.0:  # Fahrenheit
                df["temperature"] = cls.fahrenheit_to_celsius(df["temperature"])

        # Detect pressure in Pa or inHg
        if "pressure" in df.columns:
            mean_p = df["pressure"].dropna().mean()
            if mean_p > 20000.0:  # Pascals
                df["pressure"] = cls.pa_to_hpa(df["pressure"])
            elif mean_p < 40.0 and mean_p > 20.0:  # inHg
                df["pressure"] = cls.inhg_to_hpa(df["pressure"])

        # Clamp humidity
        if "relative_humidity" in df.columns:
            df["relative_humidity"] = np.clip(df["relative_humidity"], 0.0, 100.0)

        return df
