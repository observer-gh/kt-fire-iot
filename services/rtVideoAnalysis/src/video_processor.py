import logging
import cv2
import time
import threading
import asyncio
from datetime import datetime
from .azure_vision_client import AzureVisionClient
from .event_publisher import EventPublisher
from .stream_client import StreamClient

logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self, config, azure_vision_client, event_publisher):
        self.config = config
        self.azure_vision_client = azure_vision_client
        self.event_publisher = event_publisher
        self.running = False
        self.threads = []
        self.stream_client = None

    def start_processing(self):
        """Start processing video streams via SockJS"""
        self.running = True

        # Initialize SockJS stream client
        if not self.config.WEBSOCKET_URL:
            logger.error("WebSocket URL not configured")
            return False

        self.stream_client = StreamClient(self.config.WEBSOCKET_URL)

        if not self.stream_client.connect():
            logger.error("Failed to connect to SockJS streaming server")
            return False

        # Set frame callback for processing
        self.stream_client.set_frame_callback(self._process_frame)

        # Start streaming for each CCTV ID with different video files
        for i, cctv_id in enumerate(self.config.CCTV_IDS):
            video_file = self.config.DEFAULT_VIDEO_FILES[i % len(
                self.config.DEFAULT_VIDEO_FILES)]
            logger.info(
                f"Starting stream for {cctv_id} with {video_file}")

            # Start stream in separate thread (non-blocking)
            thread = threading.Thread(
                target=self._start_stream,
                args=(cctv_id, video_file),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)

        logger.info(
            f"Started {len(self.threads)} video streaming threads")
        return True

    def stop_processing(self):
        """Stop all video processing threads"""
        self.running = False

        # Stop SockJS streams
        if self.stream_client:
            self.stream_client.stop_stream()
            self.stream_client.disconnect()

        for thread in self.threads:
            thread.join(timeout=5)

        logger.info("Stopped all video processing threads")

    def _start_stream(self, cctv_id, video_file):
        """Start streaming for CCTV ID with specific video file"""
        try:
            if self.stream_client and self.stream_client.connected:
                self.stream_client.start_stream(video_file)
                logger.info(f"Started streaming {video_file} for {cctv_id}")
            else:
                logger.error(f"Stream client not connected for {cctv_id}")
        except Exception as e:
            logger.error(f"Error starting stream for {cctv_id}: {e}")

    def _process_frame(self, frame, cctv_id):
        """Process single frame for fire detection (async-friendly)"""
        try:
            # Convert frame to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = cv2.imencode('.jpg', frame_rgb)[1].tobytes()

            # Detect fire using Azure Vision
            detection_result = self.azure_vision_client.detect_fire(pil_image)

            if detection_result['detected']:
                confidence = detection_result['confidence']

                if confidence >= self.config.FIRE_DETECTION_CONFIDENCE_THRESHOLD:
                    logger.warning(f"FIRE DETECTED! CCTV: {cctv_id}, "
                                   f"Confidence: {confidence}%")

                    # Publish fire detected event
                    self._publish_fire_event(
                        cctv_id, confidence, detection_result)
                else:
                    logger.debug(f"Fire detected but below threshold. "
                                 f"CCTV: {cctv_id}, Confidence: {confidence}%")
            else:
                logger.debug(f"No fire detected. CCTV: {cctv_id}")

        except Exception as e:
            logger.error(f"Error processing frame from {cctv_id}: {e}")

    def _publish_fire_event(self, cctv_id, confidence, detection_result):
        """Publish fire detected event"""
        try:
            # Extract facility info from CCTV ID (you may need to map this)
            facility_id = cctv_id  # TODO: Map CCTV ID to facility
            equipment_location = "cctv_area"  # TODO: Map CCTV ID to location

            description = (f"Fire detected via CCTV {cctv_id}. "
                           f"Objects: {detection_result.get('objects', [])}, "
                           f"Tags: {detection_result.get('tags', [])}")

            detection_area = "full_frame"  # TODO: Implement area detection

            success = self.event_publisher.publish_fire_detected(
                cctv_id=cctv_id,
                facility_id=facility_id,
                equipment_location=equipment_location,
                detection_confidence=confidence,
                detection_area=detection_area,
                description=description
            )

            if success:
                logger.info(f"Fire event published for CCTV: {cctv_id}")
            else:
                logger.error(
                    f"Failed to publish fire event for CCTV: {cctv_id}")

        except Exception as e:
            logger.error(f"Error publishing fire event for {cctv_id}: {e}")
