import streamlit as st
import asyncio
import time
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go

from app.dashboard.data_manager import FireSensorDataManager
from app.dashboard.alert_manager import AlertManager
from app.dashboard.charts import SensorCharts
from app.config import settings

# Page configuration
st.set_page_config(
    page_title="Fire Safety Monitoring Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def get_services():
    """Initialize dashboard services"""
    return {
        'data_manager': FireSensorDataManager(),
        'alert_manager': AlertManager(),
        'charts': SensorCharts()
    }

def main():
    st.title("🚨 Real-time Fire Safety Monitoring Dashboard")
    
    # Get services
    services = get_services()
    data_manager = services['data_manager']
    alert_manager = services['alert_manager']
    charts = services['charts']
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔧 Dashboard Controls")
        
        # Facility filter
        facilities = ['All'] + data_manager.get_facilities()
        facility_filter = st.selectbox("Select Facility", facilities, index=0)
        
        # Time range filter
        time_range = st.selectbox("Time Range", ["Real-time", "1 Hour", "24 Hours", "7 Days"])
        
        # Auto refresh
        refresh_interval = settings.dashboard_refresh_interval_seconds
        auto_refresh = st.checkbox(f"Auto Refresh ({refresh_interval}s)", value=True)
        
        # Sensor selection
        st.subheader("📊 Sensor Selection")
        show_temperature = st.checkbox("Temperature", value=True)
        show_humidity = st.checkbox("Humidity", value=True)
        show_smoke = st.checkbox("Smoke Density", value=True)
        show_co = st.checkbox("CO Level", value=True)
        show_gas = st.checkbox("Gas Level", value=True)
        
        # Refresh button
        if st.button("🔄 Manual Refresh"):
            st.rerun()
    
    # Main dashboard layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_facilities = len(data_manager.get_facilities())
        st.metric("🏢 Total Facilities", total_facilities)
    
    with col2:
        active_alerts = len(alert_manager.active_alerts)
        st.metric("🚨 Active Alerts", active_alerts, delta=None)
    
    with col3:
        online_equipment = data_manager.get_online_equipment_count()
        st.metric("🟢 Online Equipment", online_equipment)
    
    with col4:
        total_equipment = data_manager.get_equipment_count()
        st.metric("📡 Total Equipment", total_equipment)
    
    # Real-time sensor charts
    st.subheader("📊 Real-time Sensor Readings")
    
    # Get real-time data
    facility_id = None if facility_filter == 'All' else facility_filter
    realtime_data = data_manager.get_realtime_data(facility_id=facility_id)
    
    if realtime_data:
        # Get latest readings for each equipment
        equipment_status = data_manager.get_equipment_status()
        
        # Layout for sensor charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Temperature and humidity charts
            if equipment_status and show_temperature:
                latest_temp = next((eq['temperature'] for eq in equipment_status if eq.get('temperature') is not None), None)
                if latest_temp is not None:
                    temp_gauge = charts.create_realtime_gauge(
                        'temperature', latest_temp, 40.00, "Current Temperature (°C)"
                    )
                    st.plotly_chart(temp_gauge, use_container_width=True)
            
            if equipment_status and show_humidity:
                latest_humidity = next((eq['humidity'] for eq in equipment_status if eq.get('humidity') is not None), None)
                if latest_humidity is not None:
                    humidity_gauge = charts.create_realtime_gauge(
                        'humidity', latest_humidity, 90.0, "Current Humidity (%)"
                    )
                    st.plotly_chart(humidity_gauge, use_container_width=True)
        
        with chart_col2:
            # Gas sensors charts
            if equipment_status and show_smoke:
                latest_smoke = next((eq['smoke_density'] for eq in equipment_status if eq.get('smoke_density') is not None), None)
                if latest_smoke is not None:
                    smoke_gauge = charts.create_realtime_gauge(
                        'smoke_density', latest_smoke, 0.500, "Current Smoke Density"
                    )
                    st.plotly_chart(smoke_gauge, use_container_width=True)
            
            if equipment_status and show_co:
                latest_co = next((eq['co_level'] for eq in equipment_status if eq.get('co_level') is not None), None)
                if latest_co is not None:
                    co_gauge = charts.create_realtime_gauge(
                        'co_level', latest_co, 30.000, "Current CO Level (ppm)"
                    )
                    st.plotly_chart(co_gauge, use_container_width=True)
        
        # Time series chart
        st.subheader("📈 Historical Sensor Data")
        
        # Determine time range for historical data
        end_time = datetime.now()
        if time_range == "1 Hour":
            start_time = end_time - timedelta(hours=1)
        elif time_range == "24 Hours":
            start_time = end_time - timedelta(days=1)
        elif time_range == "7 Days":
            start_time = end_time - timedelta(days=7)
        else:  # Real-time
            start_time = end_time - timedelta(hours=1)
        
        historical_data = data_manager.get_historical_data(start_time, end_time, facility_id)
        
        if historical_data:
            # Filter sensor types based on selection
            selected_sensors = []
            if show_temperature:
                selected_sensors.append('temperature')
            if show_humidity:
                selected_sensors.append('humidity')
            if show_smoke:
                selected_sensors.append('smoke_density')
            if show_co:
                selected_sensors.append('co_level')
            if show_gas:
                selected_sensors.append('gas_level')
            
            time_series_chart = charts.create_time_series_chart(historical_data, selected_sensors)
            st.plotly_chart(time_series_chart, use_container_width=True)
        else:
            st.info("No historical data available for the selected time range.")
    
    # Equipment status overview
    st.subheader("📊 Equipment Status Overview")
    
    if equipment_status:
        # Create equipment summary table
        equipment_df = pd.DataFrame(equipment_status)
        st.dataframe(equipment_df, use_container_width=True)
    else:
        st.info("No equipment data available.")
    
    # Active alerts
    st.subheader("🚨 Active Alerts")
    
    if realtime_data:
        # Detect alerts from current data
        alert_summary = alert_manager.get_alert_summary(realtime_data)
        
        if alert_summary['total_alerts'] > 0:
            # Display alert summary
            alert_col1, alert_col2, alert_col3 = st.columns(3)
            
            with alert_col1:
                st.metric("Total Alerts", alert_summary['total_alerts'])
            
            with alert_col2:
                st.metric("Critical Alerts", alert_summary['critical_alerts'], delta=None)
            
            with alert_col3:
                st.metric("High Alerts", alert_summary['high_alerts'], delta=None)
            
            # Display individual alerts
            for alert in alert_summary['alerts']:
                alert_message = alert_manager.format_alert_message(alert)
                st.error(alert_message)
            
            # Alert distribution chart
            alert_distribution = alert_manager.get_alert_distribution(realtime_data)
            alert_chart = charts.create_alert_distribution_chart(alert_distribution)
            st.plotly_chart(alert_chart, use_container_width=True)
        else:
            st.success("✅ No active alerts detected. All systems are operating normally.")
    
    # Data quality monitoring
    st.subheader("🔍 Data Quality Monitoring")
    
    if realtime_data:
        # Check data quality for each reading
        quality_issues = []
        for sensor_data in realtime_data:
            quality_alerts = alert_manager.get_data_quality_alerts(sensor_data)
            quality_issues.extend(quality_alerts)
        
        if quality_issues:
            st.warning(f"⚠️ {len(quality_issues)} data quality issues detected")
            
            # Display quality issues
            for issue in quality_issues[:10]:  # Show first 10 issues
                st.write(f"• {issue['message']} (ID: {issue['equipment_data_id']})")
        else:
            st.success("✅ All data quality checks passed")
    
    # Equipment health scores
    if equipment_status:
        st.subheader("💚 Equipment Health Status")
        
        health_scores = []
        for equipment in equipment_status:
            health = alert_manager.get_equipment_health_score(equipment)
            health_scores.append({
                'equipment_id': equipment.get('equipment_id', 'Unknown'),
                'facility_id': equipment.get('facility_id', 'Unknown'),
                'location': equipment.get('equipment_location', 'Unknown'),
                'health_score': health['score'],
                'status': health['status'],
                'color': health['color'],
                'issues': ', '.join(health['issues']) if health['issues'] else 'None'
            })
        
        if health_scores:
            health_df = pd.DataFrame(health_scores)
            
            # Color code the health scores
            def color_health_score(val):
                if val >= 80:
                    return 'background-color: #d4edda'  # Green
                elif val >= 50:
                    return 'background-color: #fff3cd'  # Yellow
                else:
                    return 'background-color: #f8d7da'  # Red
            
            styled_df = health_df.style.map(color_health_score, subset=['health_score'])
            st.dataframe(styled_df, use_container_width=True)
    
    # Footer with last update time
    st.markdown("---")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
