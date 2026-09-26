"""End-to-End Feature Processing & Pipeline Orchestrator for SkyGuard AI."""

import pandas as pd
from typing import Dict, Any, Tuple
from skyguard.preprocessing.validator import DataValidationPipeline
from skyguard.physics.features import PhysicsFeatureEngine
from skyguard.temporal.baseline import TemporalEngine
from skyguard.multivariate.mahalanobis import MahalanobisEngine
from skyguard.multivariate.coherence import MultivariateCoherenceEngine
from skyguard.spatial.corroborator import SpatialCorroborator
from skyguard.fusion.fusion_layer import EvidenceFusionLayer


class SkyGuardPipeline:
    """Master feature orchestration pipeline executing all scientific modules in strict sequence."""

    def __init__(self):
        self.validator = DataValidationPipeline()
        self.physics = PhysicsFeatureEngine()
        self.temporal = TemporalEngine()
        self.mahalanobis = MahalanobisEngine()
        self.coherence = MultivariateCoherenceEngine()
        self.spatial = SpatialCorroborator()
        self.fusion = EvidenceFusionLayer()

    def process_dataframe(self, df: pd.DataFrame, is_training: bool = False) -> pd.DataFrame:
        """Transforms raw station dataframe into full scientific feature set."""
        df = df.copy()

        # Step 1: Quality Control & Normalization
        df = self.validator.process(df)

        # Step 2: Atmospheric Physics & Thermodynamics
        df = self.physics.transform(df)

        # Step 3: Diurnal & Multi-Scale Temporal Features
        df = self.temporal.transform(df)

        # Step 4: Multivariate Covariance & Mahalanobis Distance
        if is_training:
            self.mahalanobis.fit(df)
        df = self.mahalanobis.transform(df)
        df = self.coherence.transform(df)

        # Step 5: Spatial Neighborhood Corroboration
        df = self.spatial.transform(df)

        # Step 6: Evidence Fusion & Calibrated Scoring
        df = self.fusion.fuse(df)

        return df
