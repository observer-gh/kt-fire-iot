#!/usr/bin/env python3
"""
Test producer to send sample alert messages to Kafka topics
"""
import json
import time
import uuid
from datetime import datetime
from kafka import KafkaProducer

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
WARNING_TOPIC = 'WarningNotificationCreated'
EMERGENCY_TOPIC = 'EmergencyAlertTriggered'


def create_test_message(alert_type='warning', severity='MEDIUM'):
    """Create a test alert message"""
    if alert_type == 'emergency':
        event_type = "alert.emergency-alert-triggered"
    else:
        event_type = "alert.warning-notification-created"

    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "event_version": "v1",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "dedupe_key": f"station_001:{int(time.time())}:rule_001",
        "data": {
            "alert_id": str(uuid.uuid4()),
            "station_id": "station_001",
            "rule_id": "rule_001",
            "rule_name": f"{alert_type.title()} Alert Rule",
            "severity": severity,
            "message": f"This is a test {alert_type} alert message",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "location": {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "address": "123 Test Street",
                "building_name": "Test Building",
                "floor": "3",
                "room": "301"
            },
            "sensor_readings": {
                "temperature": 25.5,
                "humidity": 60.2,
                "smoke_level": 0.1 if alert_type == 'warning' else 0.8,
                "co_level": 0.05 if alert_type == 'warning' else 0.3
            },
            "metadata": {
                "test": True,
                "source": "test_producer"
            }
        }
    }


def main():
    """Send test messages to Kafka topics"""
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print("🚀 Starting test message producer...")
    print(f"📡 Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")

    try:
        # Send warning message
        warning_msg = create_test_message('warning', 'MEDIUM')
        producer.send(WARNING_TOPIC, warning_msg)
        print(f"⚠️  Sent warning message to {WARNING_TOPIC}")
        print(f"   Alert ID: {warning_msg['data']['alert_id']}")

        time.sleep(2)

        # Send emergency message
        emergency_msg = create_test_message('emergency', 'CRITICAL')
        producer.send(EMERGENCY_TOPIC, emergency_msg)
        print(f"🚨 Sent emergency message to {EMERGENCY_TOPIC}")
        print(f"   Alert ID: {emergency_msg['data']['alert_id']}")

        # Flush to ensure messages are sent
        producer.flush()
        print("✅ Test messages sent successfully!")

    except Exception as e:
        print(f"❌ Error sending messages: {e}")
    finally:
        producer.close()


if __name__ == "__main__":
    main()
