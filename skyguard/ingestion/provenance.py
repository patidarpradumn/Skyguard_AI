"""Data provenance and lineage metadata tracker for SkyGuard AI."""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class DataProvenance(str, Enum):
    IMD_AWS = "IMD_AWS"
    NOAA_ISD = "NOAA_ISD"
    ERA5 = "ERA5"
    SYNTHETIC = "SYNTHETIC"
    EXTERNAL_CSV = "EXTERNAL_CSV"


class ObservationSchema(BaseModel):
    """Canonical Observation Data Schema for SkyGuard AI.
    
    STRICT RAW INPUT CONSTRAINT: Only temperature, pressure, relative_humidity.
    All other values (lat/lon/elevation/station_id) are treated as metadata/context only.
    """
    timestamp: datetime = Field(..., description="Timestamp in UTC")
    station_id: str = Field(..., description="Unique station identifier")
    latitude: float = Field(..., description="Station latitude in decimal degrees")
    longitude: float = Field(..., description="Station longitude in decimal degrees")
    elevation: Optional[float] = Field(None, description="Station elevation in meters above sea level")
    temperature: float = Field(..., description="Air Temperature in Celsius (°C)")
    pressure: float = Field(..., description="Atmospheric Pressure in hPa (millibars)")
    relative_humidity: float = Field(..., description="Relative Humidity in percent (%)")
    source: DataProvenance = Field(..., description="Provenance source label")
    raw_status: str = Field("UNVALIDATED", description="Status flag of the raw observation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Auxiliary provenance metadata")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "station_id": self.station_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "elevation": self.elevation,
            "temperature": self.temperature,
            "pressure": self.pressure,
            "relative_humidity": self.relative_humidity,
            "source": self.source.value,
            "raw_status": self.raw_status,
            "metadata": self.metadata
        }
