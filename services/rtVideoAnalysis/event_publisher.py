import logging
import json
import uuid
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self, bootstrap_servers, topic):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )

    def publish_fire_detected(self, cctv_id, facility_id, equipment_location,
                              detection_confidence, detection_area, description):
        """
        Publish fire detected event

        Args:
            cctv_id: CCTV camera identifier
            facility_id: Facility identifier
            equipment_location: Equipment location
            detection_confidence: Detection confidence (0-100)
            detection_area: Area where fire was detected
            description: Detection description
        """
        try:
            event = {
                'version': 1,
                'event_id': str(uuid.uuid4()),
                'facility_id': facility_id,
                'equipment_location': equipment_location,
                'detection_confidence': detection_confidence,
                'detection_timestamp': datetime.utcnow().isoformat() + 'Z',
                'cctv_id': cctv_id,
                'detection_area': detection_area,
                'description': description
            }

            # Use CCTV ID as key for partitioning
            future = self.producer.send(self.topic, key=cctv_id, value=event)

            # Wait for send to complete
            record_metadata = future.get(timeout=10)

            logger.info(f"Fire detected event published: {event['event_id']} "
                        f"to topic {record_metadata.topic} "
                        f"partition {record_metadata.partition} "
                        f"offset {record_metadata.offset}")

            return True

        except KafkaError as e:
            logger.error(f"Failed to publish fire detected event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing event: {e}")
            return False

    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")
