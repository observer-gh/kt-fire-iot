#!/usr/bin/env python3
"""
Test producer for controlTower.fireDetectionNotified events
This script sends test fire detection events to Kafka for local testing
"""

import json
import time
import uuid
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Test configuration
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"  # Local container port
TOPIC = "controlTower.fireDetectionNotified"

def create_test_fire_detection_event(severity="EMERGENCY", alert_type="SMOKE"):
    """Create a test fire detection event"""
    return {
        "version": 1,
        "alert_id": str(uuid.uuid4()),
        "incident_id": f"INC-{int(time.time())}",
        "facility_id": "FAC-001",
        "equipment_location": "Building A - Floor 2 - Room 201",
        "alert_type": alert_type,  # SMOKE, GAS, CO, HEAT, POWER, COMM, CUSTOM
        "severity": severity,  # INFO, WARN, EMERGENCY
        "status": "ACTIVE",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "description": f"Fire detected by {alert_type.lower()} sensor in Building A",
        "cctv_id": "CCTV-A2-201",
        "detection_confidence": 85
    }

def create_kafka_producer():
    """Create and return Kafka producer"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, indent=2).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        print(f"✅ Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
        return producer
    except Exception as e:
        print(f"❌ Failed to connect to Kafka: {e}")
        return None

def send_test_events(producer, count=5):
    """Send test fire detection events"""
    severities = ["INFO", "WARN", "EMERGENCY"]
    alert_types = ["SMOKE", "GAS", "CO", "HEAT"]
    
    print(f"\n🔥 Sending {count} test fire detection events to topic: {TOPIC}")
    print("-" * 60)
    
    for i in range(count):
        # Rotate through different severities and alert types
        severity = severities[i % len(severities)]
        alert_type = alert_types[i % len(alert_types)]
        
        event = create_test_fire_detection_event(severity, alert_type)
        
        try:
            # Send the event
            future = producer.send(TOPIC, value=event, key=event["alert_id"])
            result = future.get(timeout=10)  # Wait for confirmation
            
            print(f"✅ Event {i+1}: {event['alert_id'][:8]}... | {severity} | {alert_type}")
            print(f"   Partition: {result.partition}, Offset: {result.offset}")
            
        except KafkaError as e:
            print(f"❌ Failed to send event {i+1}: {e}")
        except Exception as e:
            print(f"❌ Error sending event {i+1}: {e}")
        
        # Small delay between messages
        time.sleep(1)

def main():
    print("🚀 Fire Detection Event Test Producer")
    print("=" * 50)
    
    # Create producer
    producer = create_kafka_producer()
    if not producer:
        return
    
    try:
        # Send test events
        send_test_events(producer, count=5)
        
        print("\n" + "=" * 50)
        print("✅ Test completed! Check:")
        print("1. Kafka UI at http://localhost:8080 for messages")
        print("2. DataLake dashboard consumer logs")
        print("3. Topic: controlTower.fireDetectionNotified")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if producer:
            producer.flush()
            producer.close()
            print("🔌 Producer closed")

if __name__ == "__main__":
    main()
