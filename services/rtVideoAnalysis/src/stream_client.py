import logging
import json
import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import websocket
import threading
import time

logger = logging.getLogger(__name__)


class StreamClient:
    def __init__(self, websocket_url=None):
        self.websocket_url = websocket_url
        self.ws = None
        self.connected = False
        self.frame_callback = None
        self.running = False

    def connect(self):
        """Connect to WebSocket streaming server"""
        try:
            if not self.websocket_url:
                raise ValueError("WebSocket URL not configured")

            self.ws = websocket.WebSocketApp(
                self.websocket_url,
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

            if not self.connected:
                raise Exception(
                    "Failed to connect to WebSocket streaming server")

            logger.info("Connected to WebSocket streaming server")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to streaming server: {e}")
            return False

    def _on_open(self, ws):
        """WebSocket connection opened"""
        logger.info("WebSocket connection opened")
        self.connected = True

        # Subscribe to CCTV stream topic
        subscribe_msg = {
            "destination": "/topic/cctv-stream",
            "id": "cctv-subscription"
        }
        ws.send(json.dumps(subscribe_msg))
        logger.info("Subscribed to CCTV stream topic")

    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)

            if "payload" in data and data["payload"]:
                # Decode base64 video frame
                frame_data = base64.b64decode(data["payload"])

                # Convert to OpenCV format
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is not None and self.frame_callback:
                    self.frame_callback(frame, data.get("cctv_id", "unknown"))

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

    def start_stream(self, video_file_name):
        """Start video streaming"""
        if not self.connected:
            logger.error("Not connected to streaming server")
            return False

        control_msg = {
            "destination": "/app/cctv/control",
            "payload": json.dumps({
                "action": "start",
                "videoFileName": video_file_name
            })
        }

        self.ws.send(json.dumps(control_msg))
        logger.info(f"Started streaming: {video_file_name}")
        return True

    def stop_stream(self):
        """Stop video streaming"""
        if not self.connected:
            return False

        control_msg = {
            "destination": "/app/cctv/control",
            "payload": json.dumps({
                "action": "stop"
            })
        }

        self.ws.send(json.dumps(control_msg))
        logger.info("Stopped streaming")
        return True

    def set_frame_callback(self, callback):
        """Set callback function for processing video frames"""
        self.frame_callback = callback

    def disconnect(self):
        """Disconnect from WebSocket"""
        if self.ws:
            self.ws.close()
        self.connected = False
        logger.info("Disconnected from streaming server")
