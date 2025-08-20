from abc import ABC, abstractmethod
from typing import Optional
from .models import ProcessedSensorData

class StorageInterface(ABC):
    """Abstract base class for storage operations"""
    
    @abstractmethod
    def save_sensor_data(self, processed_data: ProcessedSensorData) -> bool:
        """Save processed sensor data to storage"""
        pass
    
    @abstractmethod
    def should_upload_batch(self) -> bool:
        """Check if batch upload is needed"""
        pass
    
    @abstractmethod
    def upload_batch_to_storage(self) -> Optional[str]:
        """Upload a batch of data to storage"""
        pass
    
    @abstractmethod
    def cleanup_uploaded_data(self, filepath: str) -> bool:
        """Clean up data that has been uploaded"""
        pass
