import base64
import os
from io import BytesIO
from PIL import Image
from loguru import logger
from .config import Config
from .models import CctvFrame


class FrameProcessor:
    """Processes incoming video frames from the CCTV stream"""

    def __init__(self):
        self.frame_count = 0
        self.setup_output_directory()

    def setup_output_directory(self):
        """Create output directory for saving frames"""
        if Config.SAVE_FRAMES:
            os.makedirs(Config.FRAMES_OUTPUT_DIR, exist_ok=True)
            logger.info(f"Frame output directory: {Config.FRAMES_OUTPUT_DIR}")

    def process_frame(self, frame: CctvFrame):
        """Process a single CCTV frame"""
        try:
            self.frame_count += 1

            # Decode Base64 image
            image = self.decode_base64_image(frame.image_data)

            if image:
                # Log frame info instead of saving
                logger.info(f"Received frame {frame.frame_number} from {frame.video_file_name} "
                           f"(size: {image.size}, timestamp: {frame.timestamp})")

                # Save frame if configured
                if Config.SAVE_FRAMES:
                    self.save_frame(image, frame)

                # Here you can add more processing:
                # - Fire detection analysis
                # - Object detection
                # - Send to other services
                # - etc.

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

    def get_frame_stats(self):
        """Get processing statistics"""
        return {
            "total_frames_processed": self.frame_count,
            "output_directory": Config.FRAMES_OUTPUT_DIR if Config.SAVE_FRAMES else None
        }
