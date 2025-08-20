import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from .database import execute_query, execute_many
from .db_models import Realtime, Alert
from .models import ProcessedSensorData
from .config import settings
from .storage_interface import StorageInterface

logger = logging.getLogger(__name__)

class StorageService(StorageInterface):
    """Handles data storage and batch upload operations for production"""
    
    def __init__(self):
        self.batch_size = settings.batch_size
        self.batch_interval = settings.batch_interval_minutes
        self.storage_path = settings.storage_path
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
        logger.info(f"StorageService initialized with path: {self.storage_path}")
        logger.info(f"Batch size: {self.batch_size}, Interval: {self.batch_interval} minutes")
    
    def save_sensor_data(self, processed_data: ProcessedSensorData) -> bool:
        """Save processed sensor data to database"""
        try:
            # Create realtime record
            realtime_record = Realtime(
                equipment_data_id=str(uuid.uuid4())[:10],
                equipment_id=processed_data.equipment_id,
                facility_id=processed_data.facility_id,
                equipment_location=processed_data.equipment_location,
                measured_at=processed_data.measured_at,
                temperature=processed_data.temperature,
                humidity=processed_data.humidity,
                smoke_density=processed_data.smoke_density,
                co_level=processed_data.co_level,
                gas_level=processed_data.gas_level,
                version=1
            )
            
            # Insert realtime data
            insert_realtime_query = """
            INSERT INTO realtime (
                equipment_data_id, equipment_id, facility_id, equipment_location,
                measured_at, temperature, humidity, smoke_density, co_level, gas_level, version
            ) VALUES (
                %(equipment_data_id)s, %(equipment_id)s, %(facility_id)s, %(equipment_location)s,
                %(measured_at)s, %(temperature)s, %(humidity)s, %(smoke_density)s, %(co_level)s, %(gas_level)s, %(version)s
            )
            """
            execute_query(insert_realtime_query, realtime_record.to_dict(), fetch=False)
            
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
                
                insert_alert_query = """
                INSERT INTO alert (
                    alert_id, equipment_id, facility_id, equipment_location,
                    alert_type, severity, status, created_at, updated_at, version
                ) VALUES (
                    %(alert_id)s, %(equipment_id)s, %(facility_id)s, %(equipment_location)s,
                    %(alert_type)s, %(severity)s, %(status)s, %(created_at)s, %(updated_at)s, %(version)s
                )
                """
                execute_query(insert_alert_query, alert_record.to_dict(), fetch=False)
            
            logger.info(f"Saved sensor data for equipment {processed_data.equipment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save sensor data: {e}")
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
        # This is a simplified logic - you might want to make this more sophisticated
        if metric == "temperature" and value >= 95:
            return "EMERGENCY"
        elif metric in ["smoke_density", "co_level", "gas_level"] and value >= 500:
            return "EMERGENCY"
        else:
            return "WARN"
    
    def should_upload_batch(self) -> bool:
        """Check if it's time to upload a batch of data"""
        try:
            # Check if we have enough data
            count_query = "SELECT COUNT(*) as count FROM realtime"
            result = execute_query(count_query)
            count = result[0]['count'] if result else 0
            
            if count < self.batch_size:
                return False
            
            # Check if enough time has passed since last upload
            # This is a simplified check - you might want to track last upload time
            return True
            
        except Exception as e:
            logger.error(f"Error checking batch upload condition: {e}")
            return False
    
    def upload_batch_to_storage(self) -> Optional[str]:
        """Upload a batch of data to storage and return file path"""
        try:
            # Get batch of data
            batch_query = "SELECT * FROM realtime LIMIT %s"
            batch_data = execute_query(batch_query, (self.batch_size,))
            
            if not batch_data:
                logger.info("No data to upload")
                return None
            
            # Convert to list of dictionaries
            data_list = []
            for record in batch_data:
                data_dict = {
                    "equipment_data_id": record['equipment_data_id'],
                    "equipment_id": record['equipment_id'],
                    "facility_id": record['facility_id'],
                    "equipment_location": record['equipment_location'],
                    "measured_at": record['measured_at'].isoformat() if record['measured_at'] else None,
                    "ingested_at": record['ingested_at'].isoformat() if record['ingested_at'] else None,
                    "temperature": float(record['temperature']) if record['temperature'] else None,
                    "humidity": float(record['humidity']) if record['humidity'] else None,
                    "smoke_density": float(record['smoke_density']) if record['smoke_density'] else None,
                    "co_level": float(record['co_level']) if record['co_level'] else None,
                    "gas_level": float(record['gas_level']) if record['gas_level'] else None,
                    "version": record['version']
                }
                data_list.append(data_dict)
            
            # Generate filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"sensor_data_batch_{timestamp}.json"
            filepath = os.path.join(self.storage_path, filename)
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump({
                    "batch_id": str(uuid.uuid4()),
                    "uploaded_at": datetime.utcnow().isoformat(),
                    "record_count": len(data_list),
                    "storage_type": "production",
                    "data": data_list
                }, f, indent=2)
            
            logger.info(f"Uploaded batch to storage: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to upload batch to storage: {e}")
            return None
    
    def cleanup_uploaded_data(self, filepath: str) -> bool:
        """Clean up data that has been uploaded to storage"""
        try:
            # Read the uploaded file to get record IDs
            with open(filepath, 'r') as f:
                batch_info = json.load(f)
            
            # Extract equipment_data_ids
            equipment_data_ids = [record["equipment_data_id"] for record in batch_info["data"]]
            
            # Delete from database
            placeholders = ','.join(['%s'] * len(equipment_data_ids))
            delete_query = f"DELETE FROM realtime WHERE equipment_data_id IN ({placeholders})"
            
            deleted_count = execute_query(delete_query, equipment_data_ids, fetch=False)
            
            logger.info(f"Cleaned up {deleted_count} records after upload")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup uploaded data: {e}")
            return False
