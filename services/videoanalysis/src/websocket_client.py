import json
import threading
import time
from typing import Callable, Optional
import websocket
from loguru import logger
from .config import Config
from .models import CctvFrame, ControlMessage, ControlResponse


class StompWebSocketClient:
    """WebSocket client with basic STOMP protocol support"""

    def __init__(self, on_frame_received: Callable[[CctvFrame], None]):
        self.ws: Optional[websocket.WebSocketApp] = None
        self.connected = False
        self.subscribed = False
        self.on_frame_received = on_frame_received
        self.subscription_id = 1

    def connect(self):
        """Connect to the WebSocket server"""
        try:
            self.ws = websocket.WebSocketApp(
                Config.WEBSOCKET_URL,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )

            # Run in separate thread
            wst = threading.Thread(target=self.ws.run_forever)
            wst.daemon = True
            wst.start()

            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1

            if not self.connected:
                raise Exception("Failed to connect within timeout")

            logger.info("WebSocket connected successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    def _on_open(self, ws):
        """Handle WebSocket connection opened"""
        logger.info("WebSocket connection opened")
        # Send STOMP CONNECT frame
        connect_frame = "CONNECT\naccept-version:1.0,1.1,2.0\n\n\x00"
        ws.send(connect_frame)

    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            if message.startswith("CONNECTED"):
                self.connected = True
                logger.info("STOMP connection established")
                self._subscribe_to_streams()

            elif message.startswith("MESSAGE"):
                self._handle_stomp_message(message)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection closed"""
        logger.info("WebSocket connection closed")
        self.connected = False
        self.subscribed = False

    def _subscribe_to_streams(self):
        """Subscribe to CCTV stream and control topics"""
        if not self.connected:
            return

        # Subscribe to video stream
        stream_subscribe = f"SUBSCRIBE\nid:sub-{self.subscription_id}\ndestination:{Config.STREAM_SUBSCRIPTION}\n\n\x00"
        self.ws.send(stream_subscribe)
        self.subscription_id += 1

        # Subscribe to control responses
        control_subscribe = f"SUBSCRIBE\nid:sub-{self.subscription_id}\ndestination:{Config.CONTROL_SUBSCRIPTION}\n\n\x00"
        self.ws.send(control_subscribe)
        self.subscription_id += 1

        self.subscribed = True
        logger.info("Subscribed to CCTV streams")

    def _handle_stomp_message(self, message):
        """Parse and handle STOMP MESSAGE frames"""
        try:
            lines = message.split('\n')
            headers = {}
            body_start = 0

            # Parse headers
            for i, line in enumerate(lines[1:], 1):
                if line == '':
                    body_start = i + 1
                    break
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key] = value

            # Get message body
            body = '\n'.join(lines[body_start:]).rstrip('\x00')

            if not body:
                return

            # Parse JSON body
            data = json.loads(body)
            destination = headers.get('destination', '')

            if destination == Config.STREAM_SUBSCRIPTION:
                self._handle_frame_message(data)
            elif destination == Config.CONTROL_SUBSCRIPTION:
                self._handle_control_response(data)

        except Exception as e:
            logger.error(f"Error parsing STOMP message: {e}")

    def _handle_frame_message(self, data):
        """Handle incoming video frame data"""
        try:
            frame = CctvFrame(
                frame_number=data.get('frameNumber', 0),
                image_data=data.get('imageData', ''),
                timestamp=data.get('timestamp', 0),
                video_file_name=data.get('videoFileName', '')
            )
            self.on_frame_received(frame)

        except Exception as e:
            logger.error(f"Error handling frame: {e}")

    def _handle_control_response(self, data):
        """Handle control command responses"""
        response = ControlResponse(
            status=data.get('status', 'unknown'),
            message=data.get('message', ''),
            streaming=data.get('streaming')
        )
        logger.info(f"Control response: {response.message}")

    def send_control_command(self, command: ControlMessage):
        """Send control command to mock server"""
        if not self.connected:
            logger.error("Not connected to WebSocket")
            return False

        try:
            body = {
                "action": command.action
            }
            if command.video_file_name:
                body["videoFileName"] = command.video_file_name

            message = f"SEND\ndestination:{Config.CONTROL_DESTINATION}\n\n{json.dumps(body)}\x00"
            self.ws.send(message)
            logger.info(f"Sent control command: {command.action}")
            return True

        except Exception as e:
            logger.error(f"Failed to send control command: {e}")
            return False

    def disconnect(self):
        """Disconnect from WebSocket"""
        if self.ws:
            self.ws.close()
            self.connected = False
            self.subscribed = False
