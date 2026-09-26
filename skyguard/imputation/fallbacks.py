"""Baseline imputation algorithms for comparative evaluation."""

import numpy as np
import pandas as pd
from typing import Dict, Any


class BaselineImputers:
    """Provides standard benchmark imputation methods: Linear, Forward Fill, Spline."""

    @staticmethod
    def forward_fill(df: pd.DataFrame, value_cols: list = ["temperature", "pressure", "relative_humidity"]) -> pd.DataFrame:
        df = df.copy()
        df[value_cols] = df[value_cols].ffill().bfill()
        return df

    @staticmethod
    def linear_interpolation(df: pd.DataFrame, value_cols: list = ["temperature", "pressure", "relative_humidity"]) -> pd.DataFrame:
        df = df.copy()
        df[value_cols] = df[value_cols].interpolate(method="linear").ffill().bfill()
        return df

    @staticmethod
    def evaluate_imputation_error(true_df: pd.DataFrame, imputed_df: pd.DataFrame, mask: pd.Series) -> Dict[str, float]:
        """Calculates MAE and RMSE strictly on the corrupted/imputed points."""
        metrics = {}
        for col in ["temperature", "pressure", "relative_humidity"]:
            if mask.sum() == 0:
                metrics[f"{col}_mae"] = 0.0
                metrics[f"{col}_rmse"] = 0.0
                continue
            y_true = true_df.loc[mask, col].values
            y_pred = imputed_df.loc[mask, f"imputed_{col}" if f"imputed_{col}" in imputed_df.columns else col].values

            # Filter NaNs
            valid = ~np.isnan(y_true) & ~np.isnan(y_pred)
            if np.sum(valid) == 0:
                metrics[f"{col}_mae"] = 0.0
                metrics[f"{col}_rmse"] = 0.0
            else:
                mae = float(np.mean(np.abs(y_true[valid] - y_pred[valid])))
                rmse = float(np.sqrt(np.mean((y_true[valid] - y_pred[valid]) ** 2)))
                metrics[f"{col}_mae"] = round(mae, 3)
                metrics[f"{col}_rmse"] = round(rmse, 3)
        return metrics
