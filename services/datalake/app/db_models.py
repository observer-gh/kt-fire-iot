from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, Text, Enum
from sqlalchemy.sql import func
from .database import Base
import enum

class SeverityEnum(str, enum.Enum):
    INFO = "INFO"
    WARN = "WARN"
    EMERGENCY = "EMERGENCY"

class MaintenanceTypeEnum(str, enum.Enum):
    INSPECTION = "INSPECTION"
    REPAIR = "REPAIR"
    REPLACE = "REPLACE"
    CLEAN = "CLEAN"
    CALIBRATE = "CALIBRATE"
    OTHER = "OTHER"

class AlertTypeEnum(str, enum.Enum):
    SMOKE = "SMOKE"
    GAS = "GAS"
    CO = "CO"
    HEAT = "HEAT"
    POWER = "POWER"
    COMM = "COMM"
    CUSTOM = "CUSTOM"

class Facility(Base):
    __tablename__ = "facility"
    
    facility_id = Column(String(10), primary_key=True)
    address = Column(String(30))
    internal_address = Column(String(10))
    facility_type = Column(String(10))
    manager_name = Column(String(20))
    manager_phone = Column(String(20))
    risk_level = Column(String(20))
    active_alerts_count = Column(Integer)
    online_sensors_count = Column(Integer)
    total_sensors_count = Column(Integer)
    updated_at = Column(DateTime, default=func.now())
    version = Column(Integer, default=1)

class Equipment(Base):
    __tablename__ = "equipment"
    
    equipment_id = Column(String(10), primary_key=True)
    equipment_location = Column(String(40))
    facility_id = Column(String(10), nullable=False)
    equipment_type = Column(String(10))
    status_code = Column(String(10))
    created_at = Column(DateTime, default=func.now())
    installed_at = Column(DateTime)
    expired_at = Column(DateTime)
    version = Column(Integer, default=1)

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

class Incident(Base):
    __tablename__ = "incident"
    
    incident_id = Column(String(10), primary_key=True)
    facility_id = Column(String(10), nullable=False)
    incident_type = Column(String(10))
    severity = Column(Enum(SeverityEnum))
    created_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime)
    report_file_name = Column(String(20))
    description = Column(Text)
    version = Column(Integer, default=1)

class Analysis(Base):
    __tablename__ = "analysis"
    
    analysis_id = Column(String(20), primary_key=True)
    facility_id = Column(String(10), nullable=False)
    incident_id = Column(String(20))
    analysis_type = Column(String(20))
    confidence_score = Column(DECIMAL(5, 4))
    risk_probability = Column(DECIMAL(5, 4))
    status = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    report_file_name = Column(String(40))
    version = Column(Integer, default=1)

class EquipmentMaintenance(Base):
    __tablename__ = "equipment_maintanence"
    
    maintenance_log_id = Column(String(255), primary_key=True)
    equiment_id = Column(String(10), nullable=False)
    facility_id = Column(String(10))
    equipment_location = Column(String(40))
    maintenance_type = Column(Enum(MaintenanceTypeEnum))
    scheduled_date = Column(DateTime)
    performed_date = Column(DateTime)
    manager = Column(String(10))
    status_code = Column(String(10))
    next_scheduled_date = Column(DateTime)
    note = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    version = Column(Integer, default=1)
