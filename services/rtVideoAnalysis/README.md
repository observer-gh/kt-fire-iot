# RtVideoAnalysis Service

Real-time video analysis service for fire detection using Azure Computer Vision API.

## Features

- Process CCTV streams via WebSocket streaming
- Fire detection using Azure Computer Vision
- Kafka event publishing for detected fires
- Configurable confidence thresholds

## Environment Variables

```bash
# Azure Computer Vision
AZURE_VISION_ENDPOINT=your-endpoint
AZURE_VISION_KEY=your-key

# Kafka/Event Hubs
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# WebSocket Streaming
WEBSOCKET_URL=ws://localhost:8001/cctv-websocket
DEFAULT_VIDEO_FILES=sample1.mp4,sample2.mp4

# CCTV IDs
CCTV_ID_1=cctv_001
CCTV_ID_2=cctv_002
CCTV_ID_3=cctv_003
CCTV_ID_4=cctv_004

# Processing
FRAME_INTERVAL_SECONDS=10
FIRE_DETECTION_CONFIDENCE_THRESHOLD=70
```

## Run

```bash
# Local
python main.py

# Docker
docker build -t rtvideoanalysis .
docker run --env-file .env rtvideoanalysis
```

## Testing

```bash
# Test Azure Vision integration
PYTHONPATH=. python tests/test_azure_vision.py

# Run all tests
PYTHONPATH=. python -m pytest tests/ -v
```

**Note**: Use `PYTHONPATH=.` to ensure the `src` module can be imported from tests.

## Events

Publishes `rtVideoAnalysis.fireDetected` events when fire is detected.
