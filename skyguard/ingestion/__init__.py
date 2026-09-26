"""Data Ingestion module for SkyGuard AI."""

from skyguard.ingestion.provenance import DataProvenance, ObservationSchema
from skyguard.ingestion.base import BaseDataAdapter
from skyguard.ingestion.imd import IMDAWSAdapter
from skyguard.ingestion.noaa import NOAAISDAdapter
from skyguard.ingestion.era5 import ERA5Adapter
from skyguard.ingestion.csv_parquet import CSVParquetAdapter
from skyguard.ingestion.synthetic import SyntheticAWSGenerator

__all__ = [
    "DataProvenance",
    "ObservationSchema",
    "BaseDataAdapter",
    "IMDAWSAdapter",
    "NOAAISDAdapter",
    "ERA5Adapter",
    "CSVParquetAdapter",
    "SyntheticAWSGenerator"
]
