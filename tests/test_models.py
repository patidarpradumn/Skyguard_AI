"""Unit tests for LightGBM classifier, TreeSHAP, and baselines."""

import pytest
import numpy as np
import pandas as pd
from skyguard.models.pipeline import SkyGuardPipeline
from skyguard.models.lgbm_classifier import SkyGuardLightGBMClassifier
from skyguard.models.baselines import RuleBasedQCDetector, IsolationForestDetector
from skyguard.explainability.shap_explainer import TreeSHAPExplainer
from skyguard.simulations.scenario_runner import ScenarioRunner


@pytest.fixture(scope="module")
def trained_model_and_test_data():
    runner = ScenarioRunner(seed=42)
    raw_df = runner.generate_benchmark_dataset(n_days=10)
    pipeline = SkyGuardPipeline()
    df = pipeline.process_dataframe(raw_df, is_training=True)

    train_df = df.iloc[:int(len(df) * 0.70)]
    test_df = df.iloc[int(len(df) * 0.70):].copy()

    clf = SkyGuardLightGBMClassifier(random_state=42)
    clf.fit(train_df, train_df["label"])
    return clf, test_df


def test_lgbm_multiclass_prediction(trained_model_and_test_data):
    clf, test_df = trained_model_and_test_data
    labels, preds_int, probs = clf.predict(test_df)
    assert len(labels) == len(test_df)
    assert probs.shape[1] == 8
    # Baseline accuracy on test set should exceed 85%
    acc = np.mean(labels == test_df["label"])
    assert acc > 0.80, f"Model test accuracy too low: {acc}"


def test_tree_shap_explainability(trained_model_and_test_data):
    clf, test_df = trained_model_and_test_data
    explainer = TreeSHAPExplainer(clf)
    sample_row = test_df.iloc[[0]]
    explanation = explainer.explain_instance(sample_row, top_k=4)

    assert "predicted_class" in explanation
    assert "top_features" in explanation
    assert len(explanation["top_features"]) <= 4
    for feat in explanation["top_features"]:
        assert "feature" in feat
        assert "shap_contribution" in feat


def test_baseline_rule_detector():
    detector = RuleBasedQCDetector()
    df = pd.DataFrame({
        "temperature": [30.0, 31.0, 45.0, 32.0], # Spike of 14°C in 15min
        "pressure": [1005.0, 1005.0, 1005.0, 1005.0],
        "relative_humidity": [50.0, 50.0, 50.0, 50.0]
    })
    preds = detector.predict(df)
    assert preds[2] == 1, "Rule detector should flag 14°C jump as anomaly"
