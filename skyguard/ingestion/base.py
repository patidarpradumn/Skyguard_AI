"""Abstract Base Adapter for Data Ingestion in SkyGuard AI."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import pandas as pd
from pathlib import Path
from skyguard.ingestion.provenance import ObservationSchema, DataProvenance


class BaseDataAdapter(ABC):
    """Abstract interface for all SkyGuard data sources."""

    def __init__(self, source_type: DataProvenance):
        self.source_type = source_type

    @abstractmethod
    def load(self, source_path_or_url: Union[str, Path, Dict[str, Any]]) -> pd.DataFrame:
        """Load data from source and return a canonical pandas DataFrame."""
        pass

    @abstractmethod
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """Validate that all mandatory core variables exist and have correct types."""
        pass

    def standardize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names, ensure types, and attach provenance tag."""
        required_cols = ["timestamp", "station_id", "latitude", "longitude", "temperature", "pressure", "relative_humidity"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Standardization error: Missing required column '{col}'. Available: {list(df.columns)}")

        # Convert timestamp to UTC datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df["station_id"] = df["station_id"].astype(str)
        df["latitude"] = df["latitude"].astype(float)
        df["longitude"] = df["longitude"].astype(float)
        if "elevation" in df.columns:
            df["elevation"] = pd.to_numeric(df["elevation"], errors="coerce")
        else:
            df["elevation"] = None

        df["temperature"] = df["temperature"].astype(float)
        df["pressure"] = df["pressure"].astype(float)
        df["relative_humidity"] = df["relative_humidity"].astype(float)
        df["source"] = self.source_type.value

        # Sort chronologically per station
        df = df.sort_values(by=["station_id", "timestamp"]).reset_index(drop=True)
        return df
