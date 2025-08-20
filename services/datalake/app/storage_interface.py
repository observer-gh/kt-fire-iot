from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session
from .models import ProcessedSensorData

class StorageInterface(ABC):
    """Abstract base class for storage operations"""
    
    @abstractmethod
    def save_sensor_data(self, db: Session, processed_data: ProcessedSensorData) -> bool:
        """Save processed sensor data to storage"""
        pass
    
    @abstractmethod
    def should_upload_batch(self, db: Session) -> bool:
        """Check if batch upload is needed"""
        pass
    
    @abstractmethod
    def upload_batch_to_storage(self, db: Session) -> Optional[str]:
        """Upload a batch of data to storage and return file path"""
        pass
    
    @abstractmethod
    def cleanup_uploaded_data(self, db: Session, filepath: str) -> bool:
        """Clean up data that has been uploaded to storage"""
        pass
