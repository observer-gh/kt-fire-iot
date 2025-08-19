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
        
    def create_facility_heatmap(self, facility_data: List[Dict[str, Any]]) -> go.Figure:
        """Create heatmap showing sensor status across locations"""
        if not facility_data:
            return self._create_empty_chart("No facility data available")
        
        df = pd.DataFrame(facility_data)
        
        # Create heatmap data
        facilities = df['facility_id'].unique()
        metrics = ['equipment_count', 'total_readings', 'avg_temperature', 'max_smoke_density']
        
        heatmap_data = []
        for facility in facilities:
            facility_info = df[df['facility_id'] == facility].iloc[0]
            row = []
            for metric in metrics:
                value = facility_info.get(metric, 0)
                if pd.isna(value):
                    value = 0
                row.append(value)
            heatmap_data.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=metrics,
            y=facilities,
            colorscale='RdYlGn_r',
            text=[[f"{val:.2f}" if isinstance(val, float) else str(val) for val in row] for row in heatmap_data],
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Facility Status Overview",
            xaxis_title="Metrics",
            yaxis_title="Facilities",
            height=400
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
        
    def create_equipment_status_map(self, equipment_data: List[Dict[str, Any]]) -> go.Figure:
        """Create equipment location map with status indicators"""
        if not equipment_data:
            return self._create_empty_chart("No equipment data available")
        
        df = pd.DataFrame(equipment_data)
        
        # Create scatter plot for equipment locations
        fig = go.Figure()
        
        # Group by facility
        for facility_id in df['facility_id'].unique():
            facility_equipment = df[df['facility_id'] == facility_id]
            
            # Create synthetic coordinates for visualization (in real app, use actual GPS coordinates)
            x_coords = []
            y_coords = []
            status_colors = []
            equipment_names = []
            
            for idx, equipment in facility_equipment.iterrows():
                # Generate synthetic coordinates based on equipment location
                x_coords.append(hash(equipment.get('equipment_location', '')) % 100)
                y_coords.append(hash(equipment.get('equipment_id', '')) % 100)
                
                # Determine status color based on health
                if equipment.get('temperature', 0) > 40 or equipment.get('smoke_density', 0) > 0.5:
                    status_colors.append('#dc3545')  # Red
                elif equipment.get('temperature', 0) > 30 or equipment.get('smoke_density', 0) > 0.2:
                    status_colors.append('#ffc107')  # Yellow
                else:
                    status_colors.append('#28a745')  # Green
                
                equipment_names.append(equipment.get('equipment_id', 'Unknown'))
            
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='markers+text',
                name=facility_id,
                text=equipment_names,
                textposition="top center",
                marker=dict(
                    size=15,
                    color=status_colors,
                    symbol='circle'
                ),
                hovertemplate="<b>%{text}</b><br>" +
                            "Facility: " + facility_id + "<br>" +
                            "Location: %{customdata}<br>" +
                            "<extra></extra>",
                customdata=[eq.get('equipment_location', 'Unknown') for eq in facility_equipment.itertuples()]
            ))
        
        fig.update_layout(
            title="Equipment Status Map",
            xaxis_title="X Coordinate",
            yaxis_title="Y Coordinate",
            height=500,
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
