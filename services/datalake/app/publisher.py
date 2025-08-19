import json
import logging
from typing import Optional
from kafka import KafkaProducer
from .models import ProcessedSensorData, DataLakeEvent

logger = logging.getLogger(__name__)


class KafkaPublisher:
    """Publishes processed sensor data to Kafka topics"""

    def __init__(self, bootstrap_servers: str = "kafka:29092"):
        self.bootstrap_servers = bootstrap_servers
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

    def publish_sensor_data(self, processed_data: ProcessedSensorData) -> bool:
        """Publish processed sensor data to Kafka"""
        if not self.producer:
            logger.error("Kafka producer not connected")
            return False

        try:
            # Create event
            event = DataLakeEvent(
                event_type="sensor.data.processed",
                data=processed_data
            )

            # Determine topic based on data type
            topic = self._get_topic(processed_data)

            # Publish to Kafka
            future = self.producer.send(
                topic=topic,
                key=processed_data.station_id,
                value=event.dict()
            )

            # Wait for send to complete
            record_metadata = future.get(timeout=10)

            logger.info(f"Published to {topic}: station={processed_data.station_id}, "
                        f"value={processed_data.value}, alert={processed_data.is_alert}")

            return True

        except Exception as e:
            logger.error(f"Failed to publish to Kafka: {e}")
            return False

    def _get_topic(self, data: ProcessedSensorData) -> str:
        """Determine Kafka topic based on data type"""
        if data.is_alert:
            return "fire-iot.alerts"
        else:
            return "fire-iot.sensor-data"

    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")
