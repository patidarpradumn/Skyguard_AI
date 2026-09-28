"""Quality control routines for Automatic Weather Station observations.
Implements WMO-No. 8 & IMD Quality Control standards.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple


class QualityControlEngine:
    """Deterministic Quality Control (QC) engine for AWS observations.
    
    Evaluates:
    1. Plausibility range checks (WMO / IMD bounds)
    2. Rate-of-change / step limits (e.g. max °C change per 15 min)
    3. Persistence / stuck value test (repeated exact decimals)
    4. Sentinel / corrupted value flags
    """

    def __init__(
        self,
        temp_min_c: float = -40.0,
        temp_max_c: float = 60.0,
        temp_max_step_15min_c: float = 8.0,
        pressure_min_hpa: float = 500.0,
        pressure_max_hpa: float = 1080.0,
        pressure_max_step_15min_hpa: float = 6.0,
        rh_min_pct: float = 0.0,
        rh_max_pct: float = 100.0,
        rh_max_step_15min_pct: float = 40.0,
        consecutive_stuck_threshold: int = 6
    ):
        self.temp_min_c = temp_min_c
        self.temp_max_c = temp_max_c
        self.temp_max_step_15min_c = temp_max_step_15min_c

        self.pressure_min_hpa = pressure_min_hpa
        self.pressure_max_hpa = pressure_max_hpa
        self.pressure_max_step_15min_hpa = pressure_max_step_15min_hpa

        self.rh_min_pct = rh_min_pct
        self.rh_max_pct = rh_max_pct
        self.rh_max_step_15min_pct = rh_max_step_15min_pct

        self.consecutive_stuck_threshold = consecutive_stuck_threshold

    def check_observation_limits(self, temp: float, pressure: float, rh: float) -> Tuple[bool, List[str]]:
        """Checks whether a single observation is within climatological limits."""
        flags = []
        if np.isnan(temp) or temp < self.temp_min_c or temp > self.temp_max_c:
            flags.append(f"TEMP_OUT_OF_BOUNDS_{temp}")

        if np.isnan(pressure) or pressure < self.pressure_min_hpa or pressure > self.pressure_max_hpa:
            flags.append(f"PRESSURE_OUT_OF_BOUNDS_{pressure}")

        if np.isnan(rh) or rh < self.rh_min_pct or rh > self.rh_max_pct:
            flags.append(f"RH_OUT_OF_BOUNDS_{rh}")

        is_valid = len(flags) == 0
        return is_valid, flags

    def check_series_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processes a time-series dataframe and appends boolean and categorical QC flags."""
        df = df.copy()
        if "timestamp" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # 1. Range limit flags
        temp_valid = (df["temperature"] >= self.temp_min_c) & (df["temperature"] <= self.temp_max_c)
        press_valid = (df["pressure"] >= self.pressure_min_hpa) & (df["pressure"] <= self.pressure_max_hpa)
        rh_valid = (df["relative_humidity"] >= self.rh_min_pct) & (df["relative_humidity"] <= self.rh_max_pct)
        df["qc_range_valid"] = temp_valid & press_valid & rh_valid

        # 2. Rate of change (step) test
        dt_minutes = df["timestamp"].diff().dt.total_seconds() / 60.0
        # If sampling is ~15 min, normalize rate
        dt_scale = np.where((dt_minutes > 0) & (dt_minutes <= 60), 15.0 / dt_minutes, 1.0)

        dt_temp = (df["temperature"].diff().abs() * dt_scale)
        dt_press = (df["pressure"].diff().abs() * dt_scale)
        dt_rh = (df["relative_humidity"].diff().abs() * dt_scale)

        df["qc_temp_step_valid"] = dt_temp.fillna(0) <= self.temp_max_step_15min_c
        df["qc_press_step_valid"] = dt_press.fillna(0) <= self.pressure_max_step_15min_hpa
        df["qc_rh_step_valid"] = dt_rh.fillna(0) <= self.rh_max_step_15min_pct
        df["qc_step_valid"] = df["qc_temp_step_valid"] & df["qc_press_step_valid"] & df["qc_rh_step_valid"]

        # 3. Persistence / Stuck sensor test
        # Consecutive identical values
        def detect_stuck(series: pd.Series, threshold: int) -> pd.Series:
            diff = (series != series.shift(1)).cumsum()
            counts = series.groupby(diff).transform("size")
            return counts < threshold

        df["qc_temp_unfrozen"] = detect_stuck(df["temperature"], self.consecutive_stuck_threshold)
        df["qc_press_unfrozen"] = detect_stuck(df["pressure"], self.consecutive_stuck_threshold)
        df["qc_rh_unfrozen"] = detect_stuck(df["relative_humidity"], self.consecutive_stuck_threshold)
        df["qc_unfrozen"] = df["qc_temp_unfrozen"] & df["qc_press_unfrozen"] & df["qc_rh_unfrozen"]

        # Overall hard QC pass flag
        df["qc_passed"] = df["qc_range_valid"] & df["qc_step_valid"] & df["qc_unfrozen"]
        return df
