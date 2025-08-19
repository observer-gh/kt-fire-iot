from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SensorType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    SMOKE = "smoke"
    CO2 = "co2"
    PRESSURE = "pressure"


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RawSensorData(BaseModel):
    """Raw data received from external API"""
    station_id: str
    sensor_type: SensorType
    value: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ProcessedSensorData(BaseModel):
    """Cleaned and processed sensor data"""
    station_id: str
    sensor_type: SensorType
    value: float
    timestamp: datetime
    is_alert: bool = False
    severity: Optional[AlertSeverity] = None
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class DataLakeEvent(BaseModel):
    """Event published to Kafka"""
    event_type: str
    data: ProcessedSensorData
    source: str = "datalake"
    version: str = "1.0.0"
