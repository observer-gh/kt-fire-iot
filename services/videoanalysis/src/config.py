import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Mock server WebSocket settings
    MOCK_SERVER_HOST = os.getenv('MOCK_SERVER_HOST', 'localhost')
    MOCK_SERVER_PORT = os.getenv('MOCK_SERVER_PORT', '8001')

    # Environment detection
    ENVIRONMENT = os.getenv('PROFILE', 'local')  # local, cloud

    # Use different URLs for local vs cloud
    if ENVIRONMENT == 'cloud':
        # Azure Web Apps - use SockJS endpoint
        WEBSOCKET_URL = f"wss://{MOCK_SERVER_HOST}/cctv-websocket/websocket"
    else:
        # Local development uses custom port with SockJS
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

    # Azure Computer Vision
    AZURE_VISION_ENDPOINT = os.getenv('AZURE_VISION_ENDPOINT')
    AZURE_VISION_KEY = os.getenv('AZURE_VISION_KEY')

    # Fire Detection
    FIRE_DETECTION_CONFIDENCE_THRESHOLD = int(
        os.getenv('FIRE_DETECTION_CONFIDENCE_THRESHOLD', '70'))
    FIRE_DETECTION_INTERVAL_SECONDS = int(
        os.getenv('FIRE_DETECTION_INTERVAL_SECONDS', '20'))

    # Environment
    ENVIRONMENT = os.getenv('PROFILE', 'local')  # local, cloud

    # Kafka (for local development)
    KAFKA_BOOTSTRAP_SERVERS = os.getenv(
        'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    FIRE_DETECTED_TOPIC = 'videoAnalysis.fireDetected'

    # Azure Event Hub (for cloud)
    EVENTHUB_CONN = os.getenv('EVENTHUB_CONN')
    EVENTHUB_FIRE_DETECTED_TOPIC = 'videoAnalysis.fireDetected'

    # Service
    SERVICE_NAME = 'videoanalysis'

    # Health check server
    HEALTH_PORT = int(os.getenv('HEALTH_PORT', '8080'))

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
