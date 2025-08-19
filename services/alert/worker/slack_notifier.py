import logging
from typing import Dict, Any, Optional
from slack_sdk.webhook import WebhookClient
from .config import settings

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

    def send_alert(self, alert_data: Dict[str, Any], topic: str):
        """Send alert notification to Slack"""
        if not self.client:
            logger.info(f"Slack notification (not sent): {alert_data}")
            return

        try:
            message = self._format_message(alert_data, topic)
            response = self.client.send(text=message)

            if response.status_code == 200:
                logger.info(
                    f"Slack notification sent successfully for alert {alert_data.get('alert_id', 'unknown')}")
            else:
                logger.error(
                    f"Failed to send Slack notification: {response.status_code} - {response.body}")

        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")

    def _format_message(self, alert_data: Dict[str, Any], topic: str) -> str:
        """Format alert data into Slack message"""
        data = alert_data.get('data', {})

        # Determine severity and emoji
        severity = data.get('severity', 'UNKNOWN')
        if topic == 'EmergencyAlertTriggered':
            emoji = "🚨"
            color = "danger"
        else:
            emoji = "⚠️"
            color = "warning"

        # Format location
        location = data.get('location', {})
        location_str = f"{location.get('building_name', 'Unknown Building')}"
        if location.get('floor'):
            location_str += f" - Floor {location['floor']}"
        if location.get('room'):
            location_str += f" - Room {location['room']}"

        # Format sensor readings
        sensors = data.get('sensor_readings', {})
        sensor_str = ""
        if sensors:
            readings = []
            for sensor, value in sensors.items():
                if value is not None:
                    readings.append(f"{sensor}: {value}")
            if readings:
                sensor_str = f" | Sensors: {', '.join(readings)}"

        # Build message
        message = f"{emoji} *{severity} ALERT* - {data.get('rule_name', 'Unknown Rule')}\n"
        message += f"📍 *Location:* {location_str}\n"
        message += f"📝 *Message:* {data.get('message', 'No message')}\n"
        message += f"🆔 *Alert ID:* {data.get('alert_id', 'Unknown')}\n"
        message += f"🏢 *Station:* {data.get('station_id', 'Unknown')}\n"

        if sensor_str:
            message += f"📊 *Readings:* {sensor_str}\n"

        message += f"⏰ *Time:* {data.get('created_at', 'Unknown')}"

        return message
