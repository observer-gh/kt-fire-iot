from dataclasses import dataclass
from typing import Optional


@dataclass
class CctvFrame:
    """Represents a CCTV frame received from the mock server"""
    frame_number: int
    image_data: str  # Base64 encoded image
    timestamp: int
    video_file_name: str


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
