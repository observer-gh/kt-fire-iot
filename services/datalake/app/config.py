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
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5433"))
    postgres_db: str = os.getenv("POSTGRES_DB", "")
    
    # Redis settings
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_flush_interval_seconds: int = int(os.getenv("REDIS_FLUSH_INTERVAL_SECONDS", "60"))
    
    # Kafka settings
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BROKERS", "localhost:9092")
    kafka_topic_anomaly: str = os.getenv("KAFKA_TOPIC_ANOMALY", "dataLake.sensorDataAnomalyDetected")
    kafka_topic_data_saved: str = os.getenv("KAFKA_TOPIC_DATA_SAVED", "dataLake.sensorDataSaved")
    kafka_topic_fire_detection: str = os.getenv("KAFKA_TOPIC_FIRE_DETECTION", "controlTower.fireDetectionNotified")
    
    # Event Hub settings (for Azure cloud deployment)
    eventhub_connection_string: Optional[str] = os.getenv("EVENTHUB_CONN")
    eventhub_consumer_group: str = os.getenv("EVENTHUB_CONSUMER_GROUP", "datalake-dashboard")
    
    # Mock Server settings
    mock_server_url: str = os.getenv("MOCK_SERVER_URL", "http://localhost:8081")
    mock_server_data_count: int = int(os.getenv("MOCK_SERVER_DATA_COUNT", "10"))
    mock_server_data_fetch_interval_seconds: int = int(os.getenv("MOCK_SERVER_DATA_FETCH_INTERVAL", "5"))
    mock_server_stream_data_count: int = int(os.getenv("MOCK_SERVER_STREAM_COUNT", "5"))
    mock_server_batch_data_count: int = int(os.getenv("MOCK_SERVER_BATCH_COUNT", "100"))
    
    # Dashboard settings
    dashboard_refresh_interval_seconds: int = int(os.getenv("DASHBOARD_REFRESH_INTERVAL", "1"))
    
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
