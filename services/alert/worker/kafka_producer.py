import json
import logging
from typing import Dict, Any
from kafka import KafkaProducer
from .config import settings

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    def __init__(self):
        self.producer = None
        self._connect()

    def _connect(self):
        """Connect to Kafka broker or Azure Event Hub"""
        try:
            # Check if we're in Azure cloud environment
            if settings.azure_eventhub_connection_string:
                # Azure Event Hub connection (Kafka compatible mode)
                self.producer = KafkaProducer(
                    bootstrap_servers=settings.kafka_bootstrap_servers,
                    security_protocol='SASL_SSL',
                    sasl_mechanism='PLAIN',
                    sasl_plain_username='$ConnectionString',
                    sasl_plain_password=settings.azure_eventhub_connection_string,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None
                )
                logger.info(f"Connected to Azure Event Hub at {settings.kafka_bootstrap_servers}")
            else:
                # Local Kafka connection
                self.producer = KafkaProducer(
                    bootstrap_servers=settings.kafka_bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None
                )
                logger.info(f"Connected to local Kafka at {settings.kafka_bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka/Event Hub: {e}")
            self.producer = None

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
