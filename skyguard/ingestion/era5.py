"""Copernicus ERA5 Data Ingestion Adapter (Climatological Reference Only)."""

import pandas as pd
from pathlib import Path
from typing import Union, Dict, Any
from skyguard.ingestion.base import BaseDataAdapter
from skyguard.ingestion.provenance import DataProvenance


class ERA5Adapter(BaseDataAdapter):
    """Adapter for ERA5 Reanalysis data.
    CRITICAL CONSTRAINT: ERA5 is used strictly as a climatological reference baseline,
    never represented as direct AWS sensor ground truth.
    """

    def __init__(self):
        super().__init__(source_type=DataProvenance.ERA5)

    def load(self, source_path_or_url: Union[str, Path, Dict[str, Any]]) -> pd.DataFrame:
        if isinstance(source_path_or_url, (str, Path)):
            path = Path(source_path_or_url)
            if not path.exists():
                raise FileNotFoundError(f"ERA5 data file not found: {path}")
            df = pd.read_csv(path)
        elif isinstance(source_path_or_url, dict):
            df = pd.DataFrame(source_path_or_url)
        else:
            raise TypeError("Source must be a filepath or dict")

        # Map ERA5 column names (e.g. t2m in Kelvin, sp in Pa)
        col_map = {
            "valid_time": "timestamp",
            "time": "timestamp",
            "t2m": "temperature",
            "sp": "pressure",
            "r": "relative_humidity",
            "rh": "relative_humidity"
        }
        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

        # Convert Kelvin to Celsius if mean temp > 200
        if "temperature" in df.columns and df["temperature"].dropna().mean() > 200.0:
            df["temperature"] = df["temperature"] - 273.15

        # Convert Pa to hPa if mean pressure > 20000
        if "pressure" in df.columns and df["pressure"].dropna().mean() > 20000.0:
            df["pressure"] = df["pressure"] / 100.0

        if "station_id" not in df.columns:
            df["station_id"] = "ERA5_GRID_POINT"

        if "latitude" not in df.columns:
            df["latitude"] = 28.6139
        if "longitude" not in df.columns:
            df["longitude"] = 77.2090

        self.validate_schema(df)
        return self.standardize(df)

    def validate_schema(self, df: pd.DataFrame) -> bool:
        required = ["timestamp", "temperature", "pressure", "relative_humidity"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"ERA5 reference data missing required fields: {missing}")
        return True
