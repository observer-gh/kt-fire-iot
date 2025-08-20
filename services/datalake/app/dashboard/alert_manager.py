import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Alert thresholds based on actual DECIMAL precision
SENSOR_THRESHOLDS = {
    "temperature": {"HIGH": 40.00, "CRITICAL": 60.00},    # DECIMAL(6,2)
    "humidity": {"HIGH": 90.0, "CRITICAL": 95.0},          # DECIMAL(5,2)
    "smoke_density": {"HIGH": 0.500, "CRITICAL": 1.000},   # DECIMAL(6,3)
    "co_level": {"HIGH": 30.000, "CRITICAL": 50.000},      # DECIMAL(6,3)
    "gas_level": {"HIGH": 100.000, "CRITICAL": 200.000}    # DECIMAL(6,3)
}

class AlertManager:
    """Manage alerts and data quality monitoring"""
    
    def __init__(self):
        self.active_alerts = []
        
    def detect_alerts(self, sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect alerts from sensor readings - handle NULL values"""
        alerts = []
        
        # Only check sensors that have non-NULL values
        sensor_fields = {
            'temperature': sensor_data.get('temperature'),
            'humidity': sensor_data.get('humidity'),
            'smoke_density': sensor_data.get('smoke_density'),
            'co_level': sensor_data.get('co_level'),
            'gas_level': sensor_data.get('gas_level')
        }
        
        for sensor_type, value in sensor_fields.items():
            if value is None:  # Skip NULL values
                continue
                
            if sensor_type in SENSOR_THRESHOLDS:
                thresholds = SENSOR_THRESHOLDS[sensor_type]
                
                if value >= thresholds["CRITICAL"]:
                    alerts.append({
                        'equipment_data_id': sensor_data['equipment_data_id'],
                        'equipment_id': sensor_data.get('equipment_id', 'UNKNOWN'),
                        'facility_id': sensor_data.get('facility_id', 'UNKNOWN'),
                        'equipment_location': sensor_data.get('equipment_location', 'UNKNOWN'),
                        'sensor_type': sensor_type,
                        'value': value,
                        'threshold': thresholds["CRITICAL"],
                        'alert_level': 'CRITICAL',
                        'measured_at': sensor_data.get('measured_at'),
                        'color': '#dc3545'  # Red
                    })
                elif value >= thresholds["HIGH"]:
                    alerts.append({
                        'equipment_data_id': sensor_data['equipment_data_id'],
                        'equipment_id': sensor_data.get('equipment_id', 'UNKNOWN'),
                        'facility_id': sensor_data.get('facility_id', 'UNKNOWN'),
                        'equipment_location': sensor_data.get('equipment_location', 'UNKNOWN'),
                        'sensor_type': sensor_type,
                        'value': value,
                        'threshold': thresholds["HIGH"],
                        'alert_level': 'HIGH',
                        'measured_at': sensor_data.get('measured_at'),
                        'color': '#ffc107'  # Yellow
                    })
        
        return alerts
        
    def get_data_quality_alerts(self, sensor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for data quality issues"""
        quality_alerts = []
        
        # Check for missing equipment_id
        if not sensor_data.get('equipment_id'):
            quality_alerts.append({
                'type': 'MISSING_EQUIPMENT_ID',
                'equipment_data_id': sensor_data['equipment_data_id'],
                'message': 'Equipment ID is missing',
                'severity': 'WARN'
            })
            
        # Check for missing facility_id
        if not sensor_data.get('facility_id'):
            quality_alerts.append({
                'type': 'MISSING_FACILITY_ID', 
                'equipment_data_id': sensor_data['equipment_data_id'],
                'message': 'Facility ID is missing',
                'severity': 'WARN'
            })
            
        # Check for missing sensor readings
        sensor_fields = ['temperature', 'humidity', 'smoke_density', 'co_level', 'gas_level']
        missing_sensors = [field for field in sensor_fields if sensor_data.get(field) is None]
        
        if len(missing_sensors) > 3:  # If more than 3 sensors are missing
            quality_alerts.append({
                'type': 'MISSING_SENSOR_DATA',
                'equipment_data_id': sensor_data['equipment_data_id'],
                'message': f'Multiple sensors missing: {", ".join(missing_sensors)}',
                'severity': 'WARN'
            })
            
        return quality_alerts
        
    def format_alert_message(self, alert_data: Dict[str, Any]) -> str:
        """Format alert for display"""
        equipment_info = f"Equipment: {alert_data.get('equipment_id', 'UNKNOWN')}"
        location_info = f"Location: {alert_data.get('equipment_location', 'UNKNOWN')}"
        sensor_info = f"{alert_data['sensor_type'].title()}: {alert_data['value']}"
        threshold_info = f"Threshold: {alert_data['threshold']}"
        
        return f"🚨 {alert_data['alert_level']} - {equipment_info} | {location_info} | {sensor_info} | {threshold_info}"
    
    def get_alert_summary(self, sensor_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of all alerts from sensor data"""
        all_alerts = []
        critical_count = 0
        high_count = 0
        
        for sensor_data in sensor_data_list:
            alerts = self.detect_alerts(sensor_data)
            all_alerts.extend(alerts)
            
            for alert in alerts:
                if alert['alert_level'] == 'CRITICAL':
                    critical_count += 1
                elif alert['alert_level'] == 'HIGH':
                    high_count += 1
        
        return {
            'total_alerts': len(all_alerts),
            'critical_alerts': critical_count,
            'high_alerts': high_count,
            'alerts': all_alerts
        }
    
    def get_alert_distribution(self, sensor_data_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of alerts by sensor type"""
        alert_distribution = {
            'temperature': 0,
            'humidity': 0,
            'smoke_density': 0,
            'co_level': 0,
            'gas_level': 0
        }
        
        for sensor_data in sensor_data_list:
            alerts = self.detect_alerts(sensor_data)
            for alert in alerts:
                sensor_type = alert['sensor_type']
                if sensor_type in alert_distribution:
                    alert_distribution[sensor_type] += 1
        
        return alert_distribution
    
    def get_equipment_health_score(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate equipment health score based on sensor readings"""
        score = 100
        issues = []
        
        # Check temperature
        if sensor_data.get('temperature') is not None:
            temp = sensor_data['temperature']
            if temp >= 60.00:
                score -= 40
                issues.append('Critical temperature')
            elif temp >= 40.00:
                score -= 20
                issues.append('High temperature')
            elif temp < 0.00:
                score -= 15
                issues.append('Low temperature')
        
        # Check smoke density
        if sensor_data.get('smoke_density') is not None:
            smoke = sensor_data['smoke_density']
            if smoke >= 1.000:
                score -= 50
                issues.append('Critical smoke level')
            elif smoke >= 0.500:
                score -= 30
                issues.append('High smoke level')
        
        # Check CO level
        if sensor_data.get('co_level') is not None:
            co = sensor_data['co_level']
            if co >= 50.000:
                score -= 45
                issues.append('Critical CO level')
            elif co >= 30.000:
                score -= 25
                issues.append('High CO level')
        
        # Check gas level
        if sensor_data.get('gas_level') is not None:
            gas = sensor_data['gas_level']
            if gas >= 200.000:
                score -= 40
                issues.append('Critical gas level')
            elif gas >= 100.000:
                score -= 20
                issues.append('High gas level')
        
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        # Determine health status
        if score >= 80:
            status = 'HEALTHY'
            color = '#28a745'  # Green
        elif score >= 50:
            status = 'WARNING'
            color = '#ffc107'  # Yellow
        else:
            status = 'CRITICAL'
            color = '#dc3545'  # Red
        
        return {
            'score': score,
            'status': status,
            'color': color,
            'issues': issues
        }
