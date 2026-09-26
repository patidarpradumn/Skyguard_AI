"""Generic CSV & Parquet Ingestion Adapter for SkyGuard AI."""

import pandas as pd
from pathlib import Path
from typing import Union, Dict, Any
from skyguard.ingestion.base import BaseDataAdapter
from skyguard.ingestion.provenance import DataProvenance


class CSVParquetAdapter(BaseDataAdapter):
    """Adapter for generic tabular CSV or Parquet observation datasets."""

    def __init__(self, provenance: DataProvenance = DataProvenance.EXTERNAL_CSV):
        super().__init__(source_type=provenance)

    def load(self, source_path: Union[str, Path]) -> pd.DataFrame:
        path = Path(source_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        else:
            df = pd.read_csv(path)

        self.validate_schema(df)
        return self.standardize(df)

    def validate_schema(self, df: pd.DataFrame) -> bool:
        required = ["timestamp", "station_id", "temperature", "pressure", "relative_humidity"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Generic dataset missing required core columns: {missing}")
        if "latitude" not in df.columns:
            df["latitude"] = 0.0
        if "longitude" not in df.columns:
            df["longitude"] = 0.0
        return True
