import streamlit as st
import base64
import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional
import logging

from ..video_stream_client import get_video_client, start_video_stream, stop_video_stream, get_latest_video_frame, get_video_stats
from ..video_models import CctvFrame
from ..config import settings

logger = logging.getLogger(__name__)


class VideoDisplayManager:
    """Manages video display state and streaming for Streamlit dashboard"""

    def __init__(self):
        self.video_client = get_video_client()
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize Streamlit session state for video"""
        if 'video_streaming' not in st.session_state:
            st.session_state.video_streaming = False

        if 'video_connected' not in st.session_state:
            st.session_state.video_connected = False

        if 'current_video_file' not in st.session_state:
            st.session_state.current_video_file = settings.default_video_file

        if 'video_error' not in st.session_state:
            st.session_state.video_error = None

        if 'last_frame_time' not in st.session_state:
            st.session_state.last_frame_time = None

    async def connect_video_stream(self) -> bool:
        """Connect to video WebSocket"""
        try:
            if not self.video_client.state.connected:
                success = self.video_client.connect()
                if success:
                    st.session_state.video_connected = True
                    st.session_state.video_error = None
                    logger.info("Video WebSocket connected")
                    return True
                else:
                    error_msg = "Failed to connect to video WebSocket"
                    st.session_state.video_error = error_msg
                    logger.error(error_msg)
                    return False
            return True
        except Exception as e:
            error_msg = f"Video connection error: {e}"
            st.session_state.video_error = error_msg
            logger.error(error_msg)
            return False

    async def start_video(self, video_file: str = None) -> bool:
        """Start video streaming"""
        try:
            # Ensure connected first
            if not await self.connect_video_stream():
                return False

            # Start streaming
            success = await start_video_stream(video_file or st.session_state.current_video_file)

            if success:
                st.session_state.video_streaming = True
                st.session_state.video_error = None
                if video_file:
                    st.session_state.current_video_file = video_file
                logger.info(
                    f"Video streaming started: {st.session_state.current_video_file}")
                return True
            else:
                error_msg = "Failed to start video streaming"
                st.session_state.video_error = error_msg
                logger.error(error_msg)
                return False

        except Exception as e:
            error_msg = f"Video start error: {e}"
            st.session_state.video_error = error_msg
            logger.error(error_msg)
            return False

    async def stop_video(self) -> bool:
        """Stop video streaming"""
        try:
            success = await stop_video_stream()

            if success:
                st.session_state.video_streaming = False
                st.session_state.video_error = None
                logger.info("Video streaming stopped")
                return True
            else:
                error_msg = "Failed to stop video streaming"
                st.session_state.video_error = error_msg
                logger.error(error_msg)
                return False

        except Exception as e:
            error_msg = f"Video stop error: {e}"
            st.session_state.video_error = error_msg
            logger.error(error_msg)
            return False

    def get_current_frame(self) -> Optional[CctvFrame]:
        """Get the latest video frame"""
        try:
            frame = get_latest_video_frame()
            if frame:
                st.session_state.last_frame_time = frame.received_at
            return frame
        except Exception as e:
            logger.error(f"Error getting video frame: {e}")
            return None

    def get_streaming_stats(self) -> dict:
        """Get video streaming statistics"""
        try:
            return get_video_stats()
        except Exception as e:
            logger.error(f"Error getting video stats: {e}")
            return {}


def create_video_controls(video_manager: VideoDisplayManager):
    """Create video control buttons"""
    st.subheader("📹 Video Stream Controls")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        # Video file selection
        # Based on mock server README
        available_videos = ["sample1.mp4", "sample2.mp4"]
        selected_video = st.selectbox(
            "Select Video File",
            available_videos,
            index=available_videos.index(st.session_state.current_video_file)
            if st.session_state.current_video_file in available_videos else 0
        )

    with col2:
        if st.button("▶️ Start Stream", disabled=st.session_state.video_streaming):
            with st.spinner("Starting video stream..."):
                success = asyncio.run(
                    video_manager.start_video(selected_video))
                if success:
                    st.success("Video stream started!")
                    st.rerun()
                else:
                    st.error(
                        f"Failed to start stream: {st.session_state.video_error}")

    with col3:
        if st.button("⏹️ Stop Stream", disabled=not st.session_state.video_streaming):
            with st.spinner("Stopping video stream..."):
                success = asyncio.run(video_manager.stop_video())
                if success:
                    st.success("Video stream stopped!")
                    st.rerun()
                else:
                    st.error(
                        f"Failed to stop stream: {st.session_state.video_error}")


def create_video_display(video_manager: VideoDisplayManager, alert_severity: str = "normal"):
    """Create the main video display with optional alert border"""

    # Get current frame
    current_frame = video_manager.get_current_frame()

    # Determine border style based on alert severity
    border_styles = {
        "normal": "border: 4px solid #28a745;",  # Green - thicker
        # Blue with glow
        "INFO": "border: 6px solid #17a2b8; box-shadow: 0 0 10px rgba(23, 162, 184, 0.5);",
        # Yellow with glow and pulse
        "WARN": "border: 8px solid #ffc107; box-shadow: 0 0 15px rgba(255, 193, 7, 0.7); animation: pulse-warn 2s infinite;",
        # Red thick blinking with strong glow
        "EMERGENCY": "border: 12px solid #dc3545; box-shadow: 0 0 25px rgba(220, 53, 69, 0.9); animation: blink-emergency 0.8s infinite;"
    }

    border_style = border_styles.get(alert_severity, border_styles["normal"])

    # CSS for animations - enhanced with more dramatic effects
    if alert_severity in ["WARN", "EMERGENCY"]:
        st.markdown("""
        <style>
        @keyframes blink-emergency {
            0% { 
                border-color: #dc3545; 
                box-shadow: 0 0 25px rgba(220, 53, 69, 0.9);
            }
            50% { 
                border-color: #ff1744; 
                box-shadow: 0 0 35px rgba(255, 23, 68, 1.0);
            }
            100% { 
                border-color: #dc3545; 
                box-shadow: 0 0 25px rgba(220, 53, 69, 0.9);
            }
        }
        
        @keyframes pulse-warn {
            0% { 
                border-color: #ffc107; 
                box-shadow: 0 0 15px rgba(255, 193, 7, 0.7);
            }
            50% { 
                border-color: #ffeb3b; 
                box-shadow: 0 0 25px rgba(255, 235, 59, 0.9);
            }
            100% { 
                border-color: #ffc107; 
                box-shadow: 0 0 15px rgba(255, 193, 7, 0.7);
            }
        }
        </style>
        """, unsafe_allow_html=True)

    # Video display container
    video_container = st.container()

    with video_container:
        if current_frame and current_frame.image_data:
            try:
                # Decode base64 image
                image_data = base64.b64decode(current_frame.image_data)

                # Display image with border - constrained size
                st.markdown(f"""
                <div style="{border_style} border-radius: 10px; padding: 10px; background-color: #000; max-width: 640px; margin: 0 auto;">
                    <img src="data:image/jpeg;base64,{current_frame.image_data}" 
                         style="width: 100%; max-width: 600px; height: auto; display: block; border-radius: 5px;">
                </div>
                """, unsafe_allow_html=True)

                # Frame info
                st.caption(f"📹 Frame #{current_frame.frame_number} from {current_frame.video_file_name} "
                           f"(Received: {current_frame.received_at.strftime('%H:%M:%S')})")

            except Exception as e:
                st.error(f"Error displaying video frame: {e}")
                _show_no_video_placeholder(border_style)
        else:
            _show_no_video_placeholder(border_style)


def _show_no_video_placeholder(border_style: str):
    """Show placeholder when no video is available"""
    st.markdown(f"""
    <div style="{border_style} border-radius: 10px; padding: 40px; background-color: #f8f9fa; text-align: center; max-width: 640px; margin: 0 auto; min-height: 300px; display: flex; flex-direction: column; justify-content: center;">
        <h3 style="color: #6c757d; margin: 0;">📹 No Video Stream</h3>
        <p style="color: #6c757d; margin: 10px 0 0 0;">Click "Start Stream" to begin video streaming</p>
    </div>
    """, unsafe_allow_html=True)


def create_video_stats(video_manager: VideoDisplayManager):
    """Create video statistics display"""
    stats = video_manager.get_streaming_stats()

    if stats:
        st.subheader("📊 Video Stream Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Connected", "✅ Yes" if stats.get(
                'connected') else "❌ No")

        with col2:
            st.metric("Streaming", "🔴 Live" if stats.get(
                'streaming') else "⏸️ Stopped")

        with col3:
            st.metric("Total Frames", stats.get('total_frames_received', 0))

        with col4:
            st.metric(
                "Buffer Size", f"{stats.get('buffer_size', 0)}/{settings.video_frame_buffer_size}")

        # Additional info
        if stats.get('current_video'):
            st.info(f"📁 Current Video: {stats['current_video']}")

        if stats.get('last_frame_time'):
            time_ago = datetime.utcnow() - stats['last_frame_time']
            if time_ago.total_seconds() < 60:
                st.success(
                    f"🕒 Last frame: {int(time_ago.total_seconds())} seconds ago")
            else:
                st.warning(
                    f"🕒 Last frame: {int(time_ago.total_seconds()//60)} minutes ago")

        if stats.get('error_message'):
            st.error(f"❌ Error: {stats['error_message']}")


def render_video_section(alert_severity: str = "normal"):
    """Main function to render the complete video section"""

    # Initialize video manager
    video_manager = VideoDisplayManager()

    st.header("📹 Live Video Stream")

    # Show error if any
    if st.session_state.video_error:
        st.error(f"❌ {st.session_state.video_error}")

    # Video controls
    create_video_controls(video_manager)

    st.markdown("---")

    # Main video display
    create_video_display(video_manager, alert_severity)

    st.markdown("---")

    # Statistics
    create_video_stats(video_manager)

    # Auto-refresh for live streaming
    if st.session_state.video_streaming:
        time.sleep(1)  # Wait 1 second
        st.rerun()  # Refresh to get new frames
