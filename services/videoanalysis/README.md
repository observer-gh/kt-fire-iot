# Video Analysis Service

A Python service that connects to the mock server's WebSocket CCTV stream and processes video frames in real-time.

## Features

- WebSocket connection with STOMP protocol support
- Receives Base64-encoded video frames from mock server
- Decodes and saves frames to disk
- Configurable frame processing
- Graceful shutdown handling

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment (copy .env.example to .env):

```bash
cp .env.example .env
```

3. Run the service:

```bash
python main.py
```

## Configuration

Environment variables:

- `MOCK_SERVER_HOST`: Mock server hostname (default: localhost)
- `MOCK_SERVER_PORT`: Mock server port (default: 8080)
- `SAVE_FRAMES`: Save frames to disk (default: true)
- `FRAMES_OUTPUT_DIR`: Directory to save frames (default: ./output/frames)
- `DEFAULT_VIDEO_FILE`: Video file to request (default: sample1.mp4)
- `LOG_LEVEL`: Logging level (default: INFO)

## Docker

Build and run with Docker:

```bash
docker build -t videoanalysis .
docker run --rm -e MOCK_SERVER_HOST=host.docker.internal videoanalysis
```

## Architecture

- `main.py`: Service entry point
- `src/config.py`: Configuration management
- `src/models.py`: Data structures
- `src/websocket_client.py`: WebSocket/STOMP client
- `src/frame_processor.py`: Frame processing logic
