"""Physically coherent genuine extreme atmospheric event generator.
Ensures SkyGuard AI learns to distinguish true meteorology from hardware faults.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple


class ExtremeWeatherSimulator:
    """Simulates authentic physical extreme weather events that strictly preserve atmospheric coherence."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)

    def inject_heatwave(
        self,
        df: pd.DataFrame,
        start_idx: int = 50,
        duration_samples: int = 96, # 24 hours
        peak_temp_anomaly_c: float = 9.5
    ) -> pd.DataFrame:
        """Simulates an Indian summer severe heatwave (e.g. Loo event in Rajasthan/NCR).
        
        Thermodynamic Coherence:
        - Temperature rises significantly (+8 to +10°C).
        - Relative Humidity drops significantly (-25% to -35%, psychrometric response).
        - Thermal surface low causes slight barometric dip (-2 to -4 hPa).
        - Dew point remains stable or slightly increases (valid physical constraint Td <= T).
        """
        df = df.copy()
        n = len(df)
        end_idx = min(n, start_idx + duration_samples)

        # Smooth bell curve for multi-hour heatwave progression
        t_steps = np.linspace(0, np.pi, end_idx - start_idx)
        envelope = np.sin(t_steps)

        for step, i in enumerate(range(start_idx, end_idx)):
            temp_boost = peak_temp_anomaly_c * envelope[step]
            df.loc[i, "temperature"] += temp_boost
            # RH drops proportionally to maintain physical vapor pressure consistency
            df.loc[i, "relative_humidity"] = np.clip(df.loc[i, "relative_humidity"] - (temp_boost * 2.8), 8.0, 95.0)
            # Thermal low pressure drop
            df.loc[i, "pressure"] -= (temp_boost * 0.35)
            df.loc[i, "label"] = "GENUINE_EXTREME_WEATHER"
            df.loc[i, "fault_mode"] = "EXTREME_HEATWAVE"

        return df

    def inject_severe_squall(
        self,
        df: pd.DataFrame,
        start_idx: int = 60,
        duration_samples: int = 16 # 4 hours
    ) -> pd.DataFrame:
        """Simulates a severe convective squall line / thunderstorm outflow (e.g. Kalbaishakhi / Nor'wester).
        
        Thermodynamic Coherence:
        - Rapid temperature plunge due to evaporative cold pool (-7°C to -10°C in 15-30 min).
        - Sudden RH surge to near saturation (85% - 98%).
        - Thunderstorm 'pressure nose' (brief 2-4 hPa surge due to cold air dome, then stabilization).
        """
        df = df.copy()
        n = len(df)
        end_idx = min(n, start_idx + duration_samples)

        for step, i in enumerate(range(start_idx, end_idx)):
            # Fast drop then gradual recovery
            decay = np.exp(-step / 6.0)
            df.loc[i, "temperature"] -= (8.5 * decay)
            df.loc[i, "relative_humidity"] = np.clip(df.loc[i, "relative_humidity"] + (35.0 * decay), 20.0, 98.0)
            # Pressure nose: rise during first 3 steps, then recovery
            p_nose = 2.5 * np.exp(-((step - 1) ** 2) / 4.0)
            df.loc[i, "pressure"] += p_nose
            df.loc[i, "label"] = "GENUINE_EXTREME_WEATHER"
            df.loc[i, "fault_mode"] = "EXTREME_SQUALL_COLD_POOL"

        return df

    def inject_cyclonic_depression(
        self,
        df: pd.DataFrame,
        start_idx: int = 40,
        duration_samples: int = 120, # 30 hours
        central_pressure_drop_hpa: float = 18.0
    ) -> pd.DataFrame:
        """Simulates a deep cyclonic depression (e.g. Bay of Bengal / Arabian Sea coastal landfall).
        
        Thermodynamic Coherence:
        - Major sustained atmospheric pressure drop (-15 to -25 hPa).
        - High persistent humidity (85-98%).
        - Moderate temperature suppression due to dense cloud overcast and rain.
        """
        df = df.copy()
        n = len(df)
        end_idx = min(n, start_idx + duration_samples)

        t_steps = np.linspace(0, np.pi, end_idx - start_idx)
        envelope = np.sin(t_steps)

        for step, i in enumerate(range(start_idx, end_idx)):
            p_drop = central_pressure_drop_hpa * envelope[step]
            df.loc[i, "pressure"] -= p_drop
            df.loc[i, "relative_humidity"] = np.clip(df.loc[i, "relative_humidity"] + (18.0 * envelope[step]), 30.0, 99.0)
            df.loc[i, "temperature"] -= (3.0 * envelope[step]) # Cloud suppression
            df.loc[i, "label"] = "GENUINE_EXTREME_WEATHER"
            df.loc[i, "fault_mode"] = "EXTREME_CYCLONIC_LOW"

        return df
