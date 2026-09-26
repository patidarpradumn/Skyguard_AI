"""Multivariate Mahalanobis distance calculation using robust covariance."""

import numpy as np
import pandas as pd
from scipy.spatial.distance import mahalanobis
from typing import List, Optional


class MahalanobisEngine:
    """Computes robust multivariate distances in joint (T, P, RH) observation space."""

    def __init__(self, feature_cols: List[str] = ["temperature", "pressure", "relative_humidity"]):
        self.feature_cols = feature_cols
        self.mean_vec: Optional[np.ndarray] = None
        self.inv_cov_matrix: Optional[np.ndarray] = None

    def fit(self, df: pd.DataFrame):
        """Fit empirical mean and regularized inverse covariance matrix."""
        valid_df = df[self.feature_cols].dropna()
        if len(valid_df) < 5:
            self.mean_vec = np.zeros(len(self.feature_cols))
            self.inv_cov_matrix = np.eye(len(self.feature_cols))
            return self

        self.mean_vec = valid_df.mean().values
        cov = np.cov(valid_df.values, rowvar=False)
        # Regularize covariance to avoid singularity
        cov_reg = cov + np.eye(len(self.feature_cols)) * 1e-4
        self.inv_cov_matrix = np.linalg.pinv(cov_reg)
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates Mahalanobis distance for each row."""
        df = df.copy()
        if self.mean_vec is None or self.inv_cov_matrix is None:
            self.fit(df)

        vals = df[self.feature_cols].values
        dists = np.zeros(len(df))

        for i in range(len(df)):
            row = vals[i]
            if np.any(np.isnan(row)):
                dists[i] = 10.0 # High penalty for missing/corrupt
            else:
                diff = row - self.mean_vec
                dists[i] = np.sqrt(np.dot(np.dot(diff, self.inv_cov_matrix), diff))

        df["mahalanobis_distance"] = dists
        # Chi-squared inspired normalized score [0, 1] (for 3 DoF, p=0.01 is ~11.3)
        df["multivariate_anomaly_score"] = 1.0 / (1.0 + np.exp(-0.6 * (dists - 4.5)))
        return df
