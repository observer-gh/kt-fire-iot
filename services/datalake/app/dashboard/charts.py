import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class SensorCharts:
    """Generate interactive charts for sensor data"""
    
    def __init__(self):
        self.colors = {
            'temperature': '#ff6b6b',
            'humidity': '#4ecdc4',
            'smoke_density': '#45b7d1',
            'co_level': '#96ceb4',
            'gas_level': '#feca57'
        }
    
    def create_realtime_gauge(self, sensor_type: str, current_value: float, threshold: float, title: str = None) -> go.Figure:
        """Create gauge chart for current sensor reading"""
        if current_value is None:
            current_value = 0
            
        # Determine gauge colors based on sensor type and value
        if sensor_type == 'temperature':
            if current_value >= 60:
                color = '#dc3545'  # Red
            elif current_value >= 40:
                color = '#ffc107'  # Yellow
            else:
                color = '#28a745'  # Green
        elif sensor_type == 'smoke_density':
            if current_value >= 1.000:
                color = '#dc3545'  # Red
            elif current_value >= 0.500:
                color = '#ffc107'  # Yellow
            else:
                color = '#28a745'  # Green
        elif sensor_type == 'co_level':
            if current_value >= 50.000:
                color = '#dc3545'  # Red
            elif current_value >= 30.000:
                color = '#ffc107'  # Yellow
            else:
                color = '#28a745'  # Green
        else:
            color = self.colors.get(sensor_type, '#6c757d')
        
        # Set gauge range based on sensor type
        if sensor_type == 'temperature':
            max_value = 100
        elif sensor_type == 'humidity':
            max_value = 100
        elif sensor_type == 'smoke_density':
            max_value = 2.000
        elif sensor_type == 'co_level':
            max_value = 100.000
        elif sensor_type == 'gas_level':
            max_value = 500.000
        else:
            max_value = threshold * 2
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title or sensor_type.replace('_', ' ').title()},
            delta={'reference': threshold},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, threshold * 0.7], 'color': '#28a745'},
                    {'range': [threshold * 0.7, threshold], 'color': '#ffc107'},
                    {'range': [threshold, max_value], 'color': '#dc3545'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': threshold
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
        
    def create_time_series_chart(self, historical_data: List[Dict[str, Any]], sensor_types: List[str] = None) -> go.Figure:
        """Create time series chart for multiple sensors"""
        if not historical_data:
            return self._create_empty_chart("No historical data available")
        
        if sensor_types is None:
            sensor_types = ['temperature', 'humidity', 'smoke_density', 'co_level', 'gas_level']
        
        df = pd.DataFrame(historical_data)
        if df.empty:
            return self._create_empty_chart("No data to display")
        
        # Convert measured_at to datetime if it's string
        if 'measured_at' in df.columns:
            df['measured_at'] = pd.to_datetime(df['measured_at'])
            df = df.sort_values('measured_at')
        
        fig = go.Figure()
        
        for sensor_type in sensor_types:
            if sensor_type in df.columns and df[sensor_type].notna().any():
                # Filter out None values
                valid_data = df[df[sensor_type].notna()].copy()
                if not valid_data.empty:
                    fig.add_trace(go.Scatter(
                        x=valid_data['measured_at'],
                        y=valid_data[sensor_type],
                        mode='lines+markers',
                        name=sensor_type.replace('_', ' ').title(),
                        line=dict(color=self.colors.get(sensor_type, '#6c757d')),
                        marker=dict(size=4)
                    ))
        
        fig.update_layout(
            title="Sensor Readings Over Time",
            xaxis_title="Time",
            yaxis_title="Sensor Values",
            height=400,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
        

        
    def create_alert_distribution_chart(self, alert_data: Dict[str, int]) -> go.Figure:
        """Create pie chart for alert severity distribution"""
        if not alert_data or sum(alert_data.values()) == 0:
            return self._create_empty_chart("No alerts to display")
        
        # Filter out zero values
        filtered_data = {k: v for k, v in alert_data.items() if v > 0}
        
        if not filtered_data:
            return self._create_empty_chart("No active alerts")
        
        fig = go.Figure(data=[go.Pie(
            labels=[k.replace('_', ' ').title() for k in filtered_data.keys()],
            values=list(filtered_data.values()),
            hole=0.4,
            marker_colors=[self.colors.get(k, '#6c757d') for k in filtered_data.keys()]
        )])
        
        fig.update_layout(
            title="Alert Distribution by Sensor Type",
            height=400,
            showlegend=True
        )
        
        return fig
        

    
    def create_metrics_dashboard(self, metrics_data: Dict[str, Any]) -> go.Figure:
        """Create a comprehensive metrics dashboard"""
        # Create subplots
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Temperature Distribution', 'Smoke Density Trend', 
                          'Equipment Health Status', 'Alert Summary'),
            specs=[[{"type": "histogram"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # This is a placeholder - in real implementation, you'd populate with actual data
        fig.update_layout(height=600, title_text="Fire Safety Metrics Dashboard")
        
        return fig
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create an empty chart with a message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=300
        )
        return fig
