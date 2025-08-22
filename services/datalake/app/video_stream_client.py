import json
import threading
import time
import asyncio
import logging
from typing import Callable, Optional, List
from collections import deque
from datetime import datetime

# Optional websocket import for flexibility
try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    websocket = None

from .video_models import CctvFrame, ControlMessage, ControlResponse, VideoStreamState
from .config import settings

logger = logging.getLogger(__name__)


class VideoFrameBuffer:
    """Thread-safe buffer for storing recent video frames"""

    def __init__(self, max_size: int = 10):
        self.frames = deque(maxlen=max_size)
        self._lock = threading.Lock()

    def add_frame(self, frame: CctvFrame):
        """Add a new frame to the buffer"""
        with self._lock:
            self.frames.append(frame)

    def get_latest_frame(self) -> Optional[CctvFrame]:
        """Get the most recent frame"""
        with self._lock:
            return self.frames[-1] if self.frames else None

    def get_frames(self, count: int = None) -> List[CctvFrame]:
        """Get recent frames"""
        with self._lock:
            if count is None:
                return list(self.frames)
            return list(self.frames)[-count:] if count <= len(self.frames) else list(self.frames)

    def clear(self):
        """Clear all frames"""
        with self._lock:
            self.frames.clear()


class StompVideoStreamClient:
    """WebSocket client with STOMP protocol for video streaming"""

    def __init__(self, on_frame_received: Optional[Callable[[CctvFrame], None]] = None):
        if not WEBSOCKET_AVAILABLE:
            raise ImportError(
                "websocket-client library is required. Install with: pip install websocket-client")

        self.ws: Optional[websocket.WebSocketApp] = None
        self.state = VideoStreamState()
        self.on_frame_received = on_frame_received
        self.subscription_id = 1
        self.frame_buffer = VideoFrameBuffer(settings.video_frame_buffer_size)
        self._stats_lock = threading.Lock()

        # Connection thread
        self._ws_thread: Optional[threading.Thread] = None

    def connect(self, max_retries=3, retry_delay=5) -> bool:
        """Connect to the WebSocket server with retry logic"""
        if not WEBSOCKET_AVAILABLE:
            logger.error("WebSocket client not available")
            return False

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Attempting WebSocket({settings.video_websocket_url}) connection (attempt {attempt + 1}/{max_retries})")

                self.ws = websocket.WebSocketApp(
                    settings.video_websocket_url,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )

                # Run in separate thread
                self._ws_thread = threading.Thread(target=self.ws.run_forever)
                self._ws_thread.daemon = True
                self._ws_thread.start()

                # Wait for connection with longer timeout
                timeout = 30
                while not self.state.connected and timeout > 0:
                    time.sleep(0.1)
                    timeout -= 0.1

                if self.state.connected:
                    logger.info("Video WebSocket connected successfully")
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

        error_msg = f"Failed to connect after {max_retries} attempts"
        logger.error(error_msg)
        self.state.error_message = error_msg
        return False

    def _on_open(self, ws):
        """Handle WebSocket connection opened"""
        logger.info("Video WebSocket connection opened")
        # Send STOMP CONNECT frame
        connect_frame = "CONNECT\naccept-version:1.0,1.1,2.0\n\n\x00"
        ws.send(connect_frame)

    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
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
            error_msg = f"Error handling video WebSocket message: {e}"
            logger.error(error_msg)
            self.state.error_message = error_msg

    def _handle_possible_stomp(self, msg: str):
        """Handle possible STOMP messages"""
        if msg.startswith("CONNECTED"):
            self.state.connected = True
            self.state.error_message = None
            logger.info("STOMP connection established for video")
            self._subscribe_to_streams()
        elif msg.startswith("MESSAGE"):
            self._handle_stomp_message(msg)
        elif msg.startswith("ERROR"):
            logger.error(f"STOMP ERROR frame: {msg.splitlines()[:6]}")

    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        error_msg = f"Video WebSocket error: {error}"
        logger.error(error_msg)
        self.state.error_message = error_msg

    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection closed"""
        logger.info("Video WebSocket connection closed")
        self.state.connected = False
        self.state.streaming = False

    def _subscribe_to_streams(self):
        """Subscribe to CCTV stream and control topics"""
        if not self.state.connected:
            return

        # Subscribe to video stream
        stream_subscribe = f"SUBSCRIBE\nid:sub-{self.subscription_id}\ndestination:{settings.video_stream_subscription}\n\n\x00"
        self.ws.send(stream_subscribe)
        self.subscription_id += 1

        # Subscribe to control responses
        control_subscribe = f"SUBSCRIBE\nid:sub-{self.subscription_id}\ndestination:{settings.video_control_subscription}\n\n\x00"
        self.ws.send(control_subscribe)
        self.subscription_id += 1

        logger.info("Subscribed to video streams")

    def _handle_stomp_message(self, message: str):
        """Parse and handle STOMP MESSAGE frames"""
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

            if dest != settings.video_stream_subscription or 'application/json' not in ctype:
                # not the frame stream; ignore or log small preview
                logger.debug(
                    f"skip non-stream frame dest={dest} ctype={ctype} body[:60]={body[:60]!r}")
                return

            data = json.loads(body)
            self._handle_frame_message(data)

        except Exception as e:
            logger.error(f"Error parsing video STOMP message: {e}")

    def _handle_frame_message(self, payload):
        """Handle incoming video frame data with robust image extraction"""
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

        try:
            frame = CctvFrame(
                frame_number=payload.get('frameNumber', 0),
                image_data=b64,
                timestamp=payload.get('timestamp', 0),
                video_file_name=payload.get(
                    'videoPath', '') or payload.get('videoFileName', '')
            )

            # Update statistics
            with self._stats_lock:
                self.state.last_frame_time = datetime.utcnow()
                self.state.total_frames_received += 1
                if not self.state.streaming:
                    self.state.streaming = True
                    self.state.current_video = frame.video_file_name

            # Store in buffer
            self.frame_buffer.add_frame(frame)

            # Call callback if provided
            if self.on_frame_received:
                self.on_frame_received(frame)

            logger.debug(
                f"Received frame {frame.frame_number} from {frame.video_file_name}")

        except Exception as e:
            logger.error(f"Error creating frame object: {e}")

    def _handle_control_response(self, data):
        """Handle control command responses"""
        try:
            response = ControlResponse(
                status=data.get('status', 'unknown'),
                message=data.get('message', ''),
                streaming=data.get('streaming')
            )

            if response.streaming is not None:
                self.state.streaming = response.streaming

            logger.info(f"Video control response: {response.message}")

        except Exception as e:
            logger.error(f"Error handling control response: {e}")

    def send_control_command(self, command: ControlMessage) -> bool:
        """Send control command to mock server"""
        if not self.state.connected:
            logger.error("Not connected to video WebSocket")
            return False

        try:
            body = {
                "action": command.action
            }
            if command.video_file_name:
                body["videoFileName"] = command.video_file_name

            message = f"SEND\ndestination:{settings.video_control_destination}\n\n{json.dumps(body)}\x00"
            self.ws.send(message)
            logger.info(f"Sent video control command: {command.action}")
            return True

        except Exception as e:
            logger.error(f"Failed to send video control command: {e}")
            return False

    def start_video_stream(self, video_file: str = None) -> bool:
        """Start video streaming"""
        if not video_file:
            video_file = settings.default_video_file

        command = ControlMessage(action="start", video_file_name=video_file)
        return self.send_control_command(command)

    def stop_video_stream(self) -> bool:
        """Stop video streaming"""
        command = ControlMessage(action="stop")
        return self.send_control_command(command)

    def get_latest_frame(self) -> Optional[CctvFrame]:
        """Get the most recent frame"""
        return self.frame_buffer.get_latest_frame()

    def get_stream_state(self) -> VideoStreamState:
        """Get current streaming state"""
        return self.state

    def get_frame_stats(self) -> dict:
        """Get frame processing statistics"""
        with self._stats_lock:
            return {
                "connected": self.state.connected,
                "streaming": self.state.streaming,
                "current_video": self.state.current_video,
                "total_frames_received": self.state.total_frames_received,
                "last_frame_time": self.state.last_frame_time,
                "buffer_size": len(self.frame_buffer.frames),
                "error_message": self.state.error_message
            }

    def disconnect(self):
        """Disconnect from WebSocket"""
        if self.ws:
            self.ws.close()
        self.state.connected = False
        self.state.streaming = False
        self.frame_buffer.clear()
        logger.info("Video WebSocket disconnected")

    def is_connected(self):
        """Check if WebSocket is connected and healthy"""
        return self.state.connected and self.ws and self.ws.sock and self.ws.sock.connected


# Global instance for dashboard use
video_stream_client = StompVideoStreamClient()


def get_video_client() -> StompVideoStreamClient:
    """Get the global video stream client"""
    return video_stream_client


async def start_video_stream(video_file: str = None) -> bool:
    """Start video streaming (async wrapper)"""
    if not video_stream_client.state.connected:
        if not video_stream_client.connect(max_retries=3, retry_delay=5):
            return False
        # Wait a moment for connection to stabilize
        await asyncio.sleep(2)

    return video_stream_client.start_video_stream(video_file)


async def stop_video_stream() -> bool:
    """Stop video streaming (async wrapper)"""
    return video_stream_client.stop_video_stream()


def get_latest_video_frame() -> Optional[CctvFrame]:
    """Get the latest video frame"""
    return video_stream_client.get_latest_frame()


def get_video_stats() -> dict:
    """Get video streaming statistics"""
    return video_stream_client.get_frame_stats()
