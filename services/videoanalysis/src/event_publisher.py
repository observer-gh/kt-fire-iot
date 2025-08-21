import json
import uuid
from datetime import datetime
from typing import Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger
from .config import Config


class EventPublisher:
    """Kafka event publisher for fire detection events"""

    def __init__(self):
        """Initialize Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda x: json.dumps(x).encode('utf-8'),
                key_serializer=lambda x: x.encode('utf-8') if x else None
            )
            logger.info(
                f"Kafka producer initialized with servers: {Config.KAFKA_BOOTSTRAP_SERVERS}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.producer = None

    def publish_fire_detected(self,
                              cctv_id: str,
                              facility_id: str,
                              equipment_location: str,
                              detection_confidence: int,
                              detection_area: str,
                              description: str) -> bool:
        """
        Publish fire detected event to Kafka

        Args:
            cctv_id: CCTV camera identifier
            facility_id: Facility identifier
            equipment_location: Equipment location
            detection_confidence: Detection confidence percentage
            detection_area: Area where fire was detected
            description: Human readable description

        Returns:
            bool: Success status
        """
        if not self.producer:
            logger.error("Kafka producer not available")
            return False

        try:
            # Create fire detected event
            event = {
                "eventId": str(uuid.uuid4()),
                "eventType": "FireDetected",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": Config.SERVICE_NAME,
                "data": {
                    "cctvId": cctv_id,
                    "facilityId": facility_id,
                    "equipmentLocation": equipment_location,
                    "detectionConfidence": detection_confidence,
                    "detectionArea": detection_area,
                    "description": description,
                    "detectionMethod": "azure_computer_vision"
                }
            }

            # Send to Kafka
            future = self.producer.send(
                Config.FIRE_DETECTED_TOPIC,
                key=cctv_id,
                value=event
            )

            # Wait for send to complete (with timeout)
            record_metadata = future.get(timeout=10)

            logger.info(f"Fire event published - Topic: {record_metadata.topic}, "
                        f"Partition: {record_metadata.partition}, "
                        f"Offset: {record_metadata.offset}")

            return True

        except KafkaError as e:
            logger.error(f"Kafka error publishing fire event: {e}")
            return False
        except Exception as e:
            logger.error(f"Error publishing fire event: {e}")
            return False

    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")

    def is_available(self) -> bool:
        """Check if Kafka producer is available"""
        return self.producer is not None
