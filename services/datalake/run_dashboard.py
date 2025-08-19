#!/usr/bin/env python3
"""
Fire Safety Monitoring Dashboard Runner

This script runs the Streamlit dashboard for the DataLake service.
The dashboard displays real-time sensor data from fire detection systems.

Usage:
    python run_dashboard.py
    streamlit run run_dashboard.py
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main function to run the dashboard"""
    
    # Add the app directory to Python path
    app_dir = Path(__file__).parent / "app"
    sys.path.insert(0, str(app_dir))
    
    # Set environment variables for the dashboard
    os.environ.setdefault('STREAMLIT_SERVER_PORT', '8501')
    os.environ.setdefault('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')
    
    # Import and run the dashboard
    try:
        from app.dashboard.main_dashboard import main as dashboard_main
        
        print("🚀 Starting Fire Safety Monitoring Dashboard...")
        print("📊 Dashboard will be available at: http://localhost:8501")
        print("🔧 Press Ctrl+C to stop the dashboard")
        
        # Run the dashboard
        dashboard_main()
        
    except ImportError as e:
        print(f"❌ Error importing dashboard: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
