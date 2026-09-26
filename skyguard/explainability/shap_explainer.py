"""TreeSHAP local feature attribution for LightGBM models."""

import numpy as np
import pandas as pd
import shap
from typing import Dict, Any, List, Optional
from skyguard.models.lgbm_classifier import SkyGuardLightGBMClassifier, FEATURE_COLUMNS, CLASS_MAP


class TreeSHAPExplainer:
    """Computes exact polynomial-time TreeSHAP values for fault predictions."""

    def __init__(self, classifier: SkyGuardLightGBMClassifier):
        self.clf = classifier
        if self.clf.model is None:
            raise ValueError("Classifier must be fitted before creating TreeSHAP explainer.")
        self.explainer = shap.TreeExplainer(self.clf.model)
        self.feature_names = self.clf.feature_names

    def explain_instance(self, row_df: pd.DataFrame, top_k: int = 5) -> Dict[str, Any]:
        """Calculates SHAP attribution for a single observation record."""
        X_mat = row_df.reindex(columns=self.feature_names, fill_value=0.0).fillna(0.0)
        shap_values = self.explainer.shap_values(X_mat)

        # Get predicted class index
        probs = self.clf.predict_proba(row_df)[0]
        pred_class_idx = int(np.argmax(probs))
        pred_label = CLASS_MAP.get(pred_class_idx, "UNKNOWN")

        # In multiclass, shap_values is typically a list of arrays per class, or 3D array (n_samples, n_features, n_classes)
        if isinstance(shap_values, list):
            class_shap = shap_values[pred_class_idx][0]
        elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
            class_shap = shap_values[0, :, pred_class_idx]
        else:
            class_shap = shap_values[0]

        # Sort features by absolute contribution
        sorted_indices = np.argsort(np.abs(class_shap))[::-1]

        top_contributions = []
        for i in sorted_indices[:top_k]:
            feat_name = self.feature_names[i]
            val = float(X_mat.iloc[0, i])
            shap_val = float(class_shap[i])
            top_contributions.append({
                "feature": feat_name,
                "value": round(val, 3),
                "shap_contribution": round(shap_val, 4),
                "direction": "INCREASES_RISK" if shap_val > 0 else "DECREASES_RISK"
            })

        return {
            "predicted_class": pred_label,
            "confidence_pct": round(float(probs[pred_class_idx]) * 100.0, 1),
            "top_features": top_contributions
        }
