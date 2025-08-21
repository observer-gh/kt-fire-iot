#!/usr/bin/env python3
"""
Test script for video streaming WebSocket client
Tests connection to mock server and frame reception
"""

import sys
import os
import asyncio
import time
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.video_stream_client import StompVideoStreamClient, get_video_client, start_video_stream, get_video_stats
from app.video_models import CctvFrame
from app.config import settings

def frame_callback(frame: CctvFrame):
    """Callback function for received frames"""
    print(f"📹 Frame received: #{frame.frame_number} from {frame.video_file_name}")
    print(f"   Timestamp: {frame.timestamp}")
    print(f"   Image size: {len(frame.image_data)} chars")
    print(f"   Received at: {frame.received_at}")
    print("-" * 50)

def test_video_config():
    """Test video configuration"""
    print("🔧 Video Configuration Test")
    print("=" * 50)
    print(f"WebSocket URL: {settings.video_websocket_url}")
    print(f"Mock Server Host: {settings.mock_server_host}")
    print(f"Mock Server Port: {settings.mock_server_port}")
    print(f"Default Video: {settings.default_video_file}")
    print(f"Buffer Size: {settings.video_frame_buffer_size}")
    print(f"Stream Subscription: {settings.video_stream_subscription}")
    print(f"Control Destination: {settings.video_control_destination}")
    print("-" * 50)

def test_websocket_connection():
    """Test WebSocket connection without streaming"""
    print("\n🔌 WebSocket Connection Test")
    print("=" * 50)
    
    client = StompVideoStreamClient(on_frame_received=frame_callback)
    
    print("Attempting to connect...")
    success = client.connect()
    
    if success:
        print("✅ WebSocket connected successfully!")
        
        # Check connection state
        state = client.get_stream_state()
        print(f"Connected: {state.connected}")
        print(f"Streaming: {state.streaming}")
        
        # Wait a moment
        time.sleep(2)
        
        # Disconnect
        client.disconnect()
        print("✅ Disconnected successfully")
        return True
    else:
        print("❌ WebSocket connection failed!")
        state = client.get_stream_state()
        if state.error_message:
            print(f"Error: {state.error_message}")
        return False

def test_video_streaming():
    """Test full video streaming"""
    print("\n📹 Video Streaming Test")
    print("=" * 50)
    
    client = StompVideoStreamClient(on_frame_received=frame_callback)
    
    try:
        # Connect
        print("Connecting to WebSocket...")
        if not client.connect():
            print("❌ Failed to connect")
            return False
        
        print("✅ Connected! Starting video stream...")
        
        # Start streaming
        success = client.start_video_stream()
        if not success:
            print("❌ Failed to start video stream")
            return False
        
        print("✅ Video stream started! Waiting for frames...")
        print("(Will wait 30 seconds for frames, then stop)")
        
        # Wait for frames
        start_time = time.time()
        last_stats_time = start_time
        
        while time.time() - start_time < 30:  # Wait 30 seconds
            time.sleep(1)
            
            # Print stats every 5 seconds
            if time.time() - last_stats_time >= 5:
                stats = client.get_frame_stats()
                print(f"\n📊 Stats after {int(time.time() - start_time)}s:")
                print(f"   Total frames: {stats['total_frames_received']}")
                print(f"   Streaming: {stats['streaming']}")
                print(f"   Current video: {stats['current_video']}")
                print(f"   Buffer size: {stats['buffer_size']}")
                print(f"   Last frame: {stats['last_frame_time']}")
                
                # Get latest frame
                latest_frame = client.get_latest_frame()
                if latest_frame:
                    print(f"   Latest frame: #{latest_frame.frame_number}")
                
                last_stats_time = time.time()
        
        # Final stats
        final_stats = client.get_frame_stats()
        print(f"\n🏁 Final Results:")
        print(f"   Total frames received: {final_stats['total_frames_received']}")
        print(f"   Streaming worked: {'✅ YES' if final_stats['total_frames_received'] > 0 else '❌ NO'}")
        
        # Stop streaming
        print("\n🛑 Stopping video stream...")
        client.stop_video_stream()
        time.sleep(2)
        
        # Disconnect
        client.disconnect()
        print("✅ Test completed")
        
        return final_stats['total_frames_received'] > 0
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        client.disconnect()
        return False

async def test_async_functions():
    """Test async wrapper functions"""
    print("\n⚡ Async Functions Test")
    print("=" * 50)
    
    try:
        # Test start video stream
        print("Testing async start_video_stream...")
        success = await start_video_stream("sample1.mp4")
        
        if success:
            print("✅ Async start successful!")
            
            # Wait for a few frames
            await asyncio.sleep(10)
            
            # Check stats
            stats = get_video_stats()
            print(f"Frames received: {stats['total_frames_received']}")
            
            # Stop streaming
            from app.video_stream_client import stop_video_stream
            await stop_video_stream()
            print("✅ Async stop successful!")
            
            return stats['total_frames_received'] > 0
        else:
            print("❌ Async start failed")
            return False
            
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        return False

def check_mock_server():
    """Check if mock server is running"""
    print("🔍 Mock Server Check")
    print("=" * 50)
    
    try:
        import requests
        # Try video streaming status endpoint
        url = f"http://{settings.mock_server_host}:{settings.mock_server_port}/api/cctv/stream/status"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Mock server is running")
            return True
        else:
            print(f"⚠️ Mock server responded with status: {response.status_code}")
            # Even if 404, server is responding
            if response.status_code == 404:
                print("✅ Mock server is running (endpoint returned 404 but server is up)")
                return True
            return False
            
    except Exception as e:
        print(f"❌ Mock server not reachable: {e}")
        print("💡 Make sure to start mock server:")
        print("   docker-compose up -d mock-server")
        return False

def main():
    print("🧪 Video Stream WebSocket Test Suite")
    print("=" * 60)
    
    # Check configuration
    test_video_config()
    
    # Check mock server
    if not check_mock_server():
        print("\n❌ Cannot proceed without mock server")
        return
    
    # Test connection only
    print(f"\n{'='*60}")
    connection_ok = test_websocket_connection()
    
    if not connection_ok:
        print("\n❌ Connection test failed - stopping here")
        return
    
    # Test full streaming
    print(f"\n{'='*60}")
    streaming_ok = test_video_streaming()
    
    # Test async functions
    print(f"\n{'='*60}")
    async_ok = asyncio.run(test_async_functions())
    
    # Final summary
    print(f"\n{'='*60}")
    print("🏁 TEST SUMMARY")
    print(f"Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"Streaming: {'✅ PASS' if streaming_ok else '❌ FAIL'}")
    print(f"Async: {'✅ PASS' if async_ok else '❌ FAIL'}")
    
    if all([connection_ok, streaming_ok, async_ok]):
        print("\n🎉 ALL TESTS PASSED! WebSocket client is working!")
    else:
        print("\n🔧 Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
