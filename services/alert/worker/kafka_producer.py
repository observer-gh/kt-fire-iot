import json
import logging
from typing import Dict, Any
from kafka import KafkaProducer
from .config import settings

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        logger.info("Kafka producer initialized")

    def publish_alert_success(self, alert_id: str, channel: str = "slack", recipient: str = None):
        """Publish alert success event to Kafka"""
        try:
            event = {
                "version": 1,
                "alert_id": alert_id,
                "channel": channel,
                "recipient": recipient,
                "sent_at": self._get_current_timestamp()
            }
            
            self.producer.send(
                settings.kafka_alert_success_topic,
                key=alert_id,
                value=event
            )
            logger.info(f"Published alert success event for alert_id: {alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish alert success event: {e}")

    def publish_alert_fail(self, alert_id: str, channel: str = "slack", error_code: str = "SLACK_ERROR", error_message: str = None):
        """Publish alert failure event to Kafka"""
        try:
            event = {
                "version": 1,
                "alert_id": alert_id,
                "channel": channel,
                "error_code": error_code,
                "error_message": error_message,
                "failed_at": self._get_current_timestamp()
            }
            
            self.producer.send(
                settings.kafka_alert_fail_topic,
                key=alert_id,
                value=event
            )
            logger.info(f"Published alert failure event for alert_id: {alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish alert failure event: {e}")

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

    def close(self):
        """Close the Kafka producer"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")
