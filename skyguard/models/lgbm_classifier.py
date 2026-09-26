"""Supervised Multi-Class LightGBM Anomaly and Fault Classifier for SkyGuard AI."""

import numpy as np
import pandas as pd
import lightgbm as lgb
from typing import Dict, Any, List, Optional, Tuple, Union
import joblib
from pathlib import Path


CLASS_MAP = {
    0: "NORMAL",
    1: "GENUINE_EXTREME_WEATHER",
    2: "SPIKE",
    3: "FROZEN",
    4: "DRIFT",
    5: "COMMUNICATION_ERROR",
    6: "CORRUPTED_DATA",
    7: "OTHER_SENSOR_FAULT"
}
REVERSE_CLASS_MAP = {v: k for k, v in CLASS_MAP.items()}

FEATURE_COLUMNS = [
    # 1. Raw Core Sensors
    "temperature", "pressure", "relative_humidity",
    # 2. Physics & Thermodynamics
    "dew_point", "dew_point_depression", "vpd", "potential_temperature", "virtual_temperature",
    "d_temp_dt", "d_press_dt", "d_rh_dt", "d_vpd_dt", "thermo_incoherence_score", "physics_anomaly_score",
    # 3. Temporal & Diurnal
    "hour_sin", "hour_cos", "month_sin", "month_cos",
    "temperature_diurnal_dev", "relative_humidity_diurnal_dev",
    "temperature_zscore_12", "pressure_zscore_12", "relative_humidity_zscore_12",
    "temperature_roll_range_12", "pressure_roll_range_12", "relative_humidity_roll_range_12",
    "temporal_anomaly_score",
    # 4. Multivariate
    "mahalanobis_distance", "corr_temp_rh_16", "isolated_temp_fraction", "isolated_press_fraction", "isolated_rh_fraction",
    "multivariate_anomaly_score",
    # 5. Spatial
    "neighbor_temp_dev", "neighbor_press_dev", "neighbor_rh_dev", "spatial_anomaly_score"
]


class SkyGuardLightGBMClassifier:
    """Production Multi-Class Fault Classification Engine using LightGBM."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model: Optional[lgb.LGBMClassifier] = None
        self.feature_names = FEATURE_COLUMNS

    def fit(self, X: pd.DataFrame, y: pd.Series, val_data: Optional[Tuple[pd.DataFrame, pd.Series]] = None):
        """Train LightGBM multi-class model with strict regularization."""
        # Ensure all features exist with fallback 0.0
        X_mat = X.reindex(columns=self.feature_names, fill_value=0.0).fillna(0.0)

        # Map string labels to integer classes reliably
        if pd.api.types.is_numeric_dtype(y):
            y_int = y.astype(int)
        else:
            y_int = y.astype(str).map(REVERSE_CLASS_MAP).fillna(7).astype(int)

        eval_set = None
        if val_data is not None:
            val_X, val_y = val_data
            val_X_mat = val_X.reindex(columns=self.feature_names, fill_value=0.0).fillna(0.0)
            if pd.api.types.is_numeric_dtype(val_y):
                val_y_int = val_y.astype(int)
            else:
                val_y_int = val_y.astype(str).map(REVERSE_CLASS_MAP).fillna(7).astype(int)
            eval_set = [(val_X_mat, val_y_int)]

        self.model = lgb.LGBMClassifier(
            objective="multiclass",
            num_class=8,
            n_estimators=250,
            learning_rate=0.05,
            num_leaves=31,
            max_depth=6,
            min_child_samples=15,
            feature_fraction=0.85,
            bagging_fraction=0.80,
            bagging_freq=5,
            random_state=self.random_state,
            n_jobs=-1,
            importance_type="gain",
            verbose=-1
        )

        self.model.fit(
            X_mat, y_int,
            eval_set=eval_set,
            callbacks=[lgb.early_stopping(stopping_rounds=20, verbose=False)] if eval_set else None
        )
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("Model is not fitted yet.")
        X_mat = X.reindex(columns=self.feature_names, fill_value=0.0).fillna(0.0)
        raw_probs = self.model.predict_proba(X_mat)
        
        # If model trained on subset of classes, map to all 8 classes
        if hasattr(self.model, "classes_") and len(self.model.classes_) < 8:
            full_probs = np.zeros((len(X_mat), 8))
            for col_idx, class_val in enumerate(self.model.classes_):
                full_probs[:, int(class_val)] = raw_probs[:, col_idx]
            return full_probs
        return raw_probs

    def predict(self, X: pd.DataFrame) -> Tuple[List[str], np.ndarray, np.ndarray]:
        """Returns (class_labels, predicted_classes_int, probabilities_matrix)."""
        probs = self.predict_proba(X)
        preds_int = np.argmax(probs, axis=1)
        labels = [CLASS_MAP.get(i, "OTHER_SENSOR_FAULT") for i in preds_int]
        return labels, preds_int, probs

    def save(self, filepath: Union[str, Path]):
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "features": self.feature_names}, filepath)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "SkyGuardLightGBMClassifier":
        data = joblib.load(filepath)
        clf = cls()
        clf.model = data["model"]
        clf.feature_names = data["features"]
        return clf
