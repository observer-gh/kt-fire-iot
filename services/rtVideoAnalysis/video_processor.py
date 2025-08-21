import logging
import cv2
import time
import threading
from datetime import datetime
from azure_vision_client import AzureVisionClient
from event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(self, config, azure_vision_client, event_publisher):
        self.config = config
        self.azure_vision_client = azure_vision_client
        self.event_publisher = event_publisher
        self.running = False
        self.threads = []

    def start_processing(self):
        """Start processing all CCTV streams"""
        self.running = True

        for i, stream_url in enumerate(self.config.CCTV_STREAMS):
            if stream_url:
                cctv_id = self.config.CCTV_IDS[i]
                thread = threading.Thread(
                    target=self._process_stream,
                    args=(stream_url, cctv_id),
                    daemon=True
                )
                thread.start()
                self.threads.append(thread)
                logger.info(
                    f"Started processing stream {cctv_id}: {stream_url}")

        logger.info(f"Started {len(self.threads)} video processing threads")

    def stop_processing(self):
        """Stop all video processing threads"""
        self.running = False

        for thread in self.threads:
            thread.join(timeout=5)

        logger.info("Stopped all video processing threads")

    def _process_stream(self, stream_url, cctv_id):
        """Process single CCTV stream"""
        cap = None
        last_processed = 0

        try:
            cap = cv2.VideoCapture(stream_url)

            if not cap.isOpened():
                logger.error(f"Failed to open stream: {stream_url}")
                return

            logger.info(f"Successfully opened stream: {cctv_id}")

            while self.running:
                ret, frame = cap.read()

                if not ret:
                    logger.warning(f"Failed to read frame from {cctv_id}")
                    time.sleep(1)
                    continue

                current_time = time.time()

                # Process frame at specified interval
                if current_time - last_processed >= self.config.FRAME_INTERVAL_SECONDS:
                    self._process_frame(frame, cctv_id)
                    last_processed = current_time

        except Exception as e:
            logger.error(f"Error processing stream {cctv_id}: {e}")
        finally:
            if cap:
                cap.release()
                logger.info(f"Released stream: {cctv_id}")

    def _process_frame(self, frame, cctv_id):
        """Process single frame for fire detection"""
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
