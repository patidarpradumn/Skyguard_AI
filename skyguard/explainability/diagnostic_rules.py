"""Diagnostic Explanation Generator combining Physics Invariants and TreeSHAP."""

from typing import Dict, Any, List
import pandas as pd


class DiagnosticExplainer:
    """Produces authoritative, meteorologically grounded and human-readable diagnostic explanations."""

    @classmethod
    def generate_diagnostic_report(
        cls,
        row_dict: Dict[str, Any],
        shap_explanation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesizes physical laws, neighborhood checks, and ML attributions into a structured alert."""
        pred_class = shap_explanation.get("predicted_class", "NORMAL")
        confidence = shap_explanation.get("confidence_pct", 0.0)

        temp = row_dict.get("temperature", 0.0)
        press = row_dict.get("pressure", 0.0)
        rh = row_dict.get("relative_humidity", 0.0)
        td = row_dict.get("dew_point", 0.0)
        vpd = row_dict.get("vpd", 0.0)
        d_temp = row_dict.get("d_temp_dt", 0.0)
        d_press = row_dict.get("d_press_dt", 0.0)
        d_rh = row_dict.get("d_rh_dt", 0.0)
        sp_dev_t = row_dict.get("neighbor_temp_dev", 0.0)

        evidence_statements = []

        # 1. Physics Evidence
        if td > temp + 0.05:
            evidence_statements.append(f"Physical invariant violation: Dew point ({td:.1f}°C) exceeds ambient temperature ({temp:.1f}°C).")
        elif row_dict.get("physics_td_violation", False):
            evidence_statements.append("Psychrometric calculation indicates supersaturation anomaly.")

        if vpd < 0:
            evidence_statements.append(f"Thermodynamic violation: Negative vapor pressure deficit ({vpd:.2f} hPa).")

        # 2. Temporal & Gradient Evidence
        if abs(d_temp) > 5.0:
            evidence_statements.append(f"Abrupt thermal rate of change ({d_temp:+.1f}°C / 15-min).")
        if abs(d_press) > 3.5:
            evidence_statements.append(f"Significant barometric rate of change ({d_press:+.1f} hPa / 15-min).")
        if abs(d_rh) > 25.0:
            evidence_statements.append(f"Rapid humidity transition ({d_rh:+.1f}% / 15-min).")

        # 3. Spatial Neighborhood Evidence
        if sp_dev_t > 4.0:
            evidence_statements.append(f"Spatial discrepancy: Station temperature deviates by {sp_dev_t:.1f}°C from regional AWS median.")
        else:
            evidence_statements.append("Surrounding regional AWS stations show consistent baseline behavior.")

        # 4. Action Recommendation
        if pred_class == "NORMAL":
            action = "Observation is validated. Accept into operational pipeline."
            headline = "Verified Atmospheric Normal"
        elif pred_class == "GENUINE_EXTREME_WEATHER":
            action = "CRITICAL METEOROLOGICAL ALERT: Accept raw observation into synoptic record. Do not censor or impute. Notify forecast desk of severe weather."
            headline = "Genuine Extreme Atmospheric Event Detected"
        elif pred_class == "SPIKE":
            action = "Reject raw transient spike. Apply Kalman self-healing filter. Log spike event to sensor health log."
            headline = "Transient Hardware Sensor Spike"
        elif pred_class == "FROZEN":
            action = "Flag sensor as FROZEN/STUCK. Activate state-space Kalman prediction. Dispatch maintenance ticket if condition persists > 3 hours."
            headline = "Sensor Telemetry Frozen / ADC Stuck"
        elif pred_class == "DRIFT":
            action = "Sensor calibration drift detected. Apply continuous bias correction. Schedule on-site recalibration."
            headline = "Progressive Sensor Calibration Drift"
        elif pred_class == "COMMUNICATION_ERROR":
            action = "Packet loss / telemetry failure. Forward Kalman state estimate to maintain continuous time-series."
            headline = "Telemetry / Communication Link Failure"
        else:
            action = "Flag observation as suspect. Impute corrected value and monitor station telemetry."
            headline = "Corrupted or Faulty Observation"

        if not evidence_statements:
            evidence_statements.append("All physical parameters and temporal derivatives within nominal bounds.")

        return {
            "headline": headline,
            "classification": pred_class,
            "confidence_pct": confidence,
            "severity": row_dict.get("anomaly_severity", "LOW"),
            "physical_evidence": evidence_statements,
            "ml_feature_attribution": shap_explanation.get("top_features", []),
            "recommended_action": action,
            "provenance": row_dict.get("source", "IMD_AWS"),
            "station_id": row_dict.get("station_id", "AWS_UNKNOWN")
        }
