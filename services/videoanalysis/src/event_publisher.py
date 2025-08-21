import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger
from .config import Config

# Import Azure Event Hub client only if available
try:
    from azure.eventhub import EventHubProducerClient, EventData
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.warning(
        "Azure Event Hub client not available. Install azure-eventhub for cloud support.")


class EventPublisher:
    """Event publisher supporting both Kafka (local) and Azure Event Hub (cloud)"""

    def __init__(self):
        """Initialize event publisher based on environment"""
        self.environment = Config.ENVIRONMENT
        self.producer = None
        self.eventhub_client = None

        if self.environment == 'local':
            self._init_kafka_producer()
        else:
            self._init_eventhub_client()

    def _init_kafka_producer(self):
        """Initialize Kafka producer for local development"""
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

    def _init_eventhub_client(self):
        """Initialize Azure Event Hub client for cloud deployment"""
        if not AZURE_AVAILABLE:
            logger.error(
                "Azure Event Hub client not available. Cannot initialize for cloud environment.")
            return

        if not Config.EVENTHUB_CONN:
            logger.error(
                "EVENTHUB_CONNECTION_STRING not provided. Check EVENTHUB_CONN environment variable.")
            logger.info(
                "Available environment variables: EVENTHUB_CONNECTION_STRING, EVENTHUB_CONN")
            return

        try:
            self.eventhub_client = EventHubProducerClient.from_connection_string(
                Config.EVENTHUB_CONN,
                eventhub_name=Config.EVENTHUB_FIRE_DETECTED_TOPIC
            )
            logger.info("Azure Event Hub client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Event Hub client: {e}")
            self.eventhub_client = None

    def publish_fire_detected(self,
                              cctv_id: str,
                              facility_id: str,
                              equipment_location: str,
                              detection_confidence: int,
                              detection_area: str,
                              description: str) -> bool:
        """
        Publish fire detected event to Kafka or Event Hub

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

        if self.environment == 'local':
            return self._publish_to_kafka(event, cctv_id)
        else:
            return self._publish_to_eventhub(event)

    def _publish_to_kafka(self, event: dict, key: str) -> bool:
        """Publish event to Kafka"""
        if not self.producer:
            logger.error("Kafka producer not available")
            return False

        try:
            future = self.producer.send(
                Config.FIRE_DETECTED_TOPIC,
                key=key,
                value=event
            )

            # Wait for send to complete (with timeout)
            record_metadata = future.get(timeout=10)

            logger.info(f"Fire event published to Kafka - Topic: {record_metadata.topic}, "
                        f"Partition: {record_metadata.partition}, "
                        f"Offset: {record_metadata.offset}")

            return True

        except KafkaError as e:
            logger.error(f"Kafka error publishing fire event: {e}")
            return False
        except Exception as e:
            logger.error(f"Error publishing fire event to Kafka: {e}")
            return False

    def _publish_to_eventhub(self, event: dict) -> bool:
        """Publish event to Azure Event Hub"""
        if not self.eventhub_client:
            logger.error("Event Hub client not available")
            return False

        try:
            # Create Event Hub event data
            event_data = EventData(json.dumps(event))

            # Send to Event Hub
            with self.eventhub_client:
                event_data_batch = self.eventhub_client.create_batch()
                event_data_batch.add(event_data)
                self.eventhub_client.send_batch(event_data_batch)

            logger.info(
                f"Fire event published to Event Hub - Topic: {Config.EVENTHUB_FIRE_DETECTED_TOPIC}")
            return True

        except Exception as e:
            logger.error(f"Error publishing fire event to Event Hub: {e}")
            return False

    def close(self):
        """Close event publisher"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")
        if self.eventhub_client:
            self.eventhub_client.close()
            logger.info("Event Hub client closed")

    def is_available(self) -> bool:
        """Check if event publisher is available"""
        if self.environment == 'local':
            return self.producer is not None
        else:
            return self.eventhub_client is not None
