from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, Text, Enum
from sqlalchemy.sql import func
from .database import Base
import enum

class SeverityEnum(str, enum.Enum):
    INFO = "INFO"
    WARN = "WARN"
    EMERGENCY = "EMERGENCY"

class AlertTypeEnum(str, enum.Enum):
    SMOKE = "SMOKE"
    GAS = "GAS"
    CO = "CO"
    HEAT = "HEAT"
    POWER = "POWER"
    COMM = "COMM"
    CUSTOM = "CUSTOM"

class Realtime(Base):
    __tablename__ = "realtime"
    
    equipment_data_id = Column(String(10), primary_key=True)
    equipment_id = Column(String(10))
    facility_id = Column(String(10))
    equipment_location = Column(String(40))
    measured_at = Column(DateTime)
    ingested_at = Column(DateTime, default=func.now())
    temperature = Column(DECIMAL(6, 2))
    humidity = Column(DECIMAL(5, 2))
    smoke_density = Column(DECIMAL(6, 3))
    co_level = Column(DECIMAL(6, 3))
    gas_level = Column(DECIMAL(6, 3))
    version = Column(Integer, default=1)

class Alert(Base):
    __tablename__ = "alert"
    
    alert_id = Column(String(10), primary_key=True)
    equipment_id = Column(String(10))
    facility_id = Column(String(10))
    equipment_location = Column(String(40))
    alert_type = Column(Enum(AlertTypeEnum))
    severity = Column(Enum(SeverityEnum))
    status = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime)
    version = Column(Integer, default=1)
