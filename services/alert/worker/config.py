from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Environment
    environment: str = "local"  # local, dev, prod

    # Kafka Configuration (for local)
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_warning_topic: str = "controlTower.warningAlertIssued"
    kafka_emergency_topic: str = "controlTower.emergencyAlertIssued"
    kafka_group_id: str = "alert-service"
    
    # Alert result topics
    kafka_alert_success_topic: str = "alert.alertSendSuccess"
    kafka_alert_fail_topic: str = "alert.alertSendFail"

    # Azure Event Hubs Configuration (for cloud)
    azure_eventhub_connection_string: Optional[str] = None
    azure_eventhub_warning_topic: str = "controlTower.warningAlertIssued"
    azure_eventhub_emergency_topic: str = "controlTower.emergencyAlertIssued"
    azure_eventhub_consumer_group: str = "$Default"

    # Slack Configuration
    slack_webhook_url: Optional[str] = "https://hooks.slack.com/services/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"

    class Config:
        env_file = ".env"
        env_prefix = "ALERT_"


settings = Settings()
