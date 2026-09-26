"""Unit tests for data ingestion, quality control, and provenance tagging."""

import pytest
import pandas as pd
from skyguard.ingestion.imd import IMDAWSAdapter
from skyguard.ingestion.noaa import NOAAISDAdapter
from skyguard.ingestion.era5 import ERA5Adapter
from skyguard.ingestion.synthetic import SyntheticAWSGenerator
from skyguard.preprocessing.validator import DataValidationPipeline


def test_synthetic_network_generation():
    gen = SyntheticAWSGenerator(seed=42)
    df = gen.generate_network(n_days=2)
    assert len(df) > 0
    assert df["station_id"].nunique() >= 4
    assert "source" in df.columns
    assert (df["source"] == "SYNTHETIC").all()


def test_imd_adapter_standardization():
    adapter = IMDAWSAdapter()
    sample_data = {
        "DateTime": ["2026-05-01 12:00:00", "2026-05-01 12:15:00"],
        "Station_ID": ["IMD_DELHI", "IMD_DELHI"],
        "TEMP": [35.2, 35.5],
        "PRESS": [1004.1, 1004.0],
        "RH": [48.0, 47.5],
        "LAT": [28.58, 28.58],
        "LON": [77.20, 77.20]
    }
    std_df = adapter.load(sample_data)
    assert "temperature" in std_df.columns
    assert "pressure" in std_df.columns
    assert "relative_humidity" in std_df.columns
    assert (std_df["source"] == "IMD_AWS").all()


def test_validation_pipeline_qc():
    pipeline = DataValidationPipeline()
    dirty_data = pd.DataFrame({
        "timestamp": pd.date_range("2026-05-01", periods=5, freq="15min", tz="UTC"),
        "station_id": "TEST_AWS",
        "latitude": 28.5,
        "longitude": 77.2,
        "temperature": [30.0, 31.0, 999.0, 32.0, 32.5], # Sentinel 999.0
        "pressure": [1005.0, 1005.2, 1005.1, 1005.3, 1005.0],
        "relative_humidity": [50.0, 52.0, 51.0, 49.0, 50.0]
    })
    clean_df = pipeline.process(dirty_data)
    assert pd.isna(clean_df.loc[2, "temperature"])
    assert "qc_passed" in clean_df.columns
