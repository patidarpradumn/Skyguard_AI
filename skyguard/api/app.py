"""Production FastAPI application with REST endpoints and WebSocket live stream."""

import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from skyguard.api.schemas import IngestObservationRequest, AnomalySimulationRequest, PredictionResponse
from skyguard.models.pipeline import SkyGuardPipeline
from skyguard.models.lgbm_classifier import SkyGuardLightGBMClassifier
from skyguard.explainability.shap_explainer import TreeSHAPExplainer
from skyguard.explainability.diagnostic_rules import DiagnosticExplainer
from skyguard.imputation.kalman import KalmanSelfHealer
from skyguard.health.tracker import SensorHealthTracker
from skyguard.simulations.scenario_runner import ScenarioRunner
from skyguard.edge.edge_simulator import EdgeSimulator


app = FastAPI(
    title="SkyGuard AI - AWS Anomaly Detection & Self-Healing API",
    description="Physics-Informed, Multivariate, Explainable Anomaly Detection for Automatic Weather Stations (SIH26073)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State Container
class State:
    def __init__(self):
        self.pipeline = SkyGuardPipeline()
        self.kalman_map: Dict[str, KalmanSelfHealer] = {}
        self.health_tracker = SensorHealthTracker()
        self.history: List[Dict[str, Any]] = []
        self.active_alerts: List[Dict[str, Any]] = []
        self.active_websockets: List[WebSocket] = []
        self.model = None
        self.shap_explainer = None
        self.edge_sim = EdgeSimulator()
        self.stations_meta = {
            "IMD_DELHI_SAFDARJUNG": {"name": "Safdarjung AWS", "latitude": 28.5850, "longitude": 77.2060, "elevation": 216.0, "status": "HEALTHY"},
            "IMD_DELHI_PALAM": {"name": "Palam Airport AWS", "latitude": 28.5667, "longitude": 77.1167, "elevation": 237.0, "status": "HEALTHY"},
            "IMD_DELHI_LODHI": {"name": "Lodhi Road AWS", "latitude": 28.5900, "longitude": 77.2200, "elevation": 212.0, "status": "HEALTHY"},
            "IMD_DELHI_AYANAGAR": {"name": "Ayanagar AWS", "latitude": 28.4800, "longitude": 77.1300, "elevation": 268.0, "status": "HEALTHY"},
            "IMD_DELHI_RIDGE": {"name": "Delhi Ridge AWS", "latitude": 28.6700, "longitude": 77.2100, "elevation": 230.0, "status": "HEALTHY"},
        }

state = State()

# Mount Dashboard Static Files if present
dashboard_path = Path("dashboard")
if dashboard_path.exists():
    app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")
    @app.get("/")
    def root_redirect():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/dashboard/index.html")


@app.on_event("startup")
def startup_event():
    # Attempt to load trained model or train initial model in memory
    model_path = Path("skyguard/data/models/lightgbm_model.joblib")
    if model_path.exists():
        try:
            state.model = SkyGuardLightGBMClassifier.load(model_path)
            state.shap_explainer = TreeSHAPExplainer(state.model)
            print("Loaded trained LightGBM model successfully.")
        except Exception as e:
            print(f"Model load warning: {e}")

    # Seed initial 48 hours of benchmark data to populate history
    runner = ScenarioRunner(seed=42)
    init_df = runner.generate_benchmark_dataset(n_days=3)
    processed_df = state.pipeline.process_dataframe(init_df)

    for _, row in processed_df.iterrows():
        r = row.to_dict()
        state.history.append(r)
        if r.get("label") not in ["NORMAL", "NONE"] and r.get("anomaly_severity") in ["HIGH", "CRITICAL"]:
            state.active_alerts.append({
                "alert_id": f"ALT_{len(state.active_alerts) + 1:04d}",
                "timestamp": str(r.get("timestamp")),
                "station_id": r.get("station_id"),
                "classification": r.get("label", "FAULT"),
                "severity": r.get("anomaly_severity", "HIGH"),
                "confidence": round(float(r.get("anomaly_confidence", 95.0)), 1),
                "summary": f"Fault detected: {r.get('fault_mode', 'Sensor Anomaly')}"
            })


def process_single_reading(req_dict: Dict[str, Any]) -> Dict[str, Any]:
    station_id = req_dict["station_id"]
    if station_id not in state.kalman_map:
        state.kalman_map[station_id] = KalmanSelfHealer()

    ts = req_dict.get("timestamp") or datetime.now(timezone.utc).isoformat()
    raw_df = pd.DataFrame([{
        "timestamp": ts,
        "station_id": station_id,
        "latitude": req_dict.get("latitude", 28.5850),
        "longitude": req_dict.get("longitude", 77.2060),
        "elevation": req_dict.get("elevation", 216.0),
        "temperature": req_dict["temperature"],
        "pressure": req_dict["pressure"],
        "relative_humidity": req_dict["relative_humidity"],
        "source": "IMD_AWS"
    }])

    enriched = state.pipeline.process_dataframe(raw_df)
    row = enriched.iloc[0]
    row_dict = row.to_dict()

    # Predict class
    if state.model is not None:
        labels, _, probs = state.model.predict(enriched)
        pred_label = labels[0]
        prob = float(np.max(probs[0]))
        shap_res = state.shap_explainer.explain_instance(enriched, top_k=4)
    else:
        pred_label = "NORMAL"
        prob = 0.95
        shap_res = {"predicted_class": "NORMAL", "confidence_pct": 95.0, "top_features": []}

    is_fault = pred_label in ["SPIKE", "FROZEN", "DRIFT", "COMMUNICATION_ERROR", "CORRUPTED_DATA", "OTHER_SENSOR_FAULT"]
    is_extreme = pred_label == "GENUINE_EXTREME_WEATHER"

    # Kalman Self-Healing Update
    meas = np.array([req_dict["temperature"], req_dict["pressure"], req_dict["relative_humidity"]], dtype=float)
    mask = np.array([not is_fault, not is_fault, not is_fault])
    healed, conf = state.kalman_map[station_id].update_step(meas, mask)

    # Health evaluation
    st_history = [h for h in state.history if h.get("station_id") == station_id]
    st_df = pd.DataFrame(st_history) if st_history else enriched
    health = state.health_tracker.evaluate_sensor_health(st_df)

    # Diagnostic Report
    diag = DiagnosticExplainer.generate_diagnostic_report(row_dict, shap_res)

    res = {
        "station_id": station_id,
        "timestamp": str(ts),
        "classification": pred_label,
        "anomaly_score": round(float(row_dict.get("overall_anomaly_score", 0.0)), 3),
        "confidence_pct": round(prob * 100.0, 1),
        "severity": row_dict.get("anomaly_severity", "LOW"),
        "is_genuine_extreme_weather": is_extreme,
        "is_sensor_fault": is_fault,
        "raw_readings": {
            "temperature_c": req_dict["temperature"],
            "pressure_hpa": req_dict["pressure"],
            "relative_humidity_pct": req_dict["relative_humidity"]
        },
        "derived_physics": {
            "dew_point_c": round(float(row_dict.get("dew_point", 0.0)), 2),
            "vpd_hpa": round(float(row_dict.get("vpd", 0.0)), 3),
            "potential_temp_k": round(float(row_dict.get("potential_temperature", 0.0)), 1)
        },
        "self_healed_imputation": {
            "imputed_temperature_c": round(float(healed[0]), 2),
            "imputed_pressure_hpa": round(float(healed[1]), 2),
            "imputed_humidity_pct": round(float(healed[2]), 1),
            "imputation_confidence_pct": round(conf, 1)
        },
        "sensor_health": health,
        "diagnostic_explanation": diag
    }

    # Append to state history
    state.history.append(row_dict)
    if len(state.history) > 5000:
        state.history.pop(0)

    if is_fault and row_dict.get("anomaly_severity") in ["HIGH", "CRITICAL"]:
        state.active_alerts.append({
            "alert_id": f"ALT_{len(state.active_alerts) + 1:04d}",
            "timestamp": str(ts),
            "station_id": station_id,
            "classification": pred_label,
            "severity": row_dict.get("anomaly_severity", "HIGH"),
            "confidence": round(prob * 100.0, 1),
            "summary": diag.get("headline", "Sensor Anomaly")
        })

    return res


@app.post("/ingest", response_model=PredictionResponse)
def ingest_observation(req: IngestObservationRequest):
    return process_single_reading(req.dict())


@app.post("/predict", response_model=PredictionResponse)
def predict_observation(req: IngestObservationRequest):
    return process_single_reading(req.dict())


@app.post("/simulate-anomaly")
def simulate_anomaly(req: AnomalySimulationRequest):
    station_id = req.station_id
    if req.anomaly_type.upper() == "SPIKE":
        reading = {"temperature": 48.5, "pressure": 1004.0, "relative_humidity": 52.0}
    elif req.anomaly_type.upper() == "FROZEN":
        reading = {"temperature": 32.0, "pressure": 1005.0, "relative_humidity": 50.0}
    elif req.anomaly_type.upper() == "DRIFT":
        reading = {"temperature": 39.8, "pressure": 1004.5, "relative_humidity": 54.0}
    elif req.anomaly_type.upper() == "HEATWAVE":
        reading = {"temperature": 46.2, "pressure": 999.5, "relative_humidity": 14.0}
    elif req.anomaly_type.upper() == "SQUALL":
        reading = {"temperature": 24.0, "pressure": 1008.0, "relative_humidity": 96.0}
    else:
        reading = {"temperature": -999.0, "pressure": 1000.0, "relative_humidity": 50.0}

    payload = {
        "station_id": station_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **reading
    }
    return process_single_reading(payload)


@app.get("/stations")
def list_stations():
    stations = []
    for sid, meta in state.stations_meta.items():
        st_history = [h for h in state.history if h.get("station_id") == sid]
        latest = st_history[-1] if st_history else {}
        health = state.health_tracker.evaluate_sensor_health(pd.DataFrame(st_history) if st_history else pd.DataFrame())
        stations.append({
            "station_id": sid,
            "name": meta["name"],
            "latitude": meta["latitude"],
            "longitude": meta["longitude"],
            "elevation": meta["elevation"],
            "status": health["health_state"],
            "health_score": health["overall_health_score"],
            "latest_temperature_c": latest.get("temperature", 32.5),
            "latest_pressure_hpa": latest.get("pressure", 1005.0),
            "latest_humidity_pct": latest.get("relative_humidity", 52.0)
        })
    return {"total_stations": len(stations), "stations": stations}


@app.get("/stations/{station_id}")
def get_station_detail(station_id: str):
    if station_id not in state.stations_meta:
        raise HTTPException(status_code=404, detail="Station not found")
    meta = state.stations_meta[station_id]
    st_history = [h for h in state.history if h.get("station_id") == station_id]
    recent_readings = [{
        "timestamp": str(h.get("timestamp")),
        "temperature": h.get("temperature"),
        "pressure": h.get("pressure"),
        "relative_humidity": h.get("relative_humidity"),
        "dew_point": h.get("dew_point"),
        "anomaly_score": h.get("overall_anomaly_score", 0.0),
        "label": h.get("label", "NORMAL")
    } for h in st_history[-48:]]

    health = state.health_tracker.evaluate_sensor_health(pd.DataFrame(st_history) if st_history else pd.DataFrame())

    return {
        "station_id": station_id,
        "metadata": meta,
        "health": health,
        "recent_observations": recent_readings
    }


@app.get("/stations/{station_id}/health")
def get_station_health(station_id: str):
    st_history = [h for h in state.history if h.get("station_id") == station_id]
    return state.health_tracker.evaluate_sensor_health(pd.DataFrame(st_history) if st_history else pd.DataFrame())


@app.get("/alerts")
def get_alerts():
    return {"total_alerts": len(state.active_alerts), "alerts": state.active_alerts[-50:]}


@app.get("/alerts/{alert_id}")
def get_alert_detail(alert_id: str):
    for a in state.active_alerts:
        if a.get("alert_id") == alert_id:
            return a
    raise HTTPException(status_code=404, detail="Alert not found")


@app.get("/metrics")
def get_system_metrics():
    edge_metrics = state.edge_sim.benchmark_edge_performance(n_iterations=200)
    return {
        "pipeline_status": "ONLINE",
        "total_observations_processed": len(state.history),
        "active_alerts_count": len(state.active_alerts),
        "active_stations_count": len(state.stations_meta),
        "edge_metrics": edge_metrics
    }


@app.get("/model-info")
def get_model_info():
    return {
        "model_type": "LightGBM Multiclass Gradient Boosted Decision Tree",
        "features_count": len(state.model.feature_names) if state.model else 35,
        "classes": ["NORMAL", "GENUINE_EXTREME_WEATHER", "SPIKE", "FROZEN", "DRIFT", "COMMUNICATION_ERROR", "CORRUPTED_DATA", "OTHER_SENSOR_FAULT"],
        "provenance_sources": ["IMD_AWS", "NOAA_ISD", "ERA5 (Reference)", "SYNTHETIC"],
        "explainability_engine": "TreeSHAP Local Attributions + WMO/IMD Thermodynamic Invariants",
        "self_healing_filter": "1D/3D Recursive State-Space Kalman Filter"
    }


@app.websocket("/ws/live")
async def websocket_live_stream(websocket: WebSocket):
    await websocket.accept()
    state.active_websockets.append(websocket)
    try:
        # Stream observations cyclically from Delhi AWS network
        runner = ScenarioRunner(seed=42)
        stream_df = runner.generate_benchmark_dataset(n_days=2)
        enriched_stream = state.pipeline.process_dataframe(stream_df)

        for _, row in enriched_stream.iterrows():
            r = row.to_dict()
            msg = {
                "timestamp": str(r.get("timestamp")),
                "station_id": r.get("station_id"),
                "temperature": r.get("temperature"),
                "pressure": r.get("pressure"),
                "relative_humidity": r.get("relative_humidity"),
                "dew_point": round(float(r.get("dew_point", 0.0)), 2),
                "vpd": round(float(r.get("vpd", 0.0)), 3),
                "anomaly_score": round(float(r.get("overall_anomaly_score", 0.0)), 3),
                "classification": r.get("label", "NORMAL"),
                "severity": r.get("anomaly_severity", "LOW"),
                "is_extreme": r.get("label") == "GENUINE_EXTREME_WEATHER",
                "is_fault": r.get("label") in ["SPIKE", "FROZEN", "DRIFT", "COMMUNICATION_ERROR", "CORRUPTED_DATA", "OTHER_SENSOR_FAULT"]
            }
            await websocket.send_text(json.dumps(msg))
            await asyncio.sleep(0.8) # 800ms stream tick
    except WebSocketDisconnect:
        state.active_websockets.remove(websocket)
    except Exception:
        if websocket in state.active_websockets:
            state.active_websockets.remove(websocket)
