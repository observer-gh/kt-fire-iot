import enum
from datetime import datetime
from typing import Optional, Dict, Any

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

class Realtime:
    def __init__(self, 
                 equipment_data_id: str,
                 equipment_id: str,
                 facility_id: str,
                 equipment_location: str,
                 measured_at: datetime,
                 temperature: Optional[float] = None,
                 humidity: Optional[float] = None,
                 smoke_density: Optional[float] = None,
                 co_level: Optional[float] = None,
                 gas_level: Optional[float] = None,
                 version: int = 1):
        self.equipment_data_id = equipment_data_id
        self.equipment_id = equipment_id
        self.facility_id = facility_id
        self.equipment_location = equipment_location
        self.measured_at = measured_at
        self.temperature = temperature
        self.humidity = humidity
        self.smoke_density = smoke_density
        self.co_level = co_level
        self.gas_level = gas_level
        self.version = version
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database operations"""
        return {
            'equipment_data_id': self.equipment_data_id,
            'equipment_id': self.equipment_id,
            'facility_id': self.facility_id,
            'equipment_location': self.equipment_location,
            'measured_at': self.measured_at,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'smoke_density': self.smoke_density,
            'co_level': self.co_level,
            'gas_level': self.gas_level,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Realtime':
        """Create instance from dictionary"""
        return cls(
            equipment_data_id=data['equipment_data_id'],
            equipment_id=data['equipment_id'],
            facility_id=data['facility_id'],
            equipment_location=data['equipment_location'],
            measured_at=data['measured_at'],
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            smoke_density=data.get('smoke_density'),
            co_level=data.get('co_level'),
            gas_level=data.get('gas_level'),
            version=data.get('version', 1)
        )

class Alert:
    def __init__(self,
                 alert_id: str,
                 equipment_id: str,
                 facility_id: str,
                 equipment_location: str,
                 alert_type: AlertTypeEnum,
                 severity: SeverityEnum,
                 status: str,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 resolved_at: Optional[datetime] = None,
                 version: int = 1):
        self.alert_id = alert_id
        self.equipment_id = equipment_id
        self.facility_id = facility_id
        self.equipment_location = equipment_location
        self.alert_type = alert_type
        self.severity = severity
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.resolved_at = resolved_at
        self.version = version
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database operations"""
        return {
            'alert_id': self.alert_id,
            'equipment_id': self.equipment_id,
            'facility_id': self.facility_id,
            'equipment_location': self.equipment_location,
            'alert_type': self.alert_type.value,
            'severity': self.severity.value,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'resolved_at': self.resolved_at,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alert':
        """Create instance from dictionary"""
        return cls(
            alert_id=data['alert_id'],
            equipment_id=data['equipment_id'],
            facility_id=data['facility_id'],
            equipment_location=data['equipment_location'],
            alert_type=AlertTypeEnum(data['alert_type']),
            severity=SeverityEnum(data['severity']),
            status=data['status'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            resolved_at=data.get('resolved_at'),
            version=data.get('version', 1)
        )
