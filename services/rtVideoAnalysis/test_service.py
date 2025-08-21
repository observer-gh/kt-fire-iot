#!/usr/bin/env python3
"""
Test script for RtVideoAnalysis service
Tests with mock Azure Vision API and sample images
"""

from event_publisher import EventPublisher
from azure_vision_client import AzureVisionClient
from config import Config
import os
import sys
import time
import logging
from unittest.mock import Mock, patch
from PIL import Image
import numpy as np

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockAzureVisionClient:
    """Mock Azure Vision client for testing"""

    def __init__(self, endpoint, key):
        self.endpoint = endpoint
        self.key = key

    def detect_fire(self, image_data):
        """Mock fire detection - randomly detects fire"""
        import random

        # Simulate API call delay
        time.sleep(0.1)

        # Random fire detection (30% chance)
        if random.random() < 0.3:
            confidence = random.randint(70, 95)
            return {
                'detected': True,
                'confidence': confidence,
                'objects': ['fire', 'flame'],
                'tags': ['burning', 'smoke']
            }
        else:
            return {
                'detected': False,
                'confidence': 0,
                'objects': ['chair', 'table'],
                'tags': ['indoor', 'room']
            }


class MockEventPublisher:
    """Mock event publisher for testing"""

    def __init__(self, bootstrap_servers, topic):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.published_events = []

    def publish_fire_detected(self, cctv_id, facility_id, equipment_location,
                              detection_confidence, detection_area, description):
        """Mock event publishing"""
        event = {
            'cctv_id': cctv_id,
            'facility_id': facility_id,
            'equipment_location': equipment_location,
            'detection_confidence': detection_confidence,
            'detection_area': detection_area,
            'description': description,
            'timestamp': time.time()
        }

        self.published_events.append(event)
        logger.info(f"Mock event published: {event}")
        return True

    def close(self):
        logger.info("Mock event publisher closed")


def create_sample_image(width=640, height=480):
    """Create a sample image for testing"""
    # Create a simple image with some random content
    img_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    return Image.fromarray(img_array)


def test_azure_vision_client():
    """Test Azure Vision client with mock"""
    logger.info("Testing Azure Vision client...")

    with patch('azure_vision_client.AzureVisionClient', MockAzureVisionClient):
        client = AzureVisionClient("mock-endpoint", "mock-key")

        # Test with sample image
        sample_image = create_sample_image()
        result = client.detect_fire(sample_image)

        logger.info(f"Detection result: {result}")
        assert 'detected' in result
        assert 'confidence' in result

        logger.info("✅ Azure Vision client test passed")


def test_event_publisher():
    """Test event publisher with mock"""
    logger.info("Testing event publisher...")

    with patch('event_publisher.KafkaProducer'):
        publisher = EventPublisher("localhost:9092", "test-topic")

        # Test event publishing
        success = publisher.publish_fire_detected(
            cctv_id="test_cctv",
            facility_id="test_facility",
            equipment_location="test_location",
            detection_confidence=85,
            detection_area="center",
            description="Test fire detection"
        )

        assert success == True
        logger.info("✅ Event publisher test passed")


def test_mock_integration():
    """Test integration with mock components"""
    logger.info("Testing mock integration...")

    # Create mock components
    mock_vision = MockAzureVisionClient("mock-endpoint", "mock-key")
    mock_publisher = MockEventPublisher("localhost:9092", "test-topic")

    # Test multiple detections
    for i in range(5):
        sample_image = create_sample_image()
        result = mock_vision.detect_fire(sample_image)

        if result['detected'] and result['confidence'] >= 70:
            mock_publisher.publish_fire_detected(
                cctv_id=f"cctv_{i:03d}",
                facility_id=f"facility_{i:03d}",
                equipment_location="test_area",
                detection_confidence=result['confidence'],
                detection_area="full_frame",
                description=f"Test fire detection {i}"
            )

    logger.info(f"Published {len(mock_publisher.published_events)} events")
    logger.info("✅ Mock integration test passed")


def test_config():
    """Test configuration loading"""
    logger.info("Testing configuration...")

    config = Config()

    # Test required fields
    assert hasattr(config, 'AZURE_VISION_ENDPOINT')
    assert hasattr(config, 'KAFKA_BOOTSTRAP_SERVERS')
    assert hasattr(config, 'CCTV_STREAMS')

    logger.info(f"Config loaded: {len(config.CCTV_STREAMS)} CCTV streams")
    logger.info("✅ Configuration test passed")


def main():
    """Run all tests"""
    logger.info("Starting RtVideoAnalysis service tests...")

    try:
        test_config()
        test_azure_vision_client()
        test_event_publisher()
        test_mock_integration()

        logger.info("🎉 All tests passed!")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
