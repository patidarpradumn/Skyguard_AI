"""Scenario orchestration for synthetic benchmarks and simulations."""

import pandas as pd
from typing import Dict, Any, List
from skyguard.ingestion.synthetic import SyntheticAWSGenerator
from skyguard.simulations.anomaly_injector import AnomalyInjectionEngine
from skyguard.simulations.extreme_weather import ExtremeWeatherSimulator


class ScenarioRunner:
    """Creates unified multi-station datasets containing normal, faults, and genuine extreme events."""

    def __init__(self, seed: int = 42):
        self.generator = SyntheticAWSGenerator(seed=seed)
        self.injector = AnomalyInjectionEngine(seed=seed)
        self.extreme_sim = ExtremeWeatherSimulator(seed=seed)

    def generate_benchmark_dataset(self, n_days: int = 30) -> pd.DataFrame:
        """Generates a complete multi-station benchmark dataset with balanced classes."""
        # 1. Generate base normal multi-station network
        network_df = self.generator.generate_network(n_days=n_days)

        processed_dfs = []
        for idx, (station_id, group) in enumerate(network_df.groupby("station_id")):
            group = group.copy().reset_index(drop=True)
            n = len(group)

            if idx == 0:
                # Station 1: Pure Normal Reference Baseline
                processed_dfs.append(group)
            elif idx == 1:
                # Station 2: Sensor Spikes & Frozen Failures
                group, _ = self.injector.inject_spikes(group, parameter="temperature", magnitude=12.0, indices=[int(n * 0.15), int(n * 0.45)])
                group, _ = self.injector.inject_spikes(group, parameter="pressure", magnitude=-22.0, indices=[int(n * 0.70)])
                group = self.injector.inject_frozen(group, parameter="temperature", start_idx=int(n * 0.25), duration=18)
                group = self.injector.inject_frozen(group, parameter="relative_humidity", start_idx=int(n * 0.55), duration=24)
                processed_dfs.append(group)
            elif idx == 2:
                # Station 3: Sensor Drifts & Stuck Pins
                group = self.injector.inject_drift(group, parameter="temperature", drift_rate_per_step=0.20, start_idx=int(n * 0.20), duration=36)
                group = self.injector.inject_stuck_humidity(group, stuck_at=0.0, start_idx=int(n * 0.60), duration=20)
                group = self.injector.inject_stuck_humidity(group, stuck_at=99.8, start_idx=int(n * 0.80), duration=16)
                processed_dfs.append(group)
            elif idx == 3:
                # Station 4: Communication Failures, Bit Corruptions & Staircase
                group = self.injector.inject_packet_loss_and_outage(group, start_idx=int(n * 0.20), duration=12, mode="burst")
                group = self.injector.inject_corruptions(group, indices=[int(n * 0.45), int(n * 0.65)])
                group = self.injector.inject_quantization_staircase(group, parameter="temperature", step_size=3.0, start_idx=int(n * 0.75), duration=30)
                processed_dfs.append(group)
            elif idx == 4:
                # Station 5: Genuine Extreme Weather Events (Heatwave, Severe Squall, Depression)
                group = self.extreme_sim.inject_heatwave(group, start_idx=int(n * 0.15), duration_samples=48, peak_temp_anomaly_c=8.0)
                group = self.extreme_sim.inject_severe_squall(group, start_idx=int(n * 0.50), duration_samples=16)
                group = self.extreme_sim.inject_cyclonic_depression(group, start_idx=int(n * 0.75), duration_samples=60, central_pressure_drop_hpa=15.0)
                processed_dfs.append(group)

        full_df = pd.concat(processed_dfs, ignore_index=True)
        return full_df
