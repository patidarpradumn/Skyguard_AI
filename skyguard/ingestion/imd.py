"""IMD AWS Data Ingestion Adapter."""

import pandas as pd
from pathlib import Path
from typing import Union, Dict, Any
from skyguard.ingestion.base import BaseDataAdapter
from skyguard.ingestion.provenance import DataProvenance


class IMDAWSAdapter(BaseDataAdapter):
    """Adapter for India Meteorological Department (IMD) AWS portal data.
    Supports official CSV exports from https://dsp.imdpune.gov.in/ and http://aws.imd.gov.in/
    """

    def __init__(self):
        super().__init__(source_type=DataProvenance.IMD_AWS)

    def load(self, source_path_or_url: Union[str, Path, Dict[str, Any]]) -> pd.DataFrame:
        if isinstance(source_path_or_url, (str, Path)):
            path = Path(source_path_or_url)
            if not path.exists():
                raise FileNotFoundError(f"IMD AWS data file not found: {path}")
            df = pd.read_csv(path)
        elif isinstance(source_path_or_url, dict):
            df = pd.DataFrame(source_path_or_url)
        else:
            raise TypeError("Source must be a filepath or dict")

        # Map typical IMD column variations to canonical names
        column_mapping = {
            "DateTime": "timestamp",
            "DATETIME": "timestamp",
            "Date_Time": "timestamp",
            "TIME": "timestamp",
            "Station_ID": "station_id",
            "STATION_ID": "station_id",
            "STN_ID": "station_id",
            "STNID": "station_id",
            "LAT": "latitude",
            "Latitude": "latitude",
            "LON": "longitude",
            "Longitude": "longitude",
            "ALT": "elevation",
            "Elevation": "elevation",
            "TEMP": "temperature",
            "Temperature": "temperature",
            "TEMP_C": "temperature",
            "PRESS": "pressure",
            "Pressure": "pressure",
            "SLP": "pressure",
            "PRES_HPA": "pressure",
            "RH": "relative_humidity",
            "Humidity": "relative_humidity",
            "RH_PCT": "relative_humidity"
        }
        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
        
        self.validate_schema(df)
        return self.standardize(df)

    def validate_schema(self, df: pd.DataFrame) -> bool:
        required = ["timestamp", "station_id", "temperature", "pressure", "relative_humidity"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"IMD AWS data is missing required meteorological columns: {missing}")
        if "latitude" not in df.columns:
            df["latitude"] = 20.5937 # Center of India default if not in table
        if "longitude" not in df.columns:
            df["longitude"] = 78.9629
        return True
