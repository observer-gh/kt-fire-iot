import io
import base64
import re
from PIL import Image
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

    def connect(self, max_retries=3, retry_delay=5):
        """Connect to the WebSocket server with retry logic"""
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Attempting WebSocket({Config.WEBSOCKET_URL}) connection (attempt {attempt + 1}/{max_retries})")

                self.ws = websocket.WebSocketApp(
                    # e.g. wss://.../cctv-websocket[/websocket]
                    Config.WEBSOCKET_URL,
                    # header={
                    #     "Origin": Config.CLIENT_ORIGIN or "https://app-dev-videoanalysis.azurewebsites.net"},
                    # # <- important on Azure
                    # subprotocols=["v12.stomp"],
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                )

                # Run in separate thread
                wst = threading.Thread(target=self.ws.run_forever)
                wst.daemon = True
                wst.start()

                # Wait for connection with longer timeout
                timeout = 30
                while not self.connected and timeout > 0:
                    time.sleep(0.1)
                    timeout -= 0.1

                if self.connected:
                    logger.info("WebSocket connected successfully")
                    return True
                else:
                    logger.warning(
                        f"Connection attempt {attempt + 1} failed - timeout")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)

            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)

        logger.error(f"Failed to connect after {max_retries} attempts")
        return False

    def _on_open(self, ws):
        """Handle WebSocket connection opened"""
        logger.info("WebSocket connection opened")
        # Send STOMP CONNECT frame
        connect_frame = "CONNECT\naccept-version:1.0,1.1,2.0\n\n\x00"
        ws.send(connect_frame)

    def _on_message(self, ws, message):
        try:
            # SockJS control frames
            if message == 'o' or message == 'h':
                return
            # SockJS data frame(s): a["STOMP", ...]
            if message.startswith('a'):
                frames = json.loads(message[1:])    # strip leading 'a'
                for frame in frames:
                    self._handle_possible_stomp(frame)
                return
            # Raw STOMP (local)
            self._handle_possible_stomp(message)
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def _handle_possible_stomp(self, msg: str):
        if msg.startswith("CONNECTED"):
            self.connected = True
            logger.info("STOMP connection established")
            self._subscribe_to_streams()
        elif msg.startswith("MESSAGE"):
            self._handle_stomp_message(msg)
        elif msg.startswith("ERROR"):
            logger.error(f"STOMP ERROR frame: {msg.splitlines()[:6]}")

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

    # --- replace _handle_stomp_message with header/body checks ---

    def _handle_stomp_message(self, message: str):
        try:
            head, body_plus = message.split('\n\n', 1)
            headers = {}
            for line in head.splitlines()[1:]:
                if ':' in line:
                    k, v = line.split(':', 1)
                    headers[k] = v
            body = body_plus.split('\x00', 1)[0]
            logger.debug(f"SAMPLE headers={headers} bodyStart={body[:120]!r}")
            dest = headers.get('destination', '')
            ctype = headers.get('content-type', '').lower()

            if dest != Config.STREAM_SUBSCRIPTION or 'application/json' not in ctype:
                # not the frame stream; ignore or log small preview
                logger.debug(
                    f"skip non-stream frame dest={dest} ctype={ctype} body[:60]={body[:60]!r}")
                return

            data = json.loads(body)
            self._handle_frame_message(data)

        except Exception as e:
            logger.error(f"Error parsing STOMP message: {e}")


# --- in _handle_frame_message, make decoding robust ---


    def _handle_frame_message(self, payload):
        import re
        import base64
        import io
        from PIL import Image

        b64 = (payload.get('data')                    # <-- primary
               or payload.get('imageData')
               or payload.get('image')
               or payload.get('frame') or '')

        if not b64:
            logger.debug(f"no b64 field; keys={list(payload.keys())[:8]}")
            return

        # strip data URI + whitespace/newlines
        if b64.startswith('data:'):
            b64 = b64.split(',', 1)[1]
        b64 = re.sub(r'\s+', '', b64)
        b64 += "=" * (-len(b64) % 4)

        try:
            raw = base64.b64decode(b64, validate=False)

        except Exception:
            # fallback for urlsafe
            raw = base64.urlsafe_b64decode(b64 + "=" * (-len(b64) % 4))

        # quick magic check (JPEG/PNG/GIF)
        if not (raw.startswith(b'\xFF\xD8\xFF') or raw.startswith(b'\x89PNG\r\n\x1a\n') or raw.startswith(b'GIF8')):
            logger.error(
                f"not image bytes; magic={raw[:16].hex()} len={len(raw)}")
            return

        # verify & hand off
        img = Image.open(io.BytesIO(raw))
        img.verify()
        img = Image.open(io.BytesIO(raw))  # re-open for actual use

        frame = CctvFrame(
            frame_number=payload.get('frameNumber', 0),
            image_data=b64,
            timestamp=payload.get('timestamp', 0),
            video_file_name=payload.get('videoPath', '')
        )
        self.on_frame_received(frame)

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

    def is_connected(self):
        """Check if WebSocket is connected and healthy"""
        return self.connected and self.ws and self.ws.sock and self.ws.sock.connected
