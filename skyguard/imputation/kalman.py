"""State-space Kalman Filter for real-time sensor self-healing and imputation.
Citation: Kalman, R. E. (1960).
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional


class KalmanSelfHealer:
    """1D and 3D Joint State-Space Recursive Bayesian Filter for Automatic Weather Stations.
    
    CRITICAL CONSTRAINT: Never overwrites raw telemetry. Stores raw, validated, and imputed states separately.
    """

    def __init__(
        self,
        process_variance_temp: float = 0.04,
        process_variance_press: float = 0.02,
        process_variance_rh: float = 0.15,
        measurement_variance_temp: float = 0.25,
        measurement_variance_press: float = 0.10,
        measurement_variance_rh: float = 1.20
    ):
        self.q = np.array([process_variance_temp, process_variance_press, process_variance_rh])
        self.r = np.array([measurement_variance_temp, measurement_variance_press, measurement_variance_rh])

        # State vector x = [T, P, RH]
        self.state: Optional[np.ndarray] = None
        # State covariance P = diag([var_T, var_P, var_RH])
        self.p_cov: Optional[np.ndarray] = None

    def initialize(self, init_temp: float = 25.0, init_press: float = 1013.25, init_rh: float = 50.0):
        self.state = np.array([init_temp, init_press, init_rh], dtype=float)
        self.p_cov = np.diag([1.0, 0.5, 5.0])

    def predict_step(self, dt_minutes: float = 15.0) -> Tuple[np.ndarray, np.ndarray]:
        """Time update (Predict): x_k|k-1 = F * x_k-1, P_k|k-1 = F * P_k-1 * F^T + Q"""
        if self.state is None:
            self.initialize()

        # Random walk with drift assumption (F = Identity)
        # Process noise scales with time interval
        dt_scale = dt_minutes / 15.0
        p_predicted = self.p_cov + np.diag(self.q * dt_scale)
        return self.state.copy(), p_predicted

    def update_step(
        self,
        raw_measurement: np.ndarray,
        is_valid_mask: np.ndarray,
        dt_minutes: float = 15.0
    ) -> Tuple[np.ndarray, float]:
        """Measurement update (Correct).
        If a sensor reading is invalid/faulty, skip measurement update for that sensor (pure Kalman propagation).
        """
        if self.state is None:
            self.initialize(
                init_temp=raw_measurement[0] if is_valid_mask[0] else 25.0,
                init_press=raw_measurement[1] if is_valid_mask[1] else 1013.25,
                init_rh=raw_measurement[2] if is_valid_mask[2] else 50.0
            )

        state_pred, p_pred = self.predict_step(dt_minutes)

        imputed_state = state_pred.copy()
        new_state = state_pred.copy()
        new_p = p_pred.copy()

        # Update each dimension independently where valid
        for i in range(3):
            if is_valid_mask[i] and not np.isnan(raw_measurement[i]):
                # Innovation / measurement residual
                y = raw_measurement[i] - state_pred[i]
                # Innovation covariance
                s = p_pred[i, i] + self.r[i]
                # Kalman gain
                k = p_pred[i, i] / s
                # Updated state
                new_state[i] = state_pred[i] + k * y
                new_p[i, i] = (1.0 - k) * p_pred[i, i]
            else:
                # Sensor is faulty: keep predicted state as the self-healed estimate!
                new_state[i] = state_pred[i]
                new_p[i, i] = p_pred[i, i] # Covariance grows slightly to reflect uncertainty

        self.state = new_state
        self.p_cov = new_p

        # Imputation confidence: derived from diagonal trace of state covariance
        trace_var = float(np.sum(np.diag(new_p)))
        confidence_pct = max(10.0, min(99.0, 100.0 / (1.0 + 0.2 * trace_var)))

        return new_state, confidence_pct

    def process_series(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processes entire time-series and attaches imputed columns."""
        df = df.copy()
        self.initialize()

        imputed_temps, imputed_pressures, imputed_rhs = [], [], []
        impute_flags = []
        confidences = []

        for _, row in df.iterrows():
            meas = np.array([row["temperature"], row["pressure"], row["relative_humidity"]], dtype=float)
            label = row.get("label", "NORMAL")

            # Check if observation is accepted or considered a hardware fault
            is_fault = label in ["SPIKE", "FROZEN", "DRIFT", "COMMUNICATION_ERROR", "CORRUPTED_DATA", "OTHER_SENSOR_FAULT"]
            is_valid = ~is_fault if not np.any(np.isnan(meas)) else False

            # Mask per dimension
            mask = np.array([is_valid and not np.isnan(meas[0]), is_valid and not np.isnan(meas[1]), is_valid and not np.isnan(meas[2])])

            healed_state, conf = self.update_step(meas, mask)

            imputed_temps.append(round(float(healed_state[0]), 2))
            imputed_pressures.append(round(float(healed_state[1]), 2))
            imputed_rhs.append(round(float(np.clip(healed_state[2], 0.0, 100.0)), 1))
            impute_flags.append(is_fault or np.any(np.isnan(meas)))
            confidences.append(round(conf, 1))

        # Store separated columns strictly preserving raw inputs
        df["raw_temperature"] = df["temperature"]
        df["raw_pressure"] = df["pressure"]
        df["raw_relative_humidity"] = df["relative_humidity"]

        df["imputed_temperature"] = imputed_temps
        df["imputed_pressure"] = imputed_pressures
        df["imputed_relative_humidity"] = imputed_rhs

        # Validated stream (uses raw if normal or genuine extreme, uses imputed if fault)
        df["validated_temperature"] = np.where(df["imputed_temperature"].notna() & np.array(impute_flags), df["imputed_temperature"], df["temperature"])
        df["validated_pressure"] = np.where(df["imputed_pressure"].notna() & np.array(impute_flags), df["imputed_pressure"], df["pressure"])
        df["validated_relative_humidity"] = np.where(df["imputed_relative_humidity"].notna() & np.array(impute_flags), df["imputed_relative_humidity"], df["relative_humidity"])

        df["is_imputed"] = impute_flags
        df["imputation_confidence"] = confidences

        return df
