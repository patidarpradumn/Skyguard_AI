"""Unit tests for anomaly injection and extreme weather generation."""

import pytest
import numpy as np
import pandas as pd
from skyguard.simulations.anomaly_injector import AnomalyInjectionEngine
from skyguard.simulations.extreme_weather import ExtremeWeatherSimulator
from skyguard.ingestion.synthetic import SyntheticAWSGenerator


@pytest.fixture
def base_weather_df():
    gen = SyntheticAWSGenerator(seed=42)
    return gen.generate_station_timeseries(n_days=5)


def test_spike_injection(base_weather_df):
    injector = AnomalyInjectionEngine(seed=42)
    df, indices = injector.inject_spikes(base_weather_df, parameter="temperature", magnitude=15.0, indices=[10])
    assert df.loc[10, "temperature"] > base_weather_df.loc[10, "temperature"] + 14.0
    assert df.loc[10, "label"] == "SPIKE"


def test_frozen_injection(base_weather_df):
    injector = AnomalyInjectionEngine(seed=42)
    df = injector.inject_frozen(base_weather_df, parameter="temperature", start_idx=20, duration=8)
    frozen_slice = df.loc[20:27, "temperature"]
    assert frozen_slice.nunique() == 1
    assert (df.loc[20:27, "label"] == "FROZEN").all()


def test_drift_injection(base_weather_df):
    injector = AnomalyInjectionEngine(seed=42)
    df = injector.inject_drift(base_weather_df, parameter="temperature", drift_rate_per_step=0.5, start_idx=30, duration=10)
    assert df.loc[39, "temperature"] > base_weather_df.loc[39, "temperature"] + 4.5
    assert (df.loc[30:39, "label"] == "DRIFT").all()


def test_extreme_heatwave_simulation(base_weather_df):
    sim = ExtremeWeatherSimulator(seed=42)
    df = sim.inject_heatwave(base_weather_df, start_idx=20, duration_samples=24, peak_temp_anomaly_c=9.0)
    assert (df.loc[20:43, "label"] == "GENUINE_EXTREME_WEATHER").all()
    # Check that RH dropped coherently while T rose
    t_peak_idx = 20 + 12
    assert df.loc[t_peak_idx, "temperature"] > base_weather_df.loc[t_peak_idx, "temperature"]
    assert df.loc[t_peak_idx, "relative_humidity"] < base_weather_df.loc[t_peak_idx, "relative_humidity"]
