"""Physics Feature Engineering Engine for SkyGuard AI."""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from skyguard.physics.thermodynamics import AtmosphericThermodynamics
from skyguard.physics.invariants import PhysicsInvariantChecker


class PhysicsFeatureEngine:
    """Computes all deterministic thermodynamic features and consistency scores."""

    def __init__(self):
        self.thermo = AtmosphericThermodynamics()
        self.invariant_checker = PhysicsInvariantChecker()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transforms a DataFrame containing temperature, pressure, relative_humidity into enriched physics features."""
        df = df.copy()

        # 1. Fundamental Thermodynamic Features
        df["dew_point"] = self.thermo.dew_point(df["temperature"], df["relative_humidity"])
        df["dew_point_depression"] = df["temperature"] - df["dew_point"]
        df["saturation_vapor_pressure"] = self.thermo.saturation_vapor_pressure(df["temperature"])
        df["actual_vapor_pressure"] = self.thermo.actual_vapor_pressure(df["temperature"], df["relative_humidity"])
        df["vpd"] = self.thermo.vapor_pressure_deficit(df["temperature"], df["relative_humidity"])
        df["potential_temperature"] = self.thermo.potential_temperature(df["temperature"], df["pressure"])
        df["virtual_temperature"] = self.thermo.virtual_temperature(df["temperature"], df["pressure"], df["relative_humidity"])

        # 2. Physics Invariant Flags & Scores
        # Dew point excess (Td - T) -> should be <= 0
        td_excess = np.maximum(0.0, df["dew_point"] - df["temperature"])
        df["physics_td_violation"] = td_excess > 0.05
        df["physics_vpd_violation"] = df["vpd"] < 0.0

        # Continuous physics anomaly score [0, 1]
        df["physics_anomaly_score"] = np.clip(
            (td_excess / 3.0) + (np.where(df["vpd"] < 0.0, 0.5, 0.0)) + (np.where((df["potential_temperature"] < 220.0) | (df["potential_temperature"] > 420.0), 0.7, 0.0)),
            0.0, 1.0
        )

        # 3. Dynamic Rates of Change per Station
        if "station_id" in df.columns:
            rate_dfs = []
            for _, group in df.groupby("station_id"):
                group = group.copy()
                group["d_temp_dt"] = group["temperature"].diff().fillna(0.0)
                group["d_press_dt"] = group["pressure"].diff().fillna(0.0)
                group["d_rh_dt"] = group["relative_humidity"].diff().fillna(0.0)
                group["d_vpd_dt"] = group["vpd"].diff().fillna(0.0)

                # Thermodynamic Coherence Score:
                # In normal daytime solar heating or squall, T and RH change in opposite directions.
                # If T jumps up +5°C and RH jumps up +30% simultaneously without pressure drop, thermodynamic coherence is low.
                # d_temp * d_rh normally <= 0. If > 0 with large magnitude, flag as potential sensor artifact.
                t_rh_product = group["d_temp_dt"] * group["d_rh_dt"]
                group["thermo_incoherence_score"] = np.clip(np.where(t_rh_product > 20.0, t_rh_product / 100.0, 0.0), 0.0, 1.0)
                rate_dfs.append(group)

            df = pd.concat(rate_dfs, ignore_index=True)
        else:
            df["d_temp_dt"] = df["temperature"].diff().fillna(0.0)
            df["d_press_dt"] = df["pressure"].diff().fillna(0.0)
            df["d_rh_dt"] = df["relative_humidity"].diff().fillna(0.0)
            df["d_vpd_dt"] = df["vpd"].diff().fillna(0.0)
            t_rh_product = df["d_temp_dt"] * df["d_rh_dt"]
            df["thermo_incoherence_score"] = np.clip(np.where(t_rh_product > 20.0, t_rh_product / 100.0, 0.0), 0.0, 1.0)

        return df
