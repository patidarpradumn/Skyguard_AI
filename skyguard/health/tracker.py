"""Persistent Sensor Health and Degradation Tracking Engine."""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime


class SensorHealthTracker:
    """Calculates continuous 0-100 sensor health metrics per individual transducer."""

    def __init__(self, memory_window_samples: int = 96): # Past 24 hours of 15-min data
        self.window = memory_window_samples

    def evaluate_sensor_health(self, station_history_df: pd.DataFrame) -> Dict[str, Any]:
        """Evaluates health states for Temperature, Pressure, and Humidity sensors."""
        recent = station_history_df.tail(self.window)
        n = max(1, len(recent))

        # 1. Fault frequencies
        labels = recent.get("label", pd.Series(["NORMAL"] * n))
        spike_count = int(labels.str.contains("SPIKE", na=False).sum())
        frozen_count = int(labels.str.contains("FROZEN", na=False).sum())
        drift_count = int(labels.str.contains("DRIFT", na=False).sum())
        comm_count = int(labels.str.contains("COMMUNICATION", na=False).sum())
        corrupt_count = int(labels.str.contains("CORRUPTED", na=False).sum())
        physics_violations = int(recent.get("physics_td_violation", pd.Series([False] * n)).sum())

        # 2. Parameter specific health scores (100 is pristine)
        # Temperature Health
        t_penalty = (spike_count * 5.0) + (frozen_count * 4.0) + (drift_count * 6.0) + (physics_violations * 4.0)
        t_health = max(0.0, min(100.0, 100.0 - (t_penalty * (96.0 / n))))

        # Pressure Health
        p_penalty = (spike_count * 3.0) + (frozen_count * 5.0) + (drift_count * 5.0) + (corrupt_count * 8.0)
        p_health = max(0.0, min(100.0, 100.0 - (p_penalty * (96.0 / n))))

        # Humidity Health
        rh_penalty = (spike_count * 4.0) + (frozen_count * 6.0) + (drift_count * 4.0) + (physics_violations * 6.0)
        rh_health = max(0.0, min(100.0, 100.0 - (rh_penalty * (96.0 / n))))

        # Composite Station Health
        overall_health = round((t_health * 0.35 + p_health * 0.35 + rh_health * 0.30), 1)

        # Categorize health state
        if overall_health >= 80.0:
            state = "HEALTHY"
            risk = "LOW"
            action = "Sensor network operating within optimal specifications."
        elif overall_health >= 60.0:
            state = "WATCH"
            risk = "MODERATE"
            action = "Intermittent anomalies detected. Place station on automated watch."
        elif overall_health >= 40.0:
            state = "DEGRADED"
            risk = "ELEVATED"
            action = "Repeated telemetry/sensor faults. Schedule on-site recalibration."
        else:
            state = "CRITICAL"
            risk = "URGENT"
            action = "Severe sensor breakdown or stuck transducer. Dispatch emergency technician."

        return {
            "overall_health_score": overall_health,
            "health_state": state,
            "maintenance_risk": risk,
            "recommended_action": action,
            "sensor_details": {
                "temperature_health": round(t_health, 1),
                "pressure_health": round(p_health, 1),
                "humidity_health": round(rh_health, 1)
            },
            "fault_telemetry_24h": {
                "spikes": spike_count,
                "frozen_intervals": frozen_count,
                "drift_events": drift_count,
                "communication_drops": comm_count,
                "physics_violations": physics_violations
            }
        }
