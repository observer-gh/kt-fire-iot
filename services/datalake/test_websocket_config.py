#!/usr/bin/env python3
"""Test script to verify websocket configuration for datalake service"""

import os
import sys
sys.path.append('app')

from app.config import settings

def test_config():
    """Test the websocket configuration"""
    print("=== Datalake WebSocket Configuration Test ===")
    print(f"Environment: {settings.environment}")
    print(f"Mock Server Host: {settings.mock_server_host}")
    print(f"Mock Server Port: {settings.mock_server_port}")
    print(f"WebSocket URL: {settings.video_websocket_url}")
    print(f"Stream Subscription: {settings.video_stream_subscription}")
    print(f"Control Destination: {settings.video_control_destination}")
    print()

def test_environment_switching():
    """Test environment switching"""
    print("=== Environment Switching Test ===")
    
    # Test local environment
    os.environ['PROFILE'] = 'local'
    os.environ['MOCK_SERVER_HOST'] = 'localhost'
    os.environ['MOCK_SERVER_PORT'] = '8001'
    
    # Reload settings
    from app.config import Settings
    local_settings = Settings()
    print(f"Local environment URL: {local_settings.video_websocket_url}")
    
    # Test cloud environment
    os.environ['PROFILE'] = 'cloud'
    os.environ['MOCK_SERVER_HOST'] = 'my-app.azurewebsites.net'
    
    cloud_settings = Settings()
    print(f"Cloud environment URL: {cloud_settings.video_websocket_url}")
    print()

if __name__ == "__main__":
    test_config()
    test_environment_switching()
    print("✅ Configuration test completed successfully!")
