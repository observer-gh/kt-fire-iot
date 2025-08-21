import json
import logging
import asyncio
from typing import Optional, List
from datetime import datetime, timedelta
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Optional Azure EventHub imports for cloud deployment
try:
    from azure.eventhub.aio import EventHubConsumerClient
    from azure.eventhub.extensions.checkpointstoreblob.aio import BlobCheckpointStore
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    EventHubConsumerClient = None
    BlobCheckpointStore = None

from .models import FireDetectionNotifiedEvent
from .config import settings

logger = logging.getLogger(__name__)


class FireDetectionEventStore:
    """In-memory store for fire detection events"""
    
    def __init__(self, max_events: int = 100):
        self.events: List[FireDetectionNotifiedEvent] = []
        self.max_events = max_events
        self._lock = asyncio.Lock()
    
    async def add_event(self, event: FireDetectionNotifiedEvent):
        """Add a new fire detection event"""
        async with self._lock:
            self.events.insert(0, event)  # Add to front
            if len(self.events) > self.max_events:
                self.events = self.events[:self.max_events]  # Keep only recent events
            logger.info(f"🔥 Fire detection event stored: {event.alert_id} - {event.description}")
    
    async def get_recent_events(self, limit: int = 50) -> List[FireDetectionNotifiedEvent]:
        """Get recent fire detection events"""
        async with self._lock:
            return self.events[:limit]
    
    async def get_events_by_facility(self, facility_id: str, limit: int = 50) -> List[FireDetectionNotifiedEvent]:
        """Get events for a specific facility"""
        async with self._lock:
            filtered_events = [e for e in self.events if e.facility_id == facility_id]
            return filtered_events[:limit]
    
    async def get_events_by_severity(self, severity: str, limit: int = 50) -> List[FireDetectionNotifiedEvent]:
        """Get events by severity level"""
        async with self._lock:
            filtered_events = [e for e in self.events if e.severity == severity]
            return filtered_events[:limit]


class FireDetectionConsumer:
    """Consumer for fire detection events from Kafka/EventHub"""
    
    def __init__(self):
        self.event_store = FireDetectionEventStore()
        self.consumer = None
        self.eventhub_client = None
        self.is_running = False
        
    async def start_kafka_consumer(self):
        """Start Kafka consumer for local development"""
        try:
            self.consumer = KafkaConsumer(
                settings.kafka_topic_fire_detection,
                bootstrap_servers=settings.kafka_bootstrap_servers.split(','),
                auto_offset_reset='earliest',  # Start from earliest messages to catch existing ones
                enable_auto_commit=True,
                group_id='datalake-dashboard-fire-detection',
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=1000,  # Timeout for polling
                api_version=(0, 10, 1),  # Explicit API version
                security_protocol='PLAINTEXT'
            )
            
            logger.info(f"🔥 Started Kafka consumer for {settings.kafka_topic_fire_detection}")
            logger.info(f"🔥 Kafka servers: {settings.kafka_bootstrap_servers}")
            logger.info(f"🔥 Consumer group: datalake-dashboard-fire-detection")
            self.is_running = True
            
            # Start consuming in background
            asyncio.create_task(self._consume_kafka_messages())
            
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            raise
    
    async def start_eventhub_consumer(self):
        """Start Event Hub consumer for Azure cloud deployment"""
        if not AZURE_AVAILABLE:
            logger.warning("Azure EventHub libraries not available, skipping EventHub consumer")
            return
            
        if not settings.eventhub_connection_string:
            logger.warning("Event Hub connection string not configured, skipping EventHub consumer")
            return
            
        try:
            # For Event Hub, we need to extract the Event Hub name from topic
            eventhub_name = settings.kafka_topic_fire_detection
            
            self.eventhub_client = EventHubConsumerClient.from_connection_string(
                conn_str=settings.eventhub_connection_string,
                consumer_group=settings.eventhub_consumer_group,
                eventhub_name=eventhub_name
            )
            
            logger.info(f"🔥 Started EventHub consumer for {eventhub_name}")
            self.is_running = True
            
            # Start consuming in background
            asyncio.create_task(self._consume_eventhub_messages())
            
        except Exception as e:
            logger.error(f"Failed to start EventHub consumer: {e}")
            raise
    
    async def _consume_kafka_messages(self):
        """Background task to consume Kafka messages"""
        logger.info("🔍 Starting Kafka message consumption loop...")
        while self.is_running:
            try:
                # Poll for messages with timeout
                message_pack = self.consumer.poll(timeout_ms=1000)
                
                if message_pack:
                    logger.info(f"📨 Received {len(message_pack)} message batches")
                    for topic_partition, messages in message_pack.items():
                        logger.info(f"📨 Processing {len(messages)} messages from {topic_partition}")
                        for message in messages:
                            await self._process_message(message.value)
                else:
                    # No messages received, just continue polling
                    await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                        
            except KafkaError as e:
                logger.error(f"Kafka error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
            except Exception as e:
                logger.error(f"Error consuming Kafka messages: {e}")
                logger.exception("Full exception details:")
                await asyncio.sleep(1)
    
    async def _consume_eventhub_messages(self):
        """Background task to consume EventHub messages"""
        try:
            async with self.eventhub_client:
                await self.eventhub_client.receive(
                    on_event=self._on_eventhub_event,
                    starting_position="-1"  # Start from latest
                )
        except Exception as e:
            logger.error(f"Error consuming EventHub messages: {e}")
    
    async def _on_eventhub_event(self, partition_context, event):
        """Handle EventHub event"""
        try:
            # Event Hub events are in bytes, decode to string then parse JSON
            event_data = json.loads(event.body_as_str())
            await self._process_message(event_data)
            
            # Update checkpoint
            await partition_context.update_checkpoint(event)
            
        except Exception as e:
            logger.error(f"Error processing EventHub event: {e}")
    
    async def _process_message(self, message_data: dict):
        """Process a fire detection message"""
        try:
            # Parse the message into our model
            event = FireDetectionNotifiedEvent(**message_data)
            
            # Store the event
            await self.event_store.add_event(event)
            
            logger.info(f"🔥 Processed fire detection event: {event.alert_id} - Severity: {event.severity}")
            
        except Exception as e:
            logger.error(f"Error processing fire detection message: {e}")
            logger.debug(f"Message data: {message_data}")
    
    async def stop(self):
        """Stop the consumer"""
        self.is_running = False
        
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer stopped")
        
        if self.eventhub_client:
            await self.eventhub_client.close()
            logger.info("EventHub consumer stopped")


# Global instance
fire_detection_consumer = FireDetectionConsumer()


async def start_fire_detection_consumer():
    """Start the appropriate consumer based on configuration"""
    try:
        if settings.eventhub_connection_string and AZURE_AVAILABLE:
            # Cloud deployment - use EventHub
            await fire_detection_consumer.start_eventhub_consumer()
        else:
            # Local deployment - use Kafka
            await fire_detection_consumer.start_kafka_consumer()
            
    except Exception as e:
        logger.error(f"Failed to start fire detection consumer: {e}")


async def get_recent_fire_events(limit: int = 50) -> List[FireDetectionNotifiedEvent]:
    """Get recent fire detection events"""
    return await fire_detection_consumer.event_store.get_recent_events(limit)


async def get_fire_events_by_facility(facility_id: str, limit: int = 50) -> List[FireDetectionNotifiedEvent]:
    """Get fire detection events for a specific facility"""
    return await fire_detection_consumer.event_store.get_events_by_facility(facility_id, limit)


async def get_fire_events_by_severity(severity: str, limit: int = 50) -> List[FireDetectionNotifiedEvent]:
    """Get fire detection events by severity"""
    return await fire_detection_consumer.event_store.get_events_by_severity(severity, limit)
