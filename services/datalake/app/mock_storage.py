import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from .storage_interface import StorageInterface
from .db_models import Realtime, Alert
from .models import ProcessedSensorData

logger = logging.getLogger(__name__)

class MockStorage(StorageInterface):
    """Mock storage service for local testing - stores data in local filesystem"""
    
    def __init__(self, local_storage_path: str = "./local_storage"):
        self.batch_size = int(os.getenv("BATCH_SIZE", "100"))
        self.batch_interval = int(os.getenv("BATCH_INTERVAL_MINUTES", "10"))
        self.local_storage_path = local_storage_path
        
        # Ensure local storage directory exists
        os.makedirs(self.local_storage_path, exist_ok=True)
        
        # Track uploaded batches for testing
        self.uploaded_batches: List[Dict] = []
        
        logger.info(f"MockStorage initialized with local path: {self.local_storage_path}")
        logger.info(f"Batch size: {self.batch_size}, Interval: {self.batch_interval} minutes")
    
    def save_sensor_data(self, db: Session, processed_data: ProcessedSensorData) -> bool:
        """Save processed sensor data to database (same as real storage)"""
        try:
            # Create realtime record
            realtime_record = Realtime(
                equipment_data_id=str(uuid.uuid4())[:10],
                equipment_id=processed_data.equipment_id,
                facility_id=processed_data.facility_id,
                equipment_location=processed_data.equipment_location,
                measured_at=processed_data.measured_at,
                ingested_at=processed_data.ingested_at,
                temperature=processed_data.temperature,
                humidity=processed_data.humidity,
                smoke_density=processed_data.smoke_density,
                co_level=processed_data.co_level,
                gas_level=processed_data.gas_level,
                version=1
            )
            
            db.add(realtime_record)
            
            # Create alert record if anomaly detected
            if processed_data.is_anomaly:
                alert_record = Alert(
                    alert_id=str(uuid.uuid4())[:10],
                    equipment_id=processed_data.equipment_id,
                    facility_id=processed_data.facility_id,
                    equipment_location=processed_data.equipment_location,
                    alert_type=self._get_alert_type(processed_data.anomaly_metric),
                    severity=self._get_severity(processed_data.anomaly_metric, processed_data.anomaly_value),
                    status="ACTIVE",
                    created_at=datetime.utcnow(),
                    version=1
                )
                db.add(alert_record)
            
            db.commit()
            logger.info(f"[MOCK] Saved sensor data for equipment {processed_data.equipment_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"[MOCK] Failed to save sensor data: {e}")
            return False
    
    def _get_alert_type(self, metric: str) -> str:
        """Map metric to alert type"""
        metric_map = {
            "temperature": "HEAT",
            "humidity": "CUSTOM",
            "smoke_density": "SMOKE",
            "co_level": "CO",
            "gas_level": "GAS"
        }
        return metric_map.get(metric, "CUSTOM")
    
    def _get_severity(self, metric: str, value: float) -> str:
        """Determine severity based on metric and value"""
        if metric == "temperature" and value >= 95:
            return "EMERGENCY"
        elif metric in ["smoke_density", "co_level", "gas_level"] and value >= 500:
            return "EMERGENCY"
        else:
            return "WARN"
    
    def should_upload_batch(self, db: Session) -> bool:
        """Check if batch upload is needed (smaller batch size for testing)"""
        try:
            count = db.query(func.count(Realtime.equipment_data_id)).scalar()
            should_upload = count >= self.batch_size
            
            if should_upload:
                logger.info(f"[MOCK] Batch upload condition met: {count} >= {self.batch_size}")
            
            return should_upload
            
        except Exception as e:
            logger.error(f"[MOCK] Error checking batch upload condition: {e}")
            return False
    
    def upload_batch_to_storage(self, db: Session) -> Optional[str]:
        """Upload a batch of data to local storage and return file path"""
        try:
            # Get batch of data
            batch_data = db.query(Realtime).limit(self.batch_size).all()
            
            if not batch_data:
                logger.info("[MOCK] No data to upload")
                return None
            
            # Convert to list of dictionaries
            data_list = []
            for record in batch_data:
                data_dict = {
                    "equipment_data_id": record.equipment_data_id,
                    "equipment_id": record.equipment_id,
                    "facility_id": record.facility_id,
                    "equipment_location": record.equipment_location,
                    "measured_at": record.measured_at.isoformat() if record.measured_at else None,
                    "ingested_at": record.ingested_at.isoformat() if record.ingested_at else None,
                    "temperature": float(record.temperature) if record.temperature else None,
                    "humidity": float(record.humidity) if record.humidity else None,
                    "smoke_density": float(record.smoke_density) if record.smoke_density else None,
                    "co_level": float(record.co_level) if record.co_level else None,
                    "gas_level": float(record.gas_level) if record.gas_level else None,
                    "version": record.version
                }
                data_list.append(data_dict)
            
            # Generate filename with timestamp
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"mock_sensor_data_batch_{timestamp}.json"
            filepath = os.path.join(self.local_storage_path, filename)
            
            # Create batch info
            batch_info = {
                "batch_id": str(uuid.uuid4()),
                "uploaded_at": datetime.utcnow().isoformat(),
                "record_count": len(data_list),
                "storage_type": "mock_local",
                "data": data_list
            }
            
            # Write to local file
            with open(filepath, 'w') as f:
                json.dump(batch_info, f, indent=2)
            
            # Track uploaded batch for testing purposes
            self.uploaded_batches.append({
                "filepath": filepath,
                "batch_info": batch_info,
                "uploaded_at": datetime.utcnow()
            })
            
            logger.info(f"[MOCK] Uploaded batch to local storage: {filepath}")
            logger.info(f"[MOCK] Batch contains {len(data_list)} records")
            
            return filepath
            
        except Exception as e:
            logger.error(f"[MOCK] Failed to upload batch to local storage: {e}")
            return None
    
    def cleanup_uploaded_data(self, db: Session, filepath: str) -> bool:
        """Clean up data that has been uploaded to storage"""
        try:
            # Read the uploaded file to get record IDs
            with open(filepath, 'r') as f:
                batch_info = json.load(f)
            
            # Extract equipment_data_ids
            equipment_data_ids = [record["equipment_data_id"] for record in batch_info["data"]]
            
            # Delete from database
            deleted_count = db.query(Realtime).filter(
                Realtime.equipment_data_id.in_(equipment_data_ids)
            ).delete(synchronize_session=False)
            
            db.commit()
            logger.info(f"[MOCK] Cleaned up {deleted_count} records after upload")
            
            # Remove from tracking list
            self.uploaded_batches = [b for b in self.uploaded_batches if b["filepath"] != filepath]
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"[MOCK] Failed to cleanup uploaded data: {e}")
            return False
    
    def get_uploaded_batches(self) -> List[Dict]:
        """Get list of uploaded batches for testing purposes"""
        return self.uploaded_batches
    
    def clear_uploaded_batches(self):
        """Clear uploaded batches tracking (for testing)"""
        self.uploaded_batches.clear()
        logger.info("[MOCK] Cleared uploaded batches tracking")
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics for testing"""
        return {
            "local_storage_path": self.local_storage_path,
            "batch_size": self.batch_size,
            "batch_interval_minutes": self.batch_interval,
            "uploaded_batches_count": len(self.uploaded_batches),
            "total_records_uploaded": sum(b["batch_info"]["record_count"] for b in self.uploaded_batches)
        }
