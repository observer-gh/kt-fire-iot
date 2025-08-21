#!/usr/bin/env python3
"""
Test consumer for controlTower.fireDetectionNotified events
This script tests the fire detection consumer locally
"""

import asyncio
import logging
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.fire_detection_consumer import fire_detection_consumer, start_fire_detection_consumer, get_recent_fire_events
from app.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_consumer():
    """Test the fire detection consumer"""
    print("🔥 Testing Fire Detection Consumer")
    print("=" * 50)
    print(f"Kafka Servers: {settings.kafka_bootstrap_servers}")
    print(f"Topic: {settings.kafka_topic_fire_detection}")
    print(f"EventHub Connection: {'✅ Configured' if settings.eventhub_connection_string else '❌ Not configured'}")
    print(f"Config file check: kafka_bootstrap_servers = '{settings.kafka_bootstrap_servers}'")
    print(f"Config file check: kafka_topic_fire_detection = '{settings.kafka_topic_fire_detection}'")
    print("-" * 50)
    
    try:
        # Start the consumer
        print("🚀 Starting fire detection consumer...")
        await start_fire_detection_consumer()
        
        print("✅ Consumer started! Waiting for messages...")
        print("💡 Run the producer script in another terminal:")
        print("   python test_fire_detection_producer.py")
        print("\n🔍 Monitoring for events (Ctrl+C to stop)...")
        
        # Monitor for events
        event_count = 0
        while True:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            # Get recent events
            events = await get_recent_fire_events(limit=10)
            
            if len(events) > event_count:
                new_events = events[:len(events) - event_count]
                for event in new_events:
                    print(f"\n🔥 NEW EVENT RECEIVED:")
                    print(f"   Alert ID: {event.alert_id}")
                    print(f"   Incident: {event.incident_id}")
                    print(f"   Severity: {event.severity}")
                    print(f"   Type: {event.alert_type}")
                    print(f"   Facility: {event.facility_id}")
                    print(f"   Description: {event.description}")
                    print(f"   Confidence: {event.detection_confidence}%")
                    print("-" * 40)
                
                event_count = len(events)
                print(f"📊 Total events received: {event_count}")
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping consumer...")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Consumer error")
    finally:
        await fire_detection_consumer.stop()
        print("✅ Consumer stopped")

async def test_event_store():
    """Test the event store functionality"""
    print("\n🔍 Testing Event Store...")
    
    # Get all events
    all_events = await get_recent_fire_events()
    print(f"📊 Total events in store: {len(all_events)}")
    
    if all_events:
        # Test filtering by severity
        emergency_events = await get_recent_fire_events()
        emergency_events = [e for e in emergency_events if e.severity == "EMERGENCY"]
        print(f"🚨 EMERGENCY events: {len(emergency_events)}")
        
        # Show recent events
        print("\n📋 Recent events:")
        for i, event in enumerate(all_events[:3]):
            print(f"  {i+1}. {event.alert_id[:8]}... | {event.severity} | {event.alert_type}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--store-only":
        # Just test the event store
        asyncio.run(test_event_store())
    else:
        # Test the full consumer
        asyncio.run(test_consumer())

if __name__ == "__main__":
    main()
