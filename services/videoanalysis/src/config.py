import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Mock server WebSocket settings
    MOCK_SERVER_HOST = os.getenv('MOCK_SERVER_HOST', 'localhost')
    MOCK_SERVER_PORT = os.getenv('MOCK_SERVER_PORT', '8001')
    WEBSOCKET_URL = f"ws://{MOCK_SERVER_HOST}:{MOCK_SERVER_PORT}/cctv-websocket/websocket"

    # STOMP destinations
    CONTROL_DESTINATION = "/app/cctv/control"
    STREAM_SUBSCRIPTION = "/topic/cctv-stream"
    CONTROL_SUBSCRIPTION = "/topic/cctv-control"

    # Frame processing settings
    SAVE_FRAMES = os.getenv('SAVE_FRAMES', 'false').lower() == 'true'
    FRAMES_OUTPUT_DIR = os.getenv('FRAMES_OUTPUT_DIR', './output/frames')

    # Video files to request
    DEFAULT_VIDEO_FILE = os.getenv('DEFAULT_VIDEO_FILE', 'sample1.mp4')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
