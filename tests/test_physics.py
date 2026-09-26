"""Unit tests for deterministic physics calculations and invariants."""

import pytest
import numpy as np
from skyguard.physics.thermodynamics import AtmosphericThermodynamics
from skyguard.physics.invariants import PhysicsInvariantChecker
from skyguard.physics.features import PhysicsFeatureEngine
import pandas as pd


def test_magnus_dew_point_invariant():
    """Dew point must ALWAYS be less than or equal to ambient temperature when RH <= 100%."""
    temps = np.linspace(-30.0, 55.0, 50)
    rhs = np.linspace(1.0, 100.0, 50)

    for t in temps:
        for rh in rhs:
            td = AtmosphericThermodynamics.dew_point(t, rh)
            assert td <= (t + 1e-4), f"Physics Invariant Failed: Td ({td}) > T ({t}) at RH={rh}%"


def test_vapor_pressure_deficit_non_negative():
    """Vapor Pressure Deficit must be strictly >= 0."""
    temps = np.array([0.0, 15.0, 25.0, 42.0, 50.0])
    rhs = np.array([10.0, 50.0, 80.0, 95.0, 100.0])

    for t, rh in zip(temps, rhs):
        vpd = AtmosphericThermodynamics.vapor_pressure_deficit(t, rh)
        assert vpd >= -1e-5, f"VPD is negative: {vpd} at T={t}, RH={rh}"


def test_potential_temperature_poisson():
    """Potential temperature at 1000 hPa must equal ambient temperature in Kelvin."""
    t_c = 25.0
    p_hpa = 1000.0
    theta = AtmosphericThermodynamics.potential_temperature(t_c, p_hpa)
    expected_k = 25.0 + 273.15
    assert abs(theta - expected_k) < 1e-3, f"Theta mismatch: {theta} vs {expected_k}"


def test_physics_invariant_checker_violation():
    """Checker must detect when dew point mathematically exceeds temperature."""
    is_valid, score, details = PhysicsInvariantChecker.check_invariants(
        temp_c=20.0, pressure_hpa=1013.0, rh_pct=105.0 # Supersaturated anomaly
    )
    assert not is_valid or score > 0.0
    assert len(details["violations"]) > 0


def test_physics_feature_engine_transform():
    """Feature engine must compute all derived meteorological parameters."""
    df = pd.DataFrame({
        "timestamp": pd.date_range("2026-05-01", periods=10, freq="15min", tz="UTC"),
        "station_id": "TEST_STATION",
        "temperature": np.linspace(30.0, 35.0, 10),
        "pressure": np.linspace(1005.0, 1003.0, 10),
        "relative_humidity": np.linspace(60.0, 45.0, 10)
    })
    engine = PhysicsFeatureEngine()
    enriched = engine.transform(df)

    assert "dew_point" in enriched.columns
    assert "vpd" in enriched.columns
    assert "potential_temperature" in enriched.columns
    assert "d_temp_dt" in enriched.columns
    assert "physics_anomaly_score" in enriched.columns
