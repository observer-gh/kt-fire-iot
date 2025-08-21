from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SensorType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    SMOKE = "smoke"
    CO = "co"
    GAS = "gas"


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    EMERGENCY = "EMERGENCY"


class RawSensorData(BaseModel):
    """Raw data received from external API"""
    equipment_id: str
    facility_id: Optional[str] = None
    equipment_location: Optional[str] = None
    measured_at: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    smoke_density: Optional[float] = None
    co_level: Optional[float] = None
    gas_level: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class ProcessedSensorData(BaseModel):
    """Cleaned and processed sensor data"""
    equipment_id: str
    facility_id: Optional[str] = None
    equipment_location: Optional[str] = None
    measured_at: datetime
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    smoke_density: Optional[float] = None
    co_level: Optional[float] = None
    gas_level: Optional[float] = None
    is_anomaly: bool = False
    anomaly_metric: Optional[str] = None
    anomaly_value: Optional[float] = None
    anomaly_threshold: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class SensorDataSavedEvent(BaseModel):
    """Event sent to ControlTower when data is saved to storage"""
    version: int = 1
    event_id: str
    equipment_id: str
    facility_id: Optional[str] = None
    equipment_location: Optional[str] = None
    measured_at: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    smoke_density: Optional[float] = None
    co_level: Optional[float] = None
    gas_level: Optional[float] = None
    ingested_at: datetime


class SensorDataAnomalyDetectedEvent(BaseModel):
    """Event sent to ControlTower when anomaly is detected"""
    version: int = 1
    event_id: str
    equipment_id: str
    facility_id: Optional[str] = None
    metric: str
    value: float
    threshold: float
    rule_id: Optional[str] = None
    measured_at: str  # ISO format string for OffsetDateTime compatibility
    detected_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    severity: str = "WARN"  # Default severity level


class DataLakeEvent(BaseModel):
    """Event published to Kafka"""
    event_type: str
    data: Dict[str, Any]
    source: str = "datalake"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
