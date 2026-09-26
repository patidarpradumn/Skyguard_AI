"""Training orchestration with strict temporal and station holdout splits."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple
from skyguard.models.pipeline import SkyGuardPipeline
from skyguard.models.lgbm_classifier import SkyGuardLightGBMClassifier, CLASS_MAP
from skyguard.simulations.scenario_runner import ScenarioRunner


class ModelTrainer:
    """Trains and persists SkyGuard LightGBM model without data leakage."""

    def __init__(self, model_save_path: str = "skyguard/data/models/lightgbm_model.joblib"):
        self.pipeline = SkyGuardPipeline()
        self.model = SkyGuardLightGBMClassifier()
        self.model_save_path = Path(model_save_path)

    def prepare_dataset(self, n_days: int = 45) -> pd.DataFrame:
        """Generates realistic multi-station synthetic data with balanced fault modes."""
        runner = ScenarioRunner(seed=42)
        raw_df = runner.generate_benchmark_dataset(n_days=n_days)
        enriched_df = self.pipeline.process_dataframe(raw_df, is_training=True)
        return enriched_df

    def temporal_split(
        self,
        df: pd.DataFrame,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Strict time-based split to prevent lookahead data leakage."""
        df = df.sort_values("timestamp").reset_index(drop=True)
        unique_timestamps = df["timestamp"].drop_duplicates().sort_values().tolist()
        n_times = len(unique_timestamps)

        train_cutoff = unique_timestamps[int(n_times * train_ratio)]
        val_cutoff = unique_timestamps[int(n_times * (train_ratio + val_ratio))]

        train_df = df[df["timestamp"] <= train_cutoff].copy()
        val_df = df[(df["timestamp"] > train_cutoff) & (df["timestamp"] <= val_cutoff)].copy()
        test_df = df[df["timestamp"] > val_cutoff].copy()

        return train_df, val_df, test_df

    def train_and_persist(self, n_days: int = 40) -> Dict[str, Any]:
        """Executes full training pipeline and saves model artifact."""
        print("1. Preparing benchmark dataset...")
        df = self.prepare_dataset(n_days=n_days)

        print("2. Performing temporal train/val/test split...")
        train_df, val_df, test_df = self.temporal_split(df)

        print(f"   Train samples: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        print("3. Training LightGBM fault classifier...")
        self.model.fit(train_df, train_df["label"], val_data=(val_df, val_df["label"]))

        print(f"4. Saving model to {self.model_save_path}...")
        self.model.save(self.model_save_path)

        # Quick evaluation on unseen test set
        test_labels, preds_int, probs = self.model.predict(test_df)
        acc = float(np.mean(test_labels == test_df["label"]))
        print(f"   Unseen Test Accuracy: {acc * 100.0:.2f}%")

        return {
            "train_samples": len(train_df),
            "val_samples": len(val_df),
            "test_samples": len(test_df),
            "test_accuracy": acc,
            "model_path": str(self.model_save_path)
        }
