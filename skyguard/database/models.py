"""SQLAlchemy / TimescaleDB schema definitions and repositories for SkyGuard AI."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, Boolean, DateTime, JSON, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()


class StationModel(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, nullable=True)
    provenance = Column(String(32), default="IMD_AWS")
    status = Column(String(32), default="HEALTHY")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ObservationModel(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    station_id = Column(String(64), ForeignKey("stations.station_id"), nullable=False, index=True)
    
    # Raw Sensors
    raw_temperature = Column(Float, nullable=True)
    raw_pressure = Column(Float, nullable=True)
    raw_relative_humidity = Column(Float, nullable=True)
    
    # Validated / Self-Healed Imputed Stream
    validated_temperature = Column(Float, nullable=True)
    validated_pressure = Column(Float, nullable=True)
    validated_relative_humidity = Column(Float, nullable=True)
    is_imputed = Column(Boolean, default=False)
    imputation_confidence = Column(Float, nullable=True)
    
    # Derived Physics
    dew_point = Column(Float, nullable=True)
    vpd = Column(Float, nullable=True)
    potential_temperature = Column(Float, nullable=True)
    
    # AI Scores
    anomaly_score = Column(Float, default=0.0)
    classification = Column(String(64), default="NORMAL")
    severity = Column(String(32), default="LOW")
    provenance = Column(String(32), default="IMD_AWS")
    
    __table_args__ = (
        Index("idx_station_time", "station_id", "timestamp"),
    )


class AnomalyEventModel(Base):
    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(64), unique=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    station_id = Column(String(64), nullable=False)
    fault_type = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)
    confidence = Column(Float, nullable=False)
    explanation_json = Column(JSON, nullable=True)
    status = Column(String(32), default="ACTIVE")


class SensorHealthModel(Base):
    __tablename__ = "sensor_health"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    station_id = Column(String(64), nullable=False, index=True)
    overall_score = Column(Float, nullable=False)
    temp_health = Column(Float, nullable=False)
    press_health = Column(Float, nullable=False)
    rh_health = Column(Float, nullable=False)
    health_state = Column(String(32), nullable=False)
    maintenance_risk = Column(String(32), nullable=False)
    action_recommendation = Column(String(256), nullable=True)


class DatabaseRepository:
    """Manages SQLite / PostgreSQL / TimescaleDB session life-cycles."""

    def __init__(self, db_url: str = "sqlite:///skyguard/data/skyguard.db"):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()
