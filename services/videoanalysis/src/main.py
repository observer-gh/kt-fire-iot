import signal
import sys
import time
from loguru import logger
from .config import Config
from .websocket_client import StompWebSocketClient
from .frame_processor import FrameProcessor
from .models import ControlMessage
from .azure_vision_client import AzureVisionClient
from .event_publisher import EventPublisher
from .health_server import HealthServer


class VideoAnalysisService:
    """Main video analysis service that connects to mock server and processes frames"""

    def __init__(self):
        # Initialize Azure Vision client if credentials are available
        azure_vision_client = None
        if Config.AZURE_VISION_ENDPOINT and Config.AZURE_VISION_KEY:
            try:
                azure_vision_client = AzureVisionClient(
                    Config.AZURE_VISION_ENDPOINT,
                    Config.AZURE_VISION_KEY
                )
                logger.info(
                    "Azure Vision client initialized for fire detection")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Azure Vision client: {e}")
        else:
            logger.warning(
                "Azure Vision credentials not provided - fire detection disabled")

        # Initialize event publisher
        event_publisher = EventPublisher()
        if not event_publisher.is_available():
            logger.warning(
                "Kafka not available - events will not be published")

        self.frame_processor = FrameProcessor(
            azure_vision_client, event_publisher)
        self.ws_client = StompWebSocketClient(
            self.frame_processor.process_frame)
        self.event_publisher = event_publisher

        # Initialize health server
        self.health_server = HealthServer(self.frame_processor, self.ws_client)

        self.running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal")
        self.stop()

    def start(self):
        """Start the video analysis service"""
        logger.info("Starting Video Analysis Service")
        self.running = True

        # Start health server
        self.health_server.start()

        # Main service loop with WebSocket reconnection logic
        self._run_service_loop()

        return True

    def _try_connect_websocket(self):
        """Try to connect to WebSocket with retry logic"""
        logger.info(f"Attempting to connect to: {Config.WEBSOCKET_URL}")

        if self.ws_client.connect():
            logger.info("WebSocket connected successfully")

            # Wait a moment for connection to stabilize
            time.sleep(2)

            # Start video streaming
            start_command = ControlMessage(
                action="start",
                video_file_name=Config.DEFAULT_VIDEO_FILE
            )

            if self.ws_client.send_control_command(start_command):
                logger.info(
                    f"Requested video stream: {Config.DEFAULT_VIDEO_FILE}")
                return True
            else:
                logger.error("Failed to start video stream")
                return False
        else:
            logger.warning(
                "Failed to connect to WebSocket server - will retry later")
            return False

    def _run_service_loop(self):
        """Main service loop with WebSocket reconnection logic"""
        logger.info("Service started successfully. Entering main loop...")

        websocket_connected = False
        last_connection_attempt = 0
        connection_retry_interval = 30  # Retry every 30 seconds

        try:
            while self.running:
                current_time = time.time()

                # Try to connect to WebSocket if not connected
                if not websocket_connected and (current_time - last_connection_attempt) >= connection_retry_interval:
                    last_connection_attempt = current_time
                    websocket_connected = self._try_connect_websocket()

                # Check if WebSocket is still connected
                if websocket_connected and not self.ws_client.is_connected():
                    logger.warning("WebSocket connection lost - will retry")
                    websocket_connected = False

                # Log stats periodically
                if self.running:
                    stats = self.frame_processor.get_frame_stats()
                    connection_status = "connected" if websocket_connected else "disconnected"
                    logger.info(
                        f"Service status: WebSocket {connection_status}, Frames processed: {stats['total_frames_processed']}")

                # Sleep before next iteration
                time.sleep(10)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Service loop error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the service gracefully"""
        if not self.running:
            return

        logger.info("Stopping Video Analysis Service...")
        self.running = False

        # Stop video streaming
        stop_command = ControlMessage(action="stop")
        self.ws_client.send_control_command(stop_command)

        # Disconnect WebSocket
        self.ws_client.disconnect()

        # Stop health server
        if hasattr(self, 'health_server'):
            self.health_server.stop()

        # Close event publisher
        if hasattr(self, 'event_publisher'):
            self.event_publisher.close()

        # Log final stats
        stats = self.frame_processor.get_frame_stats()
        logger.info(
            f"Service stopped. Total frames processed: {stats['total_frames_processed']}")


def main():
    """Main entry point"""
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        level=Config.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    logger.info("=" * 50)
    logger.info("Video Analysis Service Starting")
    logger.info("=" * 50)

    # Create and start service
    service = VideoAnalysisService()

    try:
        success = service.start()
        if not success:
            logger.error("Failed to start service")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
