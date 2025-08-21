import logging
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image
import io

logger = logging.getLogger(__name__)


class AzureVisionClient:
    def __init__(self, endpoint, key):
        self.client = ComputerVisionClient(
            endpoint, CognitiveServicesCredentials(key))

    def detect_fire(self, image_data):
        """
        Detect fire in image using Azure Computer Vision API

        Args:
            image_data: PIL Image or bytes

        Returns:
            dict: Detection result with confidence and details
        """
        try:
            # Convert to file-like object if PIL Image
            if hasattr(image_data, 'save'):
                img_byte_arr = io.BytesIO()
                image_data.save(img_byte_arr, format='JPEG')
                img_byte_arr.seek(0)  # Reset position to beginning
            else:
                img_byte_arr = image_data

            # Analyze image for objects and tags
            features = [VisualFeatureTypes.objects, VisualFeatureTypes.tags]
            result = self.client.analyze_image_in_stream(
                img_byte_arr, features)

            # Check for fire-related objects and tags
            fire_confidence = self._analyze_fire_detection(result)

            return {
                'detected': fire_confidence > 0,
                'confidence': fire_confidence,
                'objects': [obj.object_property if hasattr(obj, 'object_property') else str(obj) for obj in result.objects],
                'tags': [tag.name if hasattr(tag, 'name') else str(tag) for tag in result.tags]
            }

        except Exception as e:
            logger.error(f"Error detecting fire: {e}")
            return {
                'detected': False,
                'confidence': 0,
                'error': str(e)
            }

    def _analyze_fire_detection(self, result):
        """
        Analyze API result for fire detection

        Args:
            result: Azure Vision API result

        Returns:
            int: Confidence score 0-100
        """
        fire_keywords = ['fire', 'flame', 'smoke', 'burning', 'blaze']
        confidence = 0

        # Check objects
        for obj in result.objects:
            if hasattr(obj, 'object_property') and obj.object_property.lower() in fire_keywords:
                confidence = max(confidence, int(obj.confidence * 100))

        # Check tags
        for tag in result.tags:
            if hasattr(tag, 'name') and tag.name.lower() in fire_keywords:
                confidence = max(confidence, int(tag.confidence * 100))

        return confidence
