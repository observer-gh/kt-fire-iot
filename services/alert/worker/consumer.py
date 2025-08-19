import asyncio
import json
import logging
from typing import Callable, Dict, Any
from kafka import KafkaConsumer
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub import EventData
from .config import settings

logger = logging.getLogger(__name__)


class MessageConsumer:
    def __init__(self, message_handler: Callable[[Dict[str, Any]], None]):
        self.message_handler = message_handler
        self.running = False

    async def start(self):
        """Start consuming messages based on environment"""
        self.running = True

        if settings.environment == "local":
            await self._start_kafka_consumer()
        else:
            await self._start_azure_consumer()

    async def _start_kafka_consumer(self):
        """Start Kafka consumer for local development"""
        logger.info("Starting Kafka consumer...")

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

    async def _start_azure_consumer(self):
        """Start Azure Event Hubs consumer for cloud environments"""
        if not settings.azure_eventhub_connection_string:
            raise ValueError(
                "Azure Event Hubs connection string not configured")

        logger.info("Starting Azure Event Hubs consumer...")

        client = EventHubConsumerClient.from_connection_string(
            settings.azure_eventhub_connection_string,
            settings.azure_eventhub_consumer_group
        )

        async def on_event(partition_context, event: EventData):
            try:
                message_data = json.loads(event.body_as_str())
                logger.info(
                    f"Received message from partition {partition_context.partition_id}: {message_data}")
                self.message_handler(message_data)
                await partition_context.update_checkpoint(event)
            except Exception as e:
                logger.error(f"Error processing Azure Event Hubs message: {e}")

        try:
            async with client:
                await client.receive(
                    on_event=on_event,
                    track_last_enqueued_event_properties=True,
                    starting_position="-1"
                )
        except Exception as e:
            logger.error(f"Azure Event Hubs consumer error: {e}")

    async def stop(self):
        """Stop the consumer"""
        self.running = False
        logger.info("Message consumer stopped")
