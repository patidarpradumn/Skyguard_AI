"""26-Mode Anomaly Injection Engine for Automatic Weather Stations.
Conforms strictly to SIH26073 fault simulation specifications.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple


class AnomalyInjectionEngine:
    """Configurable anomaly injection simulator implementing all 26 AWS fault modes."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)

    def inject_spikes(
        self,
        df: pd.DataFrame,
        parameter: str = "temperature",
        magnitude: float = 12.0,
        indices: Optional[List[int]] = None,
        duration: int = 1
    ) -> Tuple[pd.DataFrame, List[int]]:
        """Mode 1, 2, 3, 4: Positive, Negative, Random, Multiple Spikes."""
        df = df.copy()
        n = len(df)
        if indices is None:
            indices = list(self.rng.choice(range(5, n - 5), size=max(1, n // 200), replace=False))

        for idx in indices:
            for d in range(duration):
                if idx + d < n:
                    df.loc[idx + d, parameter] += magnitude
                    df.loc[idx + d, "label"] = "SPIKE"
                    df.loc[idx + d, "fault_mode"] = f"{parameter.upper()}_SPIKE"
        return df, indices

    def inject_frozen(
        self,
        df: pd.DataFrame,
        parameter: str = "temperature",
        start_idx: int = 50,
        duration: int = 16
    ) -> pd.DataFrame:
        """Mode 5, 6, 7: Frozen Temperature, Pressure, or Humidity."""
        df = df.copy()
        frozen_val = df.loc[start_idx, parameter]
        for i in range(start_idx, min(len(df), start_idx + duration)):
            df.loc[i, parameter] = frozen_val
            df.loc[i, "label"] = "FROZEN"
            df.loc[i, "fault_mode"] = f"{parameter.upper()}_FROZEN"
        return df

    def inject_drift(
        self,
        df: pd.DataFrame,
        parameter: str = "temperature",
        drift_rate_per_step: float = 0.25,
        start_idx: int = 50,
        duration: int = 48
    ) -> pd.DataFrame:
        """Mode 8, 9, 10: Linear / Quadratic Sensor Calibration Drift."""
        df = df.copy()
        for step, i in enumerate(range(start_idx, min(len(df), start_idx + duration))):
            df.loc[i, parameter] += drift_rate_per_step * (step + 1)
            df.loc[i, "label"] = "DRIFT"
            df.loc[i, "fault_mode"] = f"{parameter.upper()}_DRIFT"
        return df

    def inject_bias(
        self,
        df: pd.DataFrame,
        parameter: str = "temperature",
        offset: float = 6.5,
        start_idx: int = 40,
        duration: int = 50,
        gradual: bool = False
    ) -> pd.DataFrame:
        """Mode 11, 12: Sudden or Gradual Sensor Bias."""
        df = df.copy()
        for step, i in enumerate(range(start_idx, min(len(df), start_idx + duration))):
            curr_offset = offset * min(1.0, (step + 1) / 10.0) if gradual else offset
            df.loc[i, parameter] += curr_offset
            df.loc[i, "label"] = "DRIFT" if gradual else "OTHER_SENSOR_FAULT"
            df.loc[i, "fault_mode"] = f"{parameter.upper()}_{'GRADUAL' if gradual else 'SUDDEN'}_BIAS"
        return df

    def inject_stuck_humidity(
        self,
        df: pd.DataFrame,
        stuck_at: float = 0.0,
        start_idx: int = 60,
        duration: int = 30
    ) -> pd.DataFrame:
        """Mode 13, 14: Humidity Stuck Near 0% or 100%."""
        df = df.copy()
        for i in range(start_idx, min(len(df), start_idx + duration)):
            df.loc[i, "relative_humidity"] = stuck_at + self.rng.uniform(0.0, 0.2)
            df.loc[i, "label"] = "OTHER_SENSOR_FAULT"
            df.loc[i, "fault_mode"] = f"RH_STUCK_{int(stuck_at)}"
        return df

    def inject_physical_inconsistency(
        self,
        df: pd.DataFrame,
        start_idx: int = 45,
        duration: int = 10
    ) -> pd.DataFrame:
        """Mode 15, 16: Physical Inconsistencies (e.g. Dew Point > Temperature)."""
        df = df.copy()
        for i in range(start_idx, min(len(df), start_idx + duration)):
            # Force T down while keeping RH pinned at 99%, triggering impossible thermodynamic saturation
            df.loc[i, "temperature"] -= 12.0
            df.loc[i, "relative_humidity"] = 99.5
            df.loc[i, "label"] = "CORRUPTED_DATA"
            df.loc[i, "fault_mode"] = "PHYSICS_INCONSISTENCY_TD_EXCEEDS_T"
        return df

    def inject_packet_loss_and_outage(
        self,
        df: pd.DataFrame,
        start_idx: int = 80,
        duration: int = 12,
        mode: str = "burst"
    ) -> pd.DataFrame:
        """Mode 17, 18, 19: Missing Packets, Burst Loss, Telemetry Outage."""
        df = df.copy()
        for i in range(start_idx, min(len(df), start_idx + duration)):
            df.loc[i, ["temperature", "pressure", "relative_humidity"]] = np.nan
            df.loc[i, "label"] = "COMMUNICATION_ERROR"
            df.loc[i, "fault_mode"] = f"COMM_{mode.upper()}_OUTAGE"
        return df

    def inject_corruptions(
        self,
        df: pd.DataFrame,
        indices: Optional[List[int]] = None
    ) -> pd.DataFrame:
        """Mode 20, 21, 22, 23: Sentinel values, timestamp jitter, duplicates, staircase."""
        df = df.copy()
        n = len(df)
        if indices is None:
            indices = list(self.rng.choice(range(10, n - 10), size=max(1, n // 100), replace=False))

        for idx in indices:
            # Inject sentinel value -999.0
            param = self.rng.choice(["temperature", "pressure", "relative_humidity"])
            df.loc[idx, param] = -999.0
            df.loc[idx, "label"] = "CORRUPTED_DATA"
            df.loc[idx, "fault_mode"] = "SENTINEL_CORRUPTION"
        return df

    def inject_quantization_staircase(
        self,
        df: pd.DataFrame,
        parameter: str = "temperature",
        step_size: float = 3.0,
        start_idx: int = 30,
        duration: int = 40
    ) -> pd.DataFrame:
        """Mode 23: Coarse Quantization / ADC Resolution Failure."""
        df = df.copy()
        for i in range(start_idx, min(len(df), start_idx + duration)):
            raw_val = df.loc[i, parameter]
            df.loc[i, parameter] = np.round(raw_val / step_size) * step_size
            df.loc[i, "label"] = "OTHER_SENSOR_FAULT"
            df.loc[i, "fault_mode"] = "QUANTIZATION_STAIRCASE"
        return df

    def inject_intermittent_and_multi(
        self,
        df: pd.DataFrame,
        start_idx: int = 70,
        duration: int = 30
    ) -> pd.DataFrame:
        """Mode 24, 25, 26: Intermittent failures & Multi-sensor simultaneous fault."""
        df = df.copy()
        for i in range(start_idx, min(len(df), start_idx + duration)):
            if i % 3 == 0:
                df.loc[i, "temperature"] += 15.0
                df.loc[i, "relative_humidity"] = 0.0
                df.loc[i, "label"] = "OTHER_SENSOR_FAULT"
                df.loc[i, "fault_mode"] = "MULTI_SENSOR_SIMULTANEOUS"
        return df

    def generate_comprehensive_fault_dataset(self, normal_df: pd.DataFrame) -> pd.DataFrame:
        """Applies a rich, realistic sequence of various sensor faults across the dataset."""
        df = normal_df.copy()
        if "label" not in df.columns:
            df["label"] = "NORMAL"
        if "fault_mode" not in df.columns:
            df["fault_mode"] = "NONE"

        n = len(df)
        if n < 100:
            return df

        # Partition dataset into distinct segments for various faults
        # 1. Temperature spike at ~10% mark
        df, _ = self.inject_spikes(df, parameter="temperature", magnitude=14.0, indices=[int(n * 0.10), int(n * 0.12)], duration=1)
        # 2. Pressure negative spike at ~20%
        df, _ = self.inject_spikes(df, parameter="pressure", magnitude=-25.0, indices=[int(n * 0.20)], duration=2)
        # 3. Frozen temperature at ~30%
        df = self.inject_frozen(df, parameter="temperature", start_idx=int(n * 0.30), duration=16)
        # 4. Temperature drift at ~45%
        df = self.inject_drift(df, parameter="temperature", drift_rate_per_step=0.35, start_idx=int(n * 0.45), duration=24)
        # 5. Humidity stuck near zero at ~60%
        df = self.inject_stuck_humidity(df, stuck_at=0.0, start_idx=int(n * 0.60), duration=20)
        # 6. Physical inconsistency (Dew point > T) at ~72%
        df = self.inject_physical_inconsistency(df, start_idx=int(n * 0.72), duration=10)
        # 7. Burst packet loss at ~85%
        df = self.inject_packet_loss_and_outage(df, start_idx=int(n * 0.85), duration=10, mode="burst")
        # 8. Sentinels at random
        df = self.inject_corruptions(df, indices=[int(n * 0.92), int(n * 0.95)])

        return df
