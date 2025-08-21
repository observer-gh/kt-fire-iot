import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid

from .database import execute_query, execute_many
from .db_models import Realtime, Alert, StorageMetadata
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
    
    def save_storage_metadata(self, metadata: StorageMetadata) -> bool:
        """Save storage metadata to PostgreSQL database"""
        try:
            # additional_info를 JSON 문자열로 변환
            metadata_dict = metadata.to_dict()
            if metadata_dict.get('additional_info'):
                import json
                metadata_dict['additional_info'] = json.dumps(metadata_dict['additional_info'])
            
            insert_metadata_query = """
            INSERT INTO storage_metadata (
                metadata_id, flush_timestamp, data_start_time, data_end_time,
                record_count, storage_path, storage_type, file_size_bytes,
                compression_ratio, processing_duration_ms, error_count,
                success_count, additional_info, created_at
            ) VALUES (
                %(metadata_id)s, %(flush_timestamp)s, %(data_start_time)s, %(data_end_time)s,
                %(record_count)s, %(storage_path)s, %(storage_type)s, %(file_size_bytes)s,
                %(compression_ratio)s, %(processing_duration_ms)s, %(error_count)s,
                %(success_count)s, %(additional_info)s, %(created_at)s
            )
            """
            execute_query(insert_metadata_query, metadata_dict, fetch=False)
            logger.info(f"Storage metadata saved successfully: {metadata.metadata_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save storage metadata: {e}")
            return False
    
    def create_flush_metadata(self, 
                            data_list: List[ProcessedSensorData],
                            storage_path: str,
                            processing_start_time: datetime,
                            processing_end_time: datetime,
                            error_count: int = 0,
                            success_count: int = 0,
                            additional_info: Optional[Dict[str, Any]] = None) -> StorageMetadata:
        """Redis flush 시 메타데이터를 생성합니다"""
        
        # 파일 크기 계산
        file_size_bytes = None
        try:
            if os.path.exists(storage_path):
                file_size_bytes = os.path.getsize(storage_path)
        except Exception as e:
            logger.warning(f"Could not get file size: {e}")
        
        # 처리 시간 계산 (밀리초)
        processing_duration_ms = int((processing_end_time - processing_start_time).total_seconds() * 1000)
        
        # 데이터 시간 범위 계산
        if data_list:
            data_start_time = min(data.measured_at for data in data_list if data.measured_at)
            data_end_time = max(data.measured_at for data in data_list if data.measured_at)
        else:
            data_start_time = processing_start_time
            data_end_time = processing_end_time
        
        metadata = StorageMetadata(
            metadata_id=str(uuid.uuid4()),
            flush_timestamp=processing_end_time,
            data_start_time=data_start_time,
            data_end_time=data_end_time,
            record_count=len(data_list),
            storage_path=storage_path,
            storage_type="redis_flush",
            file_size_bytes=file_size_bytes,
            processing_duration_ms=processing_duration_ms,
            error_count=error_count,
            success_count=success_count,
            additional_info=additional_info or {}
        )
        
        return metadata
    
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
                try:
                    # anomaly_value를 안전하게 처리
                    anomaly_value = processed_data.anomaly_value
                    if hasattr(anomaly_value, 'value'):
                        # 객체인 경우 value 속성 사용
                        anomaly_value = anomaly_value.value
                    elif isinstance(anomaly_value, str):
                        # 문자열인 경우 그대로 사용
                        pass
                    else:
                        # 기타 타입인 경우 문자열로 변환
                        anomaly_value = str(anomaly_value)
                    
                    alert_record = Alert(
                        alert_id=str(uuid.uuid4())[:10],
                        equipment_id=processed_data.equipment_id,
                        facility_id=processed_data.facility_id,
                        equipment_location=processed_data.equipment_location,
                        alert_type=self._get_alert_type(processed_data.anomaly_metric),
                        severity=self._get_severity(processed_data.anomaly_metric, anomaly_value),
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
                    logger.info(f"Alert created for equipment {processed_data.equipment_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to create alert for equipment {processed_data.equipment_id}: {e}")
                    # 알림 생성 실패는 센서 데이터 저장을 막지 않음
            
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
