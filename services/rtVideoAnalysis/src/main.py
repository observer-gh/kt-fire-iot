import logging
import signal
import sys
import time
from .config import Config
from .azure_vision_client import AzureVisionClient
from .event_publisher import EventPublisher
from .video_processor import VideoProcessor

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RtVideoAnalysisService:
    def __init__(self):
        self.config = Config()
        self.azure_vision_client = None
        self.event_publisher = None
        self.video_processor = None
        self.running = False

    def initialize(self):
        """Initialize all service components"""
        try:
            logger.info("Initializing RtVideoAnalysis service...")

            # Validate configuration
            if not self.config.AZURE_VISION_ENDPOINT or not self.config.AZURE_VISION_KEY:
                raise ValueError("Azure Vision endpoint and key are required")

            if not self.config.WEBSOCKET_URL:
                raise ValueError("WebSocket URL is required")

            # Initialize Azure Vision client
            self.azure_vision_client = AzureVisionClient(
                self.config.AZURE_VISION_ENDPOINT,
                self.config.AZURE_VISION_KEY
            )
            logger.info("Azure Vision client initialized")

            # Initialize event publisher
            self.event_publisher = EventPublisher(
                self.config.KAFKA_BOOTSTRAP_SERVERS,
                self.config.FIRE_DETECTED_TOPIC
            )
            logger.info("Event publisher initialized")

            # Initialize video processor
            self.video_processor = VideoProcessor(
                self.config,
                self.azure_vision_client,
                self.event_publisher
            )
            logger.info("Video processor initialized")

            logger.info("RtVideoAnalysis service initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize service: {e}")
            return False

    def start(self):
        """Start the video analysis service"""
        if not self.initialize():
            logger.error("Service initialization failed")
            return False

        try:
            logger.info("Starting RtVideoAnalysis service...")
            self.running = True

            # Start video processing
            if not self.video_processor.start_processing():
                logger.error("Failed to start video processing")
                return False

            logger.info("RtVideoAnalysis service started successfully")

            # Keep service running
            while self.running:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Service error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the video analysis service"""
        logger.info("Stopping RtVideoAnalysis service...")
        self.running = False

        if self.video_processor:
            self.video_processor.stop_processing()

        if self.event_publisher:
            self.event_publisher.close()

        logger.info("RtVideoAnalysis service stopped")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)


def main():
    """Main entry point"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create and start service
    service = RtVideoAnalysisService()

    try:
        service.start()
    except Exception as e:
        logger.error(f"Service failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
