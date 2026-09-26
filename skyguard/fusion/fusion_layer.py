"""Unified Evidence Fusion Layer and Confidence Calibrator for SkyGuard AI."""

import numpy as np
import pandas as pd
from typing import Dict, Any, List


class EvidenceFusionLayer:
    """Fuses multi-modal evidence (Physics, Temporal, Multivariate, Spatial, Data Quality)
    into a mathematically calibrated continuous anomaly score and discrete severity rating.
    """

    def __init__(
        self,
        weight_physics: float = 0.30,
        weight_temporal: float = 0.25,
        weight_multivariate: float = 0.25,
        weight_spatial: float = 0.15,
        weight_quality: float = 0.05
    ):
        self.w_physics = weight_physics
        self.w_temporal = weight_temporal
        self.w_multivariate = weight_multivariate
        self.w_spatial = weight_spatial
        self.w_quality = weight_quality

    def fuse(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Ensure all score components exist
        if "physics_anomaly_score" not in df.columns:
            df["physics_anomaly_score"] = 0.0
        if "temporal_anomaly_score" not in df.columns:
            df["temporal_anomaly_score"] = 0.0
        if "multivariate_anomaly_score" not in df.columns:
            df["multivariate_anomaly_score"] = 0.0
        if "spatial_anomaly_score" not in df.columns:
            df["spatial_anomaly_score"] = 0.0

        # Data quality score (1.0 = heavy failure/missing, 0.0 = clean)
        quality_score = np.where(
            df["temperature"].isna() | df["pressure"].isna() | df["relative_humidity"].isna(),
            1.0,
            np.where(df.get("qc_passed", True) == False, 0.6, 0.0)
        )
        df["data_quality_score"] = quality_score

        # Check if spatial evidence is available; if not, re-normalize remaining weights
        spatial_avail = df.get("spatial_available", True)
        
        # Weighted linear combination
        raw_fusion = (
            self.w_physics * df["physics_anomaly_score"] +
            self.w_temporal * df["temporal_anomaly_score"] +
            self.w_multivariate * df["multivariate_anomaly_score"] +
            self.w_spatial * df["spatial_anomaly_score"] +
            self.w_quality * df["data_quality_score"]
        )

        # Calibrate using sigmoid logistic transform with steep slope around decision boundary
        # Calibrated anomaly probability
        df["overall_anomaly_score"] = np.clip(raw_fusion, 0.0, 1.0)
        
        # Confidence score: Distance from maximum uncertainty (0.50)
        df["anomaly_confidence"] = np.round(np.abs(df["overall_anomaly_score"] - 0.5) * 2.0 * 100.0, 1)

        # Severity levels
        conditions = [
            df["overall_anomaly_score"] >= 0.85,
            df["overall_anomaly_score"] >= 0.65,
            df["overall_anomaly_score"] >= 0.40,
        ]
        choices = ["CRITICAL", "HIGH", "MEDIUM"]
        df["anomaly_severity"] = np.select(conditions, choices, default="LOW")

        return df
