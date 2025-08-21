from typing import Optional, Tuple
from datetime import datetime
import uuid
from .models import RawSensorData, ProcessedSensorData, SensorType, AlertSeverity


class DataProcessor:
    """Handles data cleaning, validation, and anomaly detection"""

    # Thresholds for different sensor types
    THRESHOLDS = {
        "temperature": {
            "min": -50.0,
            "max": 100.0,
            "warn": 80.0,
            "emergency": 100.0
        },
        "humidity": {
            "min": 0.0,
            "max": 100.0,
            "warn": 95.0,
            "emergency": 97.5
        },
        "smoke_density": {
            "min": 0.0,
            "max": 999.999,
            "warn": 0.200,
            "emergency": 0.600
        },
        "co_level": {
            "min": 0.0,
            "max": 999.999,
            "warn": 0.100,
            "emergency": 0.300
        },
        "gas_level": {
            "min": 0.0,
            "max": 999.999,
            "warn": 0.150,
            "emergency": 0.475
        }
    }

    @classmethod
    def process_sensor_data(cls, raw_data: RawSensorData) -> ProcessedSensorData:
        """Clean, validate, and process raw sensor data"""

        # Clean and validate values
        cleaned_data = cls._clean_values(raw_data)

        # Check for anomalies using cleaned data
        is_anomaly, anomaly_metric, anomaly_value, anomaly_threshold, severity = cls._check_anomalies(cleaned_data)

        # Create processed data
        processed_data = ProcessedSensorData(
            equipment_id=raw_data.equipment_id,
            facility_id=raw_data.facility_id,
            equipment_location=raw_data.equipment_location,
            measured_at=raw_data.measured_at,
            ingested_at=datetime.utcnow(),
            temperature=cleaned_data.temperature,
            humidity=cleaned_data.humidity,
            smoke_density=cleaned_data.smoke_density,
            co_level=cleaned_data.co_level,
            gas_level=cleaned_data.gas_level,
            is_anomaly=is_anomaly,
            anomaly_metric=anomaly_metric,
            anomaly_value=anomaly_value,
            anomaly_threshold=anomaly_threshold,
            severity=severity or "WARN",
            metadata=raw_data.metadata
        )

        return processed_data

    @classmethod
    def _clean_values(cls, raw_data: RawSensorData) -> RawSensorData:
        """Clean and validate sensor values"""
        cleaned_data = raw_data.copy()
        
        # Clean temperature
        if raw_data.temperature is not None:
            thresholds = cls.THRESHOLDS["temperature"]
            if raw_data.temperature < thresholds["min"]:
                cleaned_data.temperature = thresholds["min"]
            elif raw_data.temperature > thresholds["max"]:
                cleaned_data.temperature = thresholds["max"]

        # Clean humidity
        if raw_data.humidity is not None:
            thresholds = cls.THRESHOLDS["humidity"]
            if raw_data.humidity < thresholds["min"]:
                cleaned_data.humidity = thresholds["min"]
            elif raw_data.humidity > thresholds["max"]:
                cleaned_data.humidity = thresholds["max"]

        # Clean smoke_density
        if raw_data.smoke_density is not None:
            thresholds = cls.THRESHOLDS["smoke_density"]
            if raw_data.smoke_density < thresholds["min"]:
                cleaned_data.smoke_density = thresholds["min"]
            elif raw_data.smoke_density > thresholds["max"]:
                cleaned_data.smoke_density = thresholds["max"]

        # Clean co_level
        if raw_data.co_level is not None:
            thresholds = cls.THRESHOLDS["co_level"]
            if raw_data.co_level < thresholds["min"]:
                cleaned_data.co_level = thresholds["min"]
            elif raw_data.co_level > thresholds["max"]:
                cleaned_data.co_level = thresholds["max"]

        # Clean gas_level
        if raw_data.gas_level is not None:
            thresholds = cls.THRESHOLDS["gas_level"]
            if raw_data.gas_level < thresholds["min"]:
                cleaned_data.gas_level = thresholds["min"]
            elif raw_data.gas_level > thresholds["max"]:
                cleaned_data.gas_level = thresholds["max"]

        return cleaned_data

    @classmethod
    def _check_anomalies(cls, data: RawSensorData) -> Tuple[bool, Optional[str], Optional[float], Optional[float], Optional[str]]:
        """Check if any sensor values trigger anomalies"""
        
        # Check temperature
        if data.temperature is not None:
            thresholds = cls.THRESHOLDS["temperature"]
            if data.temperature >= thresholds["emergency"]:
                print(f"🚨 온도 비상 이상치: {data.temperature} >= {thresholds['emergency']}")
                return True, "temperature", data.temperature, thresholds["emergency"], "EMERGENCY"
            elif data.temperature >= thresholds["warn"]:
                print(f"⚠️ 온도 경고 이상치: {data.temperature} >= {thresholds['warn']}")
                return True, "temperature", data.temperature, thresholds["warn"], "WARN"

        # Check humidity
        if data.humidity is not None:
            thresholds = cls.THRESHOLDS["humidity"]
            if data.humidity >= thresholds["emergency"]:
                print(f"🚨 습도 비상 이상치: {data.humidity} >= {thresholds['emergency']}")
                return True, "humidity", data.humidity, thresholds["emergency"], "EMERGENCY"
            elif data.humidity >= thresholds["warn"]:
                print(f"⚠️ 습도 경고 이상치: {data.humidity} >= {thresholds['warn']}")
                return True, "humidity", data.humidity, thresholds["warn"], "WARN"

        # Check smoke_density
        if data.smoke_density is not None:
            thresholds = cls.THRESHOLDS["smoke_density"]
            if data.smoke_density >= thresholds["emergency"]:
                print(f"🚨 연기 비상 이상치: {data.smoke_density} >= {thresholds['emergency']}")
                return True, "smoke_density", data.smoke_density, thresholds["emergency"], "EMERGENCY"
            elif data.smoke_density >= thresholds["warn"]:
                print(f"⚠️ 연기 경고 이상치: {data.smoke_density} >= {thresholds['warn']}")
                return True, "smoke_density", data.smoke_density, thresholds["warn"], "WARN"

        # Check co_level
        if data.co_level is not None:
            thresholds = cls.THRESHOLDS["co_level"]
            if data.co_level >= thresholds["emergency"]:
                print(f"🚨 CO 비상 이상치: {data.co_level} >= {thresholds['emergency']}")
                return True, "co_level", data.co_level, thresholds["emergency"], "EMERGENCY"
            elif data.co_level >= thresholds["warn"]:
                print(f"⚠️ CO 경고 이상치: {data.co_level} >= {thresholds['warn']}")
                return True, "co_level", data.co_level, thresholds["warn"], "WARN"

        # Check gas_level
        if data.gas_level is not None:
            thresholds = cls.THRESHOLDS["gas_level"]
            if data.gas_level >= thresholds["emergency"]:
                print(f"🚨 가스 비상 이상치: {data.gas_level} >= {thresholds['emergency']}")
                return True, "gas_level", data.gas_level, thresholds["emergency"], "EMERGENCY"
            elif data.gas_level >= thresholds["warn"]:
                print(f"⚠️ 가스 경고 이상치: {data.gas_level} >= {thresholds['warn']}")
                return True, "gas_level", data.gas_level, thresholds["warn"], "WARN"

        # 이상치가 없을 때는 로그 출력하지 않음
        return False, None, None, None, None
