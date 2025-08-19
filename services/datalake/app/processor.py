from typing import Optional
from .models import RawSensorData, ProcessedSensorData, SensorType, AlertSeverity


class DataProcessor:
    """Handles data cleaning, validation, and alert detection"""

    # Thresholds for different sensor types
    THRESHOLDS = {
        SensorType.TEMPERATURE: {
            "min": -50.0,
            "max": 100.0,
            "alert_high": 80.0,
            "alert_critical": 95.0
        },
        SensorType.HUMIDITY: {
            "min": 0.0,
            "max": 100.0,
            "alert_high": 90.0,
            "alert_critical": 98.0
        },
        SensorType.SMOKE: {
            "min": 0.0,
            "max": 1000.0,
            "alert_high": 100.0,
            "alert_critical": 500.0
        },
        SensorType.CO2: {
            "min": 300.0,
            "max": 5000.0,
            "alert_high": 1000.0,
            "alert_critical": 2000.0
        },
        SensorType.PRESSURE: {
            "min": 900.0,
            "max": 1100.0,
            "alert_high": 1050.0,
            "alert_critical": 1080.0
        }
    }

    @classmethod
    def process_sensor_data(cls, raw_data: RawSensorData) -> ProcessedSensorData:
        """Clean, validate, and process raw sensor data"""

        # Validate sensor type
        if raw_data.sensor_type not in cls.THRESHOLDS:
            raise ValueError(
                f"Unsupported sensor type: {raw_data.sensor_type}")

        # Get thresholds for this sensor type
        thresholds = cls.THRESHOLDS[raw_data.sensor_type]

        # Clean and validate value
        cleaned_value = cls._clean_value(raw_data.value, thresholds)

        # Check for alerts
        is_alert, severity = cls._check_alerts(cleaned_value, thresholds)

        # Create processed data
        processed_data = ProcessedSensorData(
            station_id=raw_data.station_id,
            sensor_type=raw_data.sensor_type,
            value=cleaned_value,
            timestamp=raw_data.timestamp,
            is_alert=is_alert,
            severity=severity,
            metadata=raw_data.metadata
        )

        return processed_data

    @classmethod
    def _clean_value(cls, value: float, thresholds: dict) -> float:
        """Clean and validate sensor value"""
        # Check bounds
        if value < thresholds["min"]:
            return thresholds["min"]
        elif value > thresholds["max"]:
            return thresholds["max"]

        return value

    @classmethod
    def _check_alerts(cls, value: float, thresholds: dict) -> tuple[bool, Optional[AlertSeverity]]:
        """Check if value triggers alerts"""
        if value >= thresholds["alert_critical"]:
            return True, AlertSeverity.CRITICAL
        elif value >= thresholds["alert_high"]:
            return True, AlertSeverity.HIGH
        else:
            return False, None
