import asyncio
import json
import logging
from typing import Callable, Dict, Any
from kafka import KafkaConsumer
from .config import settings

logger = logging.getLogger(__name__)


class MessageConsumer:
    def __init__(self, message_handler: Callable[[Dict[str, Any]], None]):
        self.message_handler = message_handler
        self.running = False

    async def start(self):
        """Start consuming messages based on environment"""
        self.running = True

        # Azure 환경인지 확인 (보안 프로토콜이 SASL_SSL인 경우)
        if settings.kafka_security_protocol == 'SASL_SSL' and settings.azure_eventhub_connection_string:
            await self._start_azure_kafka_consumer()
        else:
            await self._start_local_kafka_consumer()

    async def _start_local_kafka_consumer(self):
        """Start Kafka consumer for local development"""
        logger.info("Starting local Kafka consumer...")
        logger.info(f"Connecting to Kafka at: {settings.kafka_bootstrap_servers}")

        consumer = KafkaConsumer(
            settings.kafka_warning_topic,
            settings.kafka_emergency_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_group_id,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        try:
            for message in consumer:
                if not self.running:
                    break

                try:
                    logger.info(
                        f"Received message from topic {message.topic}: {message.value}")
                    self.message_handler(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Kafka consumer error: {e}")
        finally:
            consumer.close()

    async def _start_azure_kafka_consumer(self):
        """Start Azure Event Hub consumer using Kafka compatible mode"""
        if not settings.azure_eventhub_connection_string:
            raise ValueError(
                "Azure Event Hubs connection string not configured")

        logger.info("Starting Azure Event Hub Kafka consumer...")
        logger.info(f"Connecting to Azure Event Hub at: {settings.kafka_bootstrap_servers}")

        try:
            # Azure Event Hub용 Kafka consumer 설정
            consumer_config = {
                'bootstrap_servers': settings.kafka_bootstrap_servers,
                'group_id': settings.kafka_group_id,
                'auto_offset_reset': 'earliest',
                'enable_auto_commit': True,
                'security_protocol': settings.kafka_security_protocol,
                'sasl_mechanism': settings.kafka_sasl_mechanism,
                'sasl_plain_username': settings.kafka_sasl_username,
                'value_deserializer': lambda m: json.loads(m.decode('utf-8'))
            }
            
            # SASL 비밀번호 설정 (Azure Event Hub 연결 문자열 사용)
            if settings.kafka_sasl_password:
                consumer_config['sasl_plain_password'] = settings.kafka_sasl_password
            else:
                consumer_config['sasl_plain_password'] = settings.azure_eventhub_connection_string

            consumer = KafkaConsumer(
                settings.kafka_warning_topic,
                settings.kafka_emergency_topic,
                **consumer_config
            )
            
            logger.info(f"Successfully connected to Azure Event Hub at {settings.kafka_bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Azure Event Hub: {e}")
            return

        try:
            for message in consumer:
                if not self.running:
                    break

                try:
                    logger.info(
                        f"Received message from topic {message.topic}: {message.value}")
                    self.message_handler(message.value)
                except Exception as e:
                    logger.error(f"Azure Event Hub Kafka consumer error: {e}")

        except Exception as e:
            logger.error(f"Azure Event Hub Kafka consumer error: {e}")
        finally:
            consumer.close()

    async def stop(self):
        """Stop the consumer"""
        self.running = False
        logger.info("Message consumer stopped")
