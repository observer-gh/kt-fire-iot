import logging
from typing import Dict, Any, Optional
from slack_sdk.webhook import WebhookClient
from .config import settings
from .kafka_producer import KafkaEventProducer

logger = logging.getLogger(__name__)


class SlackNotifier:
    def __init__(self):
        self.webhook_url = settings.slack_webhook_url
        if self.webhook_url:
            self.client = WebhookClient(self.webhook_url)
        else:
            self.client = None
            logger.warning(
                "Slack webhook URL not configured - notifications will be logged only")
        
        # Initialize Kafka producer for event publishing
        self.kafka_producer = KafkaEventProducer()

    def send_alert(self, alert_data: Dict[str, Any], topic: str):
        """Send alert notification to Slack"""
        alert_id = alert_data.get('alert_id', 'unknown')
        
        if not self.client:
            logger.info(f"Slack notification (not sent): {alert_data}")
            # Publish failure event since Slack is not configured
            self.kafka_producer.publish_alert_fail(
                alert_id=alert_id,
                error_code="SLACK_NOT_CONFIGURED",
                error_message="Slack webhook URL not configured"
            )
            return

        try:
            message = self._format_message(alert_data, topic)
            response = self.client.send(text=message)

            if response.status_code == 200:
                logger.info(
                    f"Slack notification sent successfully for alert {alert_id}")
                # Publish success event
                self.kafka_producer.publish_alert_success(
                    alert_id=alert_id,
                    channel="slack"
                )
            else:
                logger.error(
                    f"Failed to send Slack notification: {response.status_code} - {response.body}")
                # Publish failure event
                self.kafka_producer.publish_alert_fail(
                    alert_id=alert_id,
                    error_code=f"SLACK_HTTP_{response.status_code}",
                    error_message=response.body
                )

        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            # Publish failure event
            self.kafka_producer.publish_alert_fail(
                alert_id=alert_id,
                error_code="SLACK_EXCEPTION",
                error_message=str(e)
            )

    def _format_message(self, alert_data: Dict[str, Any], topic: str) -> str:
        """Format alert data into Slack message"""
        # Kafka 메시지는 직접 루트에 필드들이 있음 (data 필드 없음)
        # data 필드가 있으면 사용하고, 없으면 직접 루트에서 가져옴
        if 'data' in alert_data:
            data = alert_data.get('data', {})
        else:
            data = alert_data

        # Determine severity and emoji
        severity = data.get('severity', 'UNKNOWN')
        if topic == 'controltower.emergencyAlertIssued':
            emoji = "🚨"
            color = "danger"
        else:
            emoji = "⚠️"
            color = "warning"

        # Format location - equipment_location 필드 사용
        location_str = data.get('equipment_location', 'Unknown')
        
        # location_str이 null이거나 빈 값이면 기본값 사용
        if not location_str or location_str == 'Unknown' or location_str.strip() == '':
            location_str = "KT판교 사옥 8층"

        # Format alert type
        alert_type = data.get('alert_type', 'Unknown Type')

        # Build message
        message = f"{emoji} *{severity} ALERT* - {alert_type}\n"
        message += f"📍 *Location:* {location_str}\n"
        message += f"📝 *Equipment ID:* {data.get('equipment_id', 'Unknown')}\n"
        message += f"🆔 *Alert ID:* {data.get('alert_id', 'Unknown')}\n"
        message += f"🏢 *Facility ID:* {data.get('facility_id', 'Unknown')}\n"
        message += f"📊 *Status:* {data.get('status', 'Unknown')}\n"

        # Format timestamp
        created_at = data.get('created_at', 'Unknown')
        if isinstance(created_at, (int, float)):
            from datetime import datetime
            try:
                # Unix timestamp를 datetime으로 변환
                dt = datetime.fromtimestamp(created_at)
                created_at = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                created_at = str(created_at)

        message += f"⏰ *Time:* {created_at}"

        return message

    def close(self):
        """Close the Kafka producer"""
        if hasattr(self, 'kafka_producer'):
            self.kafka_producer.close()
