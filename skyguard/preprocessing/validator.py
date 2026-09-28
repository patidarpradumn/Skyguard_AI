"""Complete Data Preprocessing and Validation Pipeline for SkyGuard AI."""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from skyguard.preprocessing.normalizer import MeteorologicalNormalizer
from skyguard.preprocessing.quality import QualityControlEngine


class DataValidationPipeline:
    """Orchestrates standard unit normalization, gap filling, and deterministic QC checks."""

    def __init__(self):
        self.normalizer = MeteorologicalNormalizer()
        self.qc = QualityControlEngine()

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """Executes full preprocessing pipeline on incoming observations."""
        # 1. Standardize units & clean sentinels
        df = self.normalizer.standardize_units(df)
        if "timestamp" in df.columns and not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        # 2. Sort by station and timestamp
        df = df.sort_values(by=["station_id", "timestamp"]).reset_index(drop=True)

        # 3. Apply Quality Control filters per station
        processed_dfs = []
        for station_id, group in df.groupby("station_id"):
            group_qc = self.qc.check_series_quality(group)
            processed_dfs.append(group_qc)

        out_df = pd.concat(processed_dfs, ignore_index=True)
        return out_df

    def get_summary_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates data quality summary metrics."""
        total_records = len(df)
        if total_records == 0:
            return {"total": 0, "pass_rate": 0.0}

        qc_passed = int(df["qc_passed"].sum()) if "qc_passed" in df.columns else total_records
        missing_temp = int(df["temperature"].isna().sum())
        missing_press = int(df["pressure"].isna().sum())
        missing_rh = int(df["relative_humidity"].isna().sum())

        return {
            "total_records": total_records,
            "qc_passed_count": qc_passed,
            "qc_pass_rate_pct": round(100.0 * qc_passed / total_records, 2),
            "missing_temp_count": missing_temp,
            "missing_press_count": missing_press,
            "missing_rh_count": missing_rh,
            "stations_count": df["station_id"].nunique() if "station_id" in df.columns else 1
        }
