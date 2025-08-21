#!/usr/bin/env python3
"""
Video Analysis Service Entry Point
Connects to mock server WebSocket and processes CCTV video frames
"""

from src.main import main
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


if __name__ == "__main__":
    main()
