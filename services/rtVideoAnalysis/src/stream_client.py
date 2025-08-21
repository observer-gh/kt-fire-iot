import logging
import json
import base64
import cv2
import numpy as np
import websocket
import threading
import time

logger = logging.getLogger(__name__)


class SockJSWebSocketClient:
    def __init__(self, ws_url, frame_callback=None):
        self.ws_url = ws_url
        self.frame_callback = frame_callback
        self.connected = False
        self.ws = None

    def connect(self):
        """Connect to WebSocket"""
        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )

            # Start WebSocket connection in separate thread
            self.ws_thread = threading.Thread(
                target=self.ws.run_forever, daemon=True)
            self.ws_thread.start()

            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1

            return self.connected

        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            return False

    def _on_open(self, ws):
        """WebSocket connection opened"""
        logger.info("WebSocket connection opened")
        self.connected = True

        # Subscribe to CCTV stream topic
        subscribe_msg = json.dumps([
            "SUBSCRIBE",
            {"destination": "/topic/cctv-stream", "id": "cctv-subscription"}
        ])
        ws.send(subscribe_msg)
        logger.info("Subscribed to CCTV stream topic")

    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            # Handle SockJS message format
            if message.startswith('a['):
                # Parse SockJS array message
                data_str = message[2:-1]  # Remove 'a[' and ']'
                if data_str.startswith('"') and data_str.endswith('"'):
                    data_str = data_str[1:-1]  # Remove quotes
                    data_str = data_str.replace('\\"', '"')  # Unescape quotes

                data = json.loads(data_str)

                if isinstance(data, dict) and "imageData" in data:
                    # Decode base64 video frame
                    frame_data = base64.b64decode(data["imageData"])

                    # Convert to OpenCV format
                    nparr = np.frombuffer(frame_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if frame is not None and self.frame_callback:
                        self.frame_callback(frame, data.get(
                            "videoFileName", "unknown"))

        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")

    def _on_error(self, ws, error):
        """WebSocket error handler"""
        logger.error(f"WebSocket error: {error}")
        self.connected = False

    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed"""
        logger.info("WebSocket connection closed")
        self.connected = False

    def send_control_message(self, action, video_file_name=None):
        """Send control message to start/stop streaming"""
        if not self.connected or not self.ws:
            logger.error("WebSocket not connected")
            return False

        control_msg = json.dumps([
            "SEND",
            {"destination": "/app/cctv/control"},
            json.dumps({
                "action": action,
                "videoFileName": video_file_name
            })
        ])

        self.ws.send(control_msg)
        return True

    def close(self):
        """Close WebSocket connection"""
        if self.ws:
            self.ws.close()
        self.connected = False


class StreamClient:
    def __init__(self, websocket_url=None):
        self.websocket_url = websocket_url
        self.connected = False
        self.frame_callback = None
        self.running = False
        self.ws_client = None

    def connect(self):
        """Connect to SockJS WebSocket streaming server"""
        try:
            if not self.websocket_url:
                raise ValueError("WebSocket URL not configured")

            logger.info(f"Connecting to SockJS: {self.websocket_url}")

            # Simple approach - connect directly to SockJS WebSocket endpoint
            ws_url = f"{self.websocket_url}/websocket"
            logger.info(f"Connecting to WebSocket: {ws_url}")

            # Create and connect WebSocket client
            self.ws_client = SockJSWebSocketClient(ws_url, self.frame_callback)

            if self.ws_client.connect():
                self.connected = True
                logger.info("Connected to SockJS streaming server")
                return True
            else:
                raise Exception("WebSocket connection failed")

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def start_stream(self, video_file_name):
        """Start video streaming"""
        if not self.connected or not self.ws_client:
            logger.error("Not connected to streaming server")
            return False

        return self.ws_client.send_control_message("start", video_file_name)

    def stop_stream(self):
        """Stop video streaming"""
        if not self.connected or not self.ws_client:
            return False

        return self.ws_client.send_control_message("stop")

    def set_frame_callback(self, callback):
        """Set callback function for processing video frames"""
        self.frame_callback = callback
        if self.ws_client:
            self.ws_client.frame_callback = callback

    def disconnect(self):
        """Disconnect from WebSocket"""
        if self.ws_client:
            self.ws_client.close()
        self.connected = False
        logger.info("Disconnected from streaming server")
