from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class CctvFrame:
    """Represents a CCTV frame received from the mock server"""
    frame_number: int
    image_data: str  # Base64 encoded image
    timestamp: int
    video_file_name: str
    received_at: datetime = None
    
    def __post_init__(self):
        if self.received_at is None:
            self.received_at = datetime.utcnow()


@dataclass
class ControlMessage:
    """Represents a control message to send to mock server"""
    action: str  # start, stop, status
    video_file_name: Optional[str] = None


@dataclass
class ControlResponse:
    """Represents a response from mock server control"""
    status: str  # success, error
    message: str
    streaming: Optional[bool] = None


@dataclass
class VideoStreamState:
    """Represents the current state of video streaming"""
    connected: bool = False
    streaming: bool = False
    current_video: Optional[str] = None
    last_frame_time: Optional[datetime] = None
    total_frames_received: int = 0
    error_message: Optional[str] = None
