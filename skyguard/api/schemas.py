"""Pydantic data models and schemas for SkyGuard AI REST API."""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class IngestObservationRequest(BaseModel):
    station_id: str = Field(..., example="AWS_IMD_DELHI_01")
    timestamp: Optional[str] = Field(None, example="2026-09-11T12:00:00Z")
    temperature: float = Field(..., description="Temperature in °C", example=34.5)
    pressure: float = Field(..., description="Pressure in hPa", example=1004.2)
    relative_humidity: float = Field(..., description="Relative Humidity in %", example=52.0)
    latitude: Optional[float] = Field(28.5850, example=28.5850)
    longitude: Optional[float] = Field(77.2060, example=77.2060)
    elevation: Optional[float] = Field(216.0, example=216.0)


class AnomalySimulationRequest(BaseModel):
    station_id: str = Field(..., example="AWS_IMD_DELHI_01")
    anomaly_type: str = Field(..., example="SPIKE", description="SPIKE, FROZEN, DRIFT, HEATWAVE, SQUALL")
    parameter: Optional[str] = Field("temperature", example="temperature")
    severity_magnitude: Optional[float] = Field(12.0, example=12.0)
    duration_samples: Optional[int] = Field(5, example=5)


class PredictionResponse(BaseModel):
    station_id: str
    timestamp: str
    classification: str
    anomaly_score: float
    confidence_pct: float
    severity: str
    is_genuine_extreme_weather: bool
    is_sensor_fault: bool
    raw_readings: Dict[str, Optional[float]]
    derived_physics: Dict[str, float]
    self_healed_imputation: Dict[str, Any]
    diagnostic_explanation: Dict[str, Any]
    sensor_health: Dict[str, Any]
