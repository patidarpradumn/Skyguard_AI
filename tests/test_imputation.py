"""Unit tests for Kalman self-healing imputation, sensor health tracking, and edge AI."""

import pytest
import numpy as np
import pandas as pd
from skyguard.imputation.kalman import KalmanSelfHealer
from skyguard.health.tracker import SensorHealthTracker
from skyguard.edge.micropython_agent import SkyGuardMicroPythonAgent
from skyguard.edge.c_code_generator import EdgeCCodeGenerator


def test_kalman_filter_continuity_and_raw_preservation():
    healer = KalmanSelfHealer()
    healer.initialize(init_temp=30.0, init_press=1005.0, init_rh=50.0)

    # Simulate spike at step 3
    meas_list = [
        [30.2, 1005.0, 49.5],
        [30.4, 1005.1, 49.0],
        [48.0, 1005.0, 48.5], # Transient Spike
        [30.6, 1004.9, 48.0]
    ]
    valid_masks = [
        [True, True, True],
        [True, True, True],
        [False, True, True], # Temperature flagged as fault
        [True, True, True]
    ]

    for meas, mask in zip(meas_list, valid_masks):
        state, conf = healer.update_step(np.array(meas), np.array(mask))

    # After step 3 (spike rejected), Kalman estimated temp should be smooth (~30.5°C), NOT 48.0°C!
    assert state[0] < 35.0, f"Kalman failed to filter spike: state={state[0]}"


def test_sensor_health_degradation():
    tracker = SensorHealthTracker()
    df_clean = pd.DataFrame({"label": ["NORMAL"] * 96, "physics_td_violation": [False] * 96})
    health_clean = tracker.evaluate_sensor_health(df_clean)
    assert health_clean["overall_health_score"] == 100.0
    assert health_clean["health_state"] == "HEALTHY"

    # Degraded sensor with repeated spikes and frozen cycles
    df_faulty = pd.DataFrame({
        "label": ["NORMAL"] * 60 + ["SPIKE"] * 10 + ["FROZEN"] * 26,
        "physics_td_violation": [False] * 90 + [True] * 6
    })
    health_faulty = tracker.evaluate_sensor_health(df_faulty)
    assert health_faulty["overall_health_score"] < 60.0
    assert health_faulty["health_state"] in ["DEGRADED", "CRITICAL"]


def test_edge_micropython_agent():
    agent = SkyGuardMicroPythonAgent(init_temp=30.0, init_press=1005.0, init_rh=50.0)
    # Normal reading
    res_norm = agent.process_observation(30.2, 1005.0, 49.5)
    assert res_norm["classification"] == "NORMAL"
    assert not res_norm["is_fault"]

    # Spike reading
    res_spike = agent.process_observation(45.0, 1005.0, 49.0)
    assert res_spike["classification"] == "SPIKE"
    assert res_spike["is_fault"]


def test_edge_c_code_generation():
    h_code = EdgeCCodeGenerator.generate_c_header()
    c_code = EdgeCCodeGenerator.generate_c_source()

    assert "skyguard_edge_process" in h_code
    assert "skyguard_edge_process" in c_code
    assert "MAGNUS_A" in c_code
