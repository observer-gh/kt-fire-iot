import os
from typing import Optional, Literal
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings
    postgres_url: Optional[str] = os.getenv("POSTGRES_URL")
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "fire_iot")
    
    # Redis settings
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Kafka settings
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BROKERS", "kafka:29092")
    kafka_topic_anomaly: str = os.getenv("KAFKA_TOPIC_ANOMALY", "fire-iot.anomaly-detected")
    kafka_topic_data_saved: str = os.getenv("KAFKA_TOPIC_DATA_SAVED", "fire-iot.sensorDataSaved")
    kafka_topic_sensor_data: str = os.getenv("KAFKA_TOPIC_SENSOR_DATA", "fire-iot.sensor-data")
    
    # Storage settings
    storage_type: Literal["production", "mock"] = os.getenv("STORAGE_TYPE", "mock")
    batch_size: int = int(os.getenv("BATCH_SIZE", "100"))
    batch_interval_minutes: int = int(os.getenv("BATCH_INTERVAL_MINUTES", "10"))
    storage_path: str = os.getenv("STORAGE_PATH", "./local_storage")
    
    # Service settings
    service_port: int = int(os.getenv("SERVICE_PORT", "8080"))
    service_host: str = os.getenv("SERVICE_HOST", "0.0.0.0")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
