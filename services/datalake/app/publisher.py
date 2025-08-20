import json
import logging
import uuid
from typing import Optional
from datetime import datetime
from kafka import KafkaProducer
from .models import (
    ProcessedSensorData, 
    DataLakeEvent, 
    SensorDataSavedEvent, 
    SensorDataAnomalyDetectedEvent
)
from .config import settings

logger = logging.getLogger(__name__)


class KafkaPublisher:
    """Publishes events to Kafka topics for ControlTower service"""

    def __init__(self, bootstrap_servers: Optional[str] = None):
        self.bootstrap_servers = bootstrap_servers or settings.kafka_bootstrap_servers
        self.producer = None
        self._connect()

    def _connect(self):
        """Connect to Kafka broker"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(
                    v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            self.producer = None

    def publish_anomaly_detected(self, processed_data: ProcessedSensorData) -> bool:
        """Publish anomaly detected event to ControlTower"""
        if not self.producer:
            logger.error("Kafka producer not connected")
            return False

        try:
            # Create anomaly event
            anomaly_event = SensorDataAnomalyDetectedEvent(
                event_id=str(uuid.uuid4()),
                equipment_id=processed_data.equipment_id,
                facility_id=processed_data.facility_id,
                metric=processed_data.anomaly_metric,
                value=processed_data.anomaly_value,
                threshold=processed_data.anomaly_threshold,
                measured_at=processed_data.measured_at,
                detected_at=datetime.utcnow()
            )

            # Publish to Kafka
            future = self.producer.send(
                topic=settings.kafka_topic_anomaly,
                key=processed_data.equipment_id,
                value=anomaly_event.dict()
            )

            # Wait for send to complete
            record_metadata = future.get(timeout=10)

            logger.info(f"Published anomaly event: equipment={processed_data.equipment_id}, "
                        f"metric={processed_data.anomaly_metric}, value={processed_data.anomaly_value}")

            return True

        except Exception as e:
            logger.error(f"Failed to publish anomaly event: {e}")
            return False

    def publish_data_saved(self, processed_data: ProcessedSensorData, filepath: str) -> bool:
        """Publish data saved event to ControlTower
        
        This method is called ONLY when sensor data is flushed from Redis to local storage.
        It should NOT be called for real-time data ingestion.
        
        Args:
            processed_data: The processed sensor data that was saved
            filepath: Path or identifier where data was saved (e.g., "redis_flush", "batch_upload")
        """
        if not self.producer:
            logger.error("Kafka producer not connected")
            return False

        try:
            # Create data saved event
            data_saved_event = SensorDataSavedEvent(
                event_id=str(uuid.uuid4()),
                equipment_id=processed_data.equipment_id,
                facility_id=processed_data.facility_id,
                equipment_location=processed_data.equipment_location,
                measured_at=processed_data.measured_at,
                temperature=processed_data.temperature,
                humidity=processed_data.humidity,
                smoke_density=processed_data.smoke_density,
                co_level=processed_data.co_level,
                gas_level=processed_data.gas_level,
                ingested_at=processed_data.ingested_at
            )

            # Publish to Kafka
            future = self.producer.send(
                topic=settings.kafka_topic_data_saved,
                key=processed_data.equipment_id,
                value=data_saved_event.dict()
            )

            # Wait for send to complete
            record_metadata = future.get(timeout=10)

            logger.info(f"Published data saved event: equipment={processed_data.equipment_id}, "
                        f"filepath={filepath}")

            return True

        except Exception as e:
            logger.error(f"Failed to publish data saved event: {e}")
            return False

    def publish_sensor_data(self, processed_data: ProcessedSensorData) -> bool:
        """Publish processed sensor data to Kafka (legacy method)
        
        NOTE: This method should NOT be used for real-time sensor data.
        Use publish_data_saved() instead, which is called during Redis flush operations.
        This method is kept for backward compatibility only.
        """
        if not self.producer:
            logger.error("Kafka producer not connected")
            return False

        try:
            # Create event
            event = DataLakeEvent(
                event_type="sensor.data.processed",
                data=processed_data.dict()
            )

            # Publish to Kafka
            future = self.producer.send(
                topic=settings.kafka_topic_sensor_data,
                key=processed_data.equipment_id,
                value=event.dict()
            )

            # Wait for send to complete
            record_metadata = future.get(timeout=10)

            logger.info(f"Published sensor data: equipment={processed_data.equipment_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to publish sensor data: {e}")
            return False

    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")
