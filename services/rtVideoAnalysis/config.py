import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Azure Computer Vision
    AZURE_VISION_ENDPOINT = os.getenv('AZURE_VISION_ENDPOINT')
    AZURE_VISION_KEY = os.getenv('AZURE_VISION_KEY')

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS = os.getenv(
        'KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    FIRE_DETECTED_TOPIC = 'rtVideoAnalysis.fireDetected'

    # Video Processing
    FRAME_INTERVAL_SECONDS = int(os.getenv('FRAME_INTERVAL_SECONDS', '10'))
    FIRE_DETECTION_CONFIDENCE_THRESHOLD = int(
        os.getenv('FIRE_DETECTION_CONFIDENCE_THRESHOLD', '70'))

    # CCTV Streams (RTSP URLs)
    CCTV_STREAMS = [
        os.getenv('CCTV_STREAM_1'),
        os.getenv('CCTV_STREAM_2'),
        os.getenv('CCTV_STREAM_3'),
        os.getenv('CCTV_STREAM_4')
    ]

    # Remove None values
    CCTV_STREAMS = [stream for stream in CCTV_STREAMS if stream]

    # CCTV IDs (for event correlation)
    CCTV_IDS = [
        os.getenv('CCTV_ID_1', 'cctv_001'),
        os.getenv('CCTV_ID_2', 'cctv_002'),
        os.getenv('CCTV_ID_3', 'cctv_003'),
        os.getenv('CCTV_ID_4', 'cctv_004')
    ]

    # Service
    SERVICE_NAME = 'rtVideoAnalysis'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
