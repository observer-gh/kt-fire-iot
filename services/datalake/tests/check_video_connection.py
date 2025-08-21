#!/usr/bin/env python3
"""
Quick check script for video WebSocket connection
Minimal test to verify if mock server WebSocket is reachable
"""

import sys
import os
import time

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.config import settings

def check_mock_server_http():
    """Check if mock server HTTP is reachable"""
    try:
        import requests
        # Try multiple endpoints to check if mock server is running
        endpoints_to_try = [
            "/api/cctv/stream/status",  # Video streaming status
            "/mock/equipment",          # Equipment endpoint
            "/swagger-ui.html"          # Swagger UI
        ]
        
        for endpoint in endpoints_to_try:
            url = f"http://{settings.mock_server_host}:{settings.mock_server_port}{endpoint}"
            print(f"🔍 Checking mock server at: {url}")
            
            try:
                response = requests.get(url, timeout=5)
                
                if response.status_code in [200, 404]:  # 404 is OK, means server is running
                    print(f"✅ Mock server HTTP is responding (status: {response.status_code})")
                    return True
                else:
                    print(f"⚠️ Mock server HTTP responded with status: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                continue  # Try next endpoint
                
        print("❌ Mock server HTTP not reachable on any endpoint")
        return False
            
    except Exception as e:
        print(f"❌ Mock server HTTP check failed: {e}")
        return False

def check_websocket_dependency():
    """Check if websocket-client is installed"""
    try:
        import websocket
        print("✅ websocket-client library is available")
        return True
    except ImportError:
        print("❌ websocket-client library not found")
        print("💡 Install with: pip install websocket-client")
        return False

def quick_websocket_test():
    """Quick WebSocket connection test"""
    if not check_websocket_dependency():
        return False
    
    try:
        from app.video_stream_client import StompVideoStreamClient
        
        print(f"🔌 Testing WebSocket connection to: {settings.video_websocket_url}")
        
        client = StompVideoStreamClient()
        success = client.connect()
        
        if success:
            print("✅ WebSocket connection successful!")
            time.sleep(1)  # Brief wait
            
            state = client.get_stream_state()
            print(f"Connected: {state.connected}")
            
            client.disconnect()
            return True
        else:
            print("❌ WebSocket connection failed")
            state = client.get_stream_state()
            if state.error_message:
                print(f"Error: {state.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def main():
    print("🚀 Quick Video WebSocket Connection Check")
    print("=" * 50)
    print(f"Target: {settings.video_websocket_url}")
    print(f"Mock Server: {settings.mock_server_host}:{settings.mock_server_port}")
    print("-" * 50)
    
    # Check HTTP first
    http_ok = check_mock_server_http()
    
    if not http_ok:
        print("\n💡 Troubleshooting:")
        print("1. Start mock server: docker-compose up -d mock-server")
        print("2. Check if port 8001 is available")
        print("3. Verify mock server logs: docker-compose logs mock-server")
        return
    
    # Test WebSocket
    print("\n" + "-" * 50)
    ws_ok = quick_websocket_test()
    
    print("\n" + "=" * 50)
    if ws_ok:
        print("🎉 WebSocket connection is working!")
        print("✅ Ready to proceed with video streaming tests")
    else:
        print("🔧 WebSocket connection failed")
        print("💡 Check mock server WebSocket endpoint configuration")

if __name__ == "__main__":
    main()
