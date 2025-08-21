#!/usr/bin/env python3
"""
Test script for Azure Vision client
"""
import os
import sys
from PIL import Image
from src.config import Config
from src.azure_vision_client import AzureVisionClient


def test_azure_vision():
    """Test Azure Vision client with sample image"""

    # Load config
    config = Config()

    # Check if credentials are available
    if not config.AZURE_VISION_ENDPOINT or not config.AZURE_VISION_KEY:
        print("❌ Error: AZURE_VISION_ENDPOINT and AZURE_VISION_KEY must be set in .env")
        print("Please check your .env file")
        return False

    print(f"✅ Using endpoint: {config.AZURE_VISION_ENDPOINT}")
    print(f"✅ Key available: {'*' * 10}{config.AZURE_VISION_KEY[-4:]}")

    # Initialize client
    try:
        client = AzureVisionClient(
            config.AZURE_VISION_ENDPOINT, config.AZURE_VISION_KEY)
        print("✅ Azure Vision client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return False

        # Load test image
    try:
        test_image_path = "tests/office_fire.jpeg"
        if not os.path.exists(test_image_path):
            print(f"❌ Test image not found: {test_image_path}")
            return False

        test_image = Image.open(test_image_path)
        print(f"✅ Loaded test image: {test_image_path}")
        print(f"   Image size: {test_image.size}")

        # Test fire detection
        print("\n🔍 Testing fire detection...")
        result = client.detect_fire(test_image)

        print(f"📊 Detection Result:")
        print(f"   Detected: {result['detected']}")
        print(f"   Confidence: {result['confidence']}%")
        print(f"   Objects found: {result['objects']}")
        print(f"   Tags found: {result['tags']}")

        if 'error' in result:
            print(f"   Error: {result['error']}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing Azure Vision Client")
    print("=" * 40)

    success = test_azure_vision()

    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
