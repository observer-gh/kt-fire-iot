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

class StorageMetadata:
    """스토리지 flush 메타데이터를 저장하는 클래스"""
    
    def __init__(self,
                 metadata_id: str,
                 flush_timestamp: datetime,
                 data_start_time: datetime,
                 data_end_time: datetime,
                 record_count: int,
                 storage_path: str,
                 storage_type: str,
                 file_size_bytes: Optional[int] = None,
                 compression_ratio: Optional[float] = None,
                 processing_duration_ms: Optional[int] = None,
                 error_count: int = 0,
                 success_count: int = 0,
                 additional_info: Optional[Dict[str, Any]] = None,
                 created_at: Optional[datetime] = None):
        self.metadata_id = metadata_id
        self.flush_timestamp = flush_timestamp
        self.data_start_time = data_start_time
        self.data_end_time = data_end_time
        self.record_count = record_count
        self.storage_path = storage_path
        self.storage_type = storage_type
        self.file_size_bytes = file_size_bytes
        self.compression_ratio = compression_ratio
        self.processing_duration_ms = processing_duration_ms
        self.error_count = error_count
        self.success_count = success_count
        self.additional_info = additional_info or {}
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database operations"""
        return {
            'metadata_id': self.metadata_id,
            'flush_timestamp': self.flush_timestamp,
            'data_start_time': self.data_start_time,
            'data_end_time': self.data_end_time,
            'record_count': self.record_count,
            'storage_path': self.storage_path,
            'storage_type': self.storage_type,
            'file_size_bytes': self.file_size_bytes,
            'compression_ratio': self.compression_ratio,
            'processing_duration_ms': self.processing_duration_ms,
            'error_count': self.error_count,
            'success_count': self.success_count,
            'additional_info': self.additional_info,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StorageMetadata':
        """Create instance from dictionary"""
        return cls(
            metadata_id=data['metadata_id'],
            flush_timestamp=data['flush_timestamp'],
            data_start_time=data['data_start_time'],
            data_end_time=data['data_end_time'],
            record_count=data['record_count'],
            storage_path=data['storage_path'],
            storage_type=data['storage_type'],
            file_size_bytes=data.get('file_size_bytes'),
            compression_ratio=data.get('compression_ratio'),
            processing_duration_ms=data.get('processing_duration_ms'),
            error_count=data.get('error_count', 0),
            success_count=data.get('success_count', 0),
            additional_info=data.get('additional_info', {}),
            created_at=data.get('created_at')
        )

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
