from pydantic_settings import BaseSettings
from typing import Optional, Tuple


class Settings(BaseSettings):
    # Environment
    environment: str = "local"  # local, dev, prod

    # Kafka Configuration (for local and cloud)
    kafka_bootstrap_servers: str = "fire-iot-eventhub-dev.servicebus.windows.net:9093"
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

    # Kafka Security Configuration for Azure
    kafka_security_protocol: str = "PLAINTEXT"  # PLAINTEXT for local, SASL_SSL for Azure
    kafka_sasl_mechanism: str = "PLAIN"
    kafka_sasl_username: str = "$ConnectionString"
    kafka_sasl_password: Optional[str] = None

    # Slack Configuration
    slack_webhook_url: Optional[str] = "https://hooks.slack.com/services/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"

    class Config:
        env_file = ".env"
        env_prefix = "ALERT_"
        
        # Bicep 환경변수와 Python 설정 매핑
        fields = {
            'kafka_bootstrap_servers': {'env': 'KAFKA_BOOTSTRAP_SERVERS'},
            'kafka_warning_topic': {'env': 'KAFKA_WARNING_TOPIC'},
            'kafka_emergency_topic': {'env': 'KAFKA_EMERGENCY_TOPIC'},
            'kafka_alert_success_topic': {'env': 'KAFKA_ALERT_SUCCESS_TOPIC'},
            'kafka_alert_fail_topic': {'env': 'KAFKA_ALERT_FAIL_TOPIC'},
            'kafka_group_id': {'env': 'KAFKA_CONSUMER_GROUP_ID'},
            'azure_eventhub_connection_string': {'env': 'azure_eventhub_connection_string'},
            'kafka_security_protocol': {'env': 'KAFKA_SECURITY_PROTOCOL'},
            'kafka_sasl_mechanism': {'env': 'KAFKA_SASL_MECHANISM'},
            'kafka_sasl_username': {'env': 'KAFKA_SASL_USERNAME'},
            'kafka_sasl_password': {'env': 'KAFKA_SASL_PASSWORD'}
        }


settings = Settings()
