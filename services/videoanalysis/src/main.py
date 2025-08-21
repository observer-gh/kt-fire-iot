import signal
import sys
import time
from loguru import logger
from .config import Config
from .websocket_client import StompWebSocketClient
from .frame_processor import FrameProcessor
from .models import ControlMessage


class VideoAnalysisService:
    """Main video analysis service that connects to mock server and processes frames"""

    def __init__(self):
        self.frame_processor = FrameProcessor()
        self.ws_client = StompWebSocketClient(
            self.frame_processor.process_frame)
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
        logger.info(f"Connecting to: {Config.WEBSOCKET_URL}")

        try:
            # Connect to WebSocket
            if not self.ws_client.connect():
                logger.error("Failed to connect to WebSocket server")
                return False

            self.running = True

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
            else:
                logger.error("Failed to start video stream")
                return False

            # Main service loop
            self._run_service_loop()

        except Exception as e:
            logger.error(f"Service error: {e}")
            return False

        return True

    def _run_service_loop(self):
        """Main service loop"""
        logger.info("Service started successfully. Processing frames...")

        try:
            while self.running:
                # Service is event-driven (frames processed in callbacks)
                # Just keep alive and log stats periodically
                time.sleep(10)

                if self.running:
                    stats = self.frame_processor.get_frame_stats()
                    logger.info(
                        f"Frames processed: {stats['total_frames_processed']}")

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
