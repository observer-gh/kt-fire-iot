#!/usr/bin/env python3
"""
Fire Safety Monitoring Dashboard Runner

This script runs the Streamlit dashboard for the DataLake service.
The dashboard displays real-time sensor data from fire detection systems.

Usage:
    streamlit run run_dashboard.py
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Set environment variables for the dashboard
os.environ.setdefault('STREAMLIT_SERVER_PORT', '8501')
os.environ.setdefault('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')

# Import and run the dashboard
try:
    from dashboard.main_dashboard import main as dashboard_main
    
    # Run the dashboard
    dashboard_main()
    
except ImportError as e:
    st.error(f"Error importing dashboard: {e}")
    st.info("Make sure all dependencies are installed: pip install -r requirements.txt")
except Exception as e:
    st.error(f"Error running dashboard: {e}")
