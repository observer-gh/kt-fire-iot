import base64
import os
import time
from io import BytesIO
from PIL import Image
from loguru import logger
from .config import Config
from .models import CctvFrame
from .azure_vision_client import AzureVisionClient
from .event_publisher import EventPublisher


class FrameProcessor:
    """Processes incoming video frames from the CCTV stream"""

    def __init__(self, azure_vision_client: AzureVisionClient = None, event_publisher: EventPublisher = None):
        self.frame_count = 0
        self.azure_vision_client = azure_vision_client
        self.event_publisher = event_publisher
        self.last_fire_detection_time = 0
        self.last_frame_log_time = 0
        self.setup_output_directory()

    def setup_output_directory(self):
        """Create output directory for saving frames"""
        if Config.SAVE_FRAMES:
            os.makedirs(Config.FRAMES_OUTPUT_DIR, exist_ok=True)
            logger.info(f"Frame output directory: {Config.FRAMES_OUTPUT_DIR}")

    def _log_frame_reception(self, frame: CctvFrame, image: Image.Image):
        """Log frame reception throttled to every 5 seconds"""
        current_time = time.time()

        # First log or 5 seconds have passed
        if (self.last_frame_log_time == 0 or
                current_time - self.last_frame_log_time >= 5):
            self.last_frame_log_time = current_time
            logger.info(f"Received frame {frame.frame_number} from {frame.video_file_name} "
                        f"(size: {image.size}, total frames: {self.frame_count})")
        else:
            logger.debug(
                f"Frame {frame.frame_number} processed (size: {image.size})")

    def process_frame(self, frame: CctvFrame):
        """Process a single CCTV frame"""
        try:
            self.frame_count += 1

            # Decode Base64 image
            image = self.decode_base64_image(frame.image_data)

            if image:
                # Log frame info (throttled to every 5 seconds)
                self._log_frame_reception(frame, image)

                # Fire detection analysis (throttled)
                if self.azure_vision_client:
                    should_detect = self._should_detect_fire()
                    logger.debug(
                        f"Frame {frame.frame_number}: should_detect={should_detect}, last_time={self.last_fire_detection_time}")
                    if should_detect:
                        logger.info(
                            f"🔍 Starting fire detection analysis for frame {frame.frame_number}")
                        fire_detected = self._detect_fire_in_frame(
                            image, frame)
                        if fire_detected:
                            logger.warning(
                                f"🔥 FIRE DETECTED in frame {frame.frame_number}!")
                            self._publish_fire_event(frame, fire_detected)
                    else:
                        logger.debug(
                            f"Skipping fire detection for frame {frame.frame_number} (throttled)")
                else:
                    logger.debug(
                        f"No Azure Vision client available for frame {frame.frame_number}")

                # Save frame if configured
                if Config.SAVE_FRAMES:
                    self.save_frame(image, frame)

                return True

        except Exception as e:
            logger.error(f"Error processing frame {frame.frame_number}: {e}")
            return False

    def decode_base64_image(self, base64_data: str) -> Image.Image:
        """Decode Base64 string to PIL Image"""
        try:
            # Remove data URL prefix if present
            if base64_data.startswith('data:image'):
                base64_data = base64_data.split(',')[1]
                base64_data += "="*(-len(base64_data) % 4)

            # Decode Base64
            image_bytes = base64.b64decode(base64_data)

            # Convert to PIL Image
            image = Image.open(BytesIO(image_bytes))
            return image

        except Exception as e:
            logger.error(f"Failed to decode Base64 image: {e}")
            return None

    def save_frame(self, image: Image.Image, frame: CctvFrame):
        """Save frame to disk"""
        try:
            filename = f"frame_{frame.frame_number:06d}_{frame.timestamp}.jpg"
            filepath = os.path.join(Config.FRAMES_OUTPUT_DIR, filename)

            # Save as JPEG
            image.save(filepath, 'JPEG', quality=85)

            # Log every 30 frames (1 second at 30fps)
            if self.frame_count % 30 == 0:
                logger.info(
                    f"Saved {self.frame_count} frames to {Config.FRAMES_OUTPUT_DIR}")

        except Exception as e:
            logger.error(f"Failed to save frame: {e}")

    def _should_detect_fire(self) -> bool:
        """Check if enough time has passed to perform fire detection"""
        current_time = time.time()

        # First detection (last_fire_detection_time == 0) or enough time has passed
        if (self.last_fire_detection_time == 0 or
                current_time - self.last_fire_detection_time >= Config.FIRE_DETECTION_INTERVAL_SECONDS):
            self.last_fire_detection_time = current_time
            return True

        return False

    def _detect_fire_in_frame(self, image: Image.Image, frame: CctvFrame) -> bool:
        """Detect fire in the current frame"""
        try:
            logger.debug(
                f"Analyzing frame {frame.frame_number} for fire detection...")

            # Call Azure Vision API
            detection_result = self.azure_vision_client.detect_fire(image)

            # Log detailed detection results
            self._log_detection_results(frame, detection_result)

            if detection_result['detected']:
                confidence = detection_result['confidence']

                if confidence >= Config.FIRE_DETECTION_CONFIDENCE_THRESHOLD:
                    logger.warning(f"FIRE DETECTED! Frame: {frame.frame_number}, "
                                   f"Video: {frame.video_file_name}, "
                                   f"Confidence: {confidence}%")

                    # Publish fire detected event
                    if self.event_publisher:
                        self._publish_fire_event(
                            frame, confidence, detection_result)

                    return True
                else:
                    logger.info(f"Fire detected but below threshold. "
                                f"Frame: {frame.frame_number}, Confidence: {confidence}%")
            else:
                logger.debug(f"No fire detected in frame {frame.frame_number}")

            return False

        except Exception as e:
            logger.error(
                f"Error in fire detection for frame {frame.frame_number}: {e}")
            return False

    def _log_detection_results(self, frame: CctvFrame, detection_result: dict):
        """Log detailed Azure Vision detection results including top 3 objects"""
        try:
            detected = detection_result.get('detected', False)
            confidence = detection_result.get('confidence', 0)
            objects = detection_result.get('objects', [])
            tags = detection_result.get('tags', [])

            # Log basic detection status
            status = "🔥 FIRE" if detected else "✅ NO FIRE"
            logger.info(
                f"{status} | Frame {frame.frame_number} | Confidence: {confidence}%")

            # Log top 3 detected objects with confidence
            if objects and isinstance(objects, list):
                # Handle both dict and string objects
                top_objects = []
                for obj in objects[:3]:  # Take first 3
                    if isinstance(obj, dict):
                        top_objects.append(
                            f"{obj.get('object', 'unknown')} ({obj.get('confidence', 0):.1f}%)")
                    else:
                        top_objects.append(str(obj))

                if top_objects:
                    objects_str = ", ".join(top_objects)
                    logger.info(f"🎯 Top Objects: {objects_str}")
                else:
                    logger.info("🎯 Top Objects: None detected")
            else:
                logger.info("🎯 Top Objects: None detected")

            # Log relevant tags
            if tags and isinstance(tags, list):
                # Handle both dict and string tags
                top_tags = []
                for tag in tags[:3]:  # Take first 3
                    if isinstance(tag, dict):
                        top_tags.append(
                            f"{tag.get('name', 'unknown')} ({tag.get('confidence', 0):.1f}%)")
                    else:
                        top_tags.append(str(tag))

                if top_tags:
                    tags_str = ", ".join(top_tags)
                    logger.info(f"🏷️  Relevant Tags: {tags_str}")
                else:
                    logger.info("🏷️  Relevant Tags: None detected")
            else:
                logger.info("🏷️  Relevant Tags: None detected")

        except Exception as e:
            logger.error(f"Error logging detection results: {e}")

    def _publish_fire_event(self, frame: CctvFrame, confidence: int, detection_result: dict):
        """Publish fire detected event"""
        try:
            # Map video filename to CCTV ID
            cctv_id = self._get_cctv_id_from_video(frame.video_file_name)

            # Basic facility mapping (can be enhanced)
            facility_id = cctv_id  # TODO: Map CCTV ID to actual facility
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
            logger.error(f"Error publishing fire event: {e}")

    def _get_cctv_id_from_video(self, video_filename: str) -> str:
        """Map video filename to CCTV ID"""
        if "sample1.mp4" in video_filename:
            return "cctv_001"
        elif "sample2.mp4" in video_filename:
            return "cctv_002"
        else:
            return "cctv_unknown"

    def _publish_fire_event(self, frame: CctvFrame, detection_result: dict):
        """Publish fire detected event (same pattern as rtVideoAnalysis)"""
        try:
            if not self.event_publisher:
                logger.warning(
                    "No event publisher configured - skipping event")
                return

            # Get CCTV ID from video filename
            cctv_id = self._get_cctv_id_from_video(frame.video_file_name)

            # Map CCTV ID to facility info (same as rtVideoAnalysis pattern)
            facility_id = cctv_id  # TODO: Map CCTV ID to facility
            equipment_location = "cctv_area"  # TODO: Map CCTV ID to location

            description = (f"Fire detected via CCTV {cctv_id}. "
                           f"Objects: {detection_result.get('objects', [])}, "
                           f"Tags: {detection_result.get('tags', [])}")

            detection_area = "full_frame"  # TODO: Implement area detection
            confidence = detection_result.get('confidence', 0)

            # Publish the event
            success = self.event_publisher.publish_fire_detected(
                cctv_id=cctv_id,
                facility_id=facility_id,
                equipment_location=equipment_location,
                detection_confidence=confidence,
                detection_area=detection_area,
                description=description
            )

            if success:
                logger.info(
                    f"✅ Fire event published for CCTV {cctv_id} with {confidence}% confidence")
            else:
                logger.error(
                    f"❌ Failed to publish fire event for CCTV {cctv_id}")

        except Exception as e:
            logger.error(f"Error publishing fire event: {e}")

    def get_frame_stats(self):
        """Get processing statistics"""
        return {
            "total_frames_processed": self.frame_count,
            "output_directory": Config.FRAMES_OUTPUT_DIR if Config.SAVE_FRAMES else None
        }
