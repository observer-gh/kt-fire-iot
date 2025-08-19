#!/bin/bash

# Fire Safety Monitoring Dashboard Starter Script

echo "🚨 Starting Fire Safety Monitoring Dashboard..."
echo "📊 This will start the Streamlit dashboard for the DataLake service"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if requirements are installed
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Please run from the datalake directory."
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -r requirements.txt

# Start the dashboard
echo "🚀 Launching dashboard..."
echo "📱 Dashboard will be available at: http://localhost:8501"
echo "🔧 Press Ctrl+C to stop the dashboard"
echo ""

# Run the dashboard
streamlit run run_dashboard.py --server.port=8501 --server.address=0.0.0.0
