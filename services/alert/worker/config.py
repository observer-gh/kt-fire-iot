from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Environment
    environment: str = "local"  # local, dev, prod

    # Kafka Configuration (for local)
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_warning_topic: str = "WarningNotificationCreated"
    kafka_emergency_topic: str = "EmergencyAlertTriggered"
    kafka_group_id: str = "alert-service"

    # Azure Event Hubs Configuration (for cloud)
    azure_eventhub_connection_string: Optional[str] = None
    azure_eventhub_warning_topic: str = "WarningNotificationCreated"
    azure_eventhub_emergency_topic: str = "EmergencyAlertTriggered"
    azure_eventhub_consumer_group: str = "$Default"

    # Slack Configuration
    slack_webhook_url: Optional[str] = "https://hooks.slack.com/services/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"

    class Config:
        env_file = ".env"
        env_prefix = "ALERT_"


settings = Settings()
