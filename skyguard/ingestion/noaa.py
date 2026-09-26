"""NOAA ISD Data Ingestion Adapter."""

import pandas as pd
from pathlib import Path
from typing import Union, Dict, Any
from skyguard.ingestion.base import BaseDataAdapter
from skyguard.ingestion.provenance import DataProvenance


class NOAAISDAdapter(BaseDataAdapter):
    """Adapter for NOAA Integrated Surface Database (ISD).
    Standardizes NOAA ISD lite or full CSV records.
    """

    def __init__(self):
        super().__init__(source_type=DataProvenance.NOAA_ISD)

    def load(self, source_path_or_url: Union[str, Path, Dict[str, Any]]) -> pd.DataFrame:
        if isinstance(source_path_or_url, (str, Path)):
            path = Path(source_path_or_url)
            if not path.exists():
                raise FileNotFoundError(f"NOAA ISD data file not found: {path}")
            df = pd.read_csv(path)
        elif isinstance(source_path_or_url, dict):
            df = pd.DataFrame(source_path_or_url)
        else:
            raise TypeError("Source must be a filepath or dict")

        # Map NOAA columns
        column_mapping = {
            "DATE": "timestamp",
            "STATION": "station_id",
            "LATITUDE": "latitude",
            "LONGITUDE": "longitude",
            "ELEVATION": "elevation",
            "TMP": "temperature",
            "SLP": "pressure",
            "RH": "relative_humidity"
        }
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

        # NOAA temperatures are often stored in tenths of degrees Celsius (e.g. +0250)
        # Check if values are > 100 on average and rescale
        if "temperature" in df.columns and df["temperature"].dropna().mean() > 80.0:
            df["temperature"] = df["temperature"] / 10.0

        if "pressure" in df.columns and df["pressure"].dropna().mean() > 5000.0:
            df["pressure"] = df["pressure"] / 10.0

        self.validate_schema(df)
        return self.standardize(df)

    def validate_schema(self, df: pd.DataFrame) -> bool:
        required = ["timestamp", "station_id", "temperature", "pressure", "relative_humidity"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"NOAA ISD data is missing required meteorological columns: {missing}")
        if "latitude" not in df.columns:
            df["latitude"] = 0.0
        if "longitude" not in df.columns:
            df["longitude"] = 0.0
        return True
