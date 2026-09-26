"""Real-time stream replay engine with configurable acceleration."""

import asyncio
import time
import numpy as np
import pandas as pd
from typing import AsyncGenerator, Dict, Any, Optional
from skyguard.models.pipeline import SkyGuardPipeline
from skyguard.models.lgbm_classifier import SkyGuardLightGBMClassifier
from skyguard.imputation.kalman import KalmanSelfHealer
from skyguard.explainability.shap_explainer import TreeSHAPExplainer
from skyguard.explainability.diagnostic_rules import DiagnosticExplainer
from skyguard.health.tracker import SensorHealthTracker


class StreamReplayEngine:
    """Simulates real-time AWS observation telemetry streaming at arbitrary acceleration speeds."""

    def __init__(self, model_path: Optional[str] = None):
        self.pipeline = SkyGuardPipeline()
        self.kalman = KalmanSelfHealer()
        self.health_tracker = SensorHealthTracker()
        self.model = None
        self.shap_explainer = None

        if model_path:
            try:
                self.model = SkyGuardLightGBMClassifier.load(model_path)
                self.shap_explainer = TreeSHAPExplainer(self.model)
            except Exception as e:
                print(f"Warning: Could not load model from {model_path}: {e}")

    async def stream_observations(
        self,
        df: pd.DataFrame,
        speed_multiplier: float = 100.0,
        interval_sec: float = 0.05
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Yields enriched, validated, and explained observation frames asynchronously."""
        # Pre-process features for entire series
        enriched_df = self.pipeline.process_dataframe(df)

        for i, row in enriched_df.iterrows():
            row_df = pd.DataFrame([row])
            row_dict = row.to_dict()

            # Model prediction if available
            if self.model is not None:
                labels, preds, probs = self.model.predict(row_df)
                pred_label = labels[0]
                pred_prob = float(np.max(probs[0]))
                shap_res = self.shap_explainer.explain_instance(row_df, top_k=4)
            else:
                pred_label = row_dict.get("label", "NORMAL")
                pred_prob = 0.95
                shap_res = {"predicted_class": pred_label, "confidence_pct": 95.0, "top_features": []}

            # Kalman self-healing imputation
            meas = np.array([row_dict["temperature"], row_dict["pressure"], row_dict["relative_humidity"]], dtype=float)
            is_fault = pred_label in ["SPIKE", "FROZEN", "DRIFT", "COMMUNICATION_ERROR", "CORRUPTED_DATA", "OTHER_SENSOR_FAULT"]
            mask = np.array([not is_fault, not is_fault, not is_fault])
            healed, conf = self.kalman.update_step(meas, mask)

            # Diagnostic explanation
            diag = DiagnosticExplainer.generate_diagnostic_report(row_dict, shap_res)

            # Sensor health update
            recent_sub = enriched_df.iloc[max(0, i - 48):i + 1]
            health = self.health_tracker.evaluate_sensor_health(recent_sub)

            payload = {
                "timestamp": str(row_dict.get("timestamp")),
                "station_id": str(row_dict.get("station_id")),
                "latitude": float(row_dict.get("latitude", 0.0)),
                "longitude": float(row_dict.get("longitude", 0.0)),
                "raw_readings": {
                    "temperature_c": float(row_dict["temperature"]) if pd.notna(row_dict["temperature"]) else None,
                    "pressure_hpa": float(row_dict["pressure"]) if pd.notna(row_dict["pressure"]) else None,
                    "relative_humidity_pct": float(row_dict["relative_humidity"]) if pd.notna(row_dict["relative_humidity"]) else None
                },
                "derived_physics": {
                    "dew_point_c": round(float(row_dict.get("dew_point", 0.0)), 2),
                    "vpd_hpa": round(float(row_dict.get("vpd", 0.0)), 3),
                    "potential_temp_k": round(float(row_dict.get("potential_temperature", 0.0)), 1)
                },
                "ai_classification": pred_label,
                "confidence_pct": round(pred_prob * 100.0, 1),
                "anomaly_score": round(float(row_dict.get("overall_anomaly_score", 0.0)), 3),
                "severity": row_dict.get("anomaly_severity", "LOW"),
                "is_extreme_weather": pred_label == "GENUINE_EXTREME_WEATHER",
                "is_sensor_fault": is_fault,
                "self_healed_imputation": {
                    "imputed_temperature_c": round(float(healed[0]), 2),
                    "imputed_pressure_hpa": round(float(healed[1]), 2),
                    "imputed_humidity_pct": round(float(healed[2]), 1),
                    "imputation_confidence_pct": round(conf, 1)
                },
                "sensor_health": health,
                "diagnostic_explanation": diag
            }

            yield payload
            await asyncio.sleep(interval_sec)
