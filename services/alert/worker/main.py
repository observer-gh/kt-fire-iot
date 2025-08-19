import asyncio
import logging
from typing import Dict, Any
from .consumer import MessageConsumer
from .slack_notifier import SlackNotifier
from .config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertWorker:
    def __init__(self):
        self.running = False
        self.slack_notifier = SlackNotifier()
        self.consumer = MessageConsumer(self._handle_message)

    def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming alert messages"""
        try:
            # Extract topic from message or determine based on event type
            event_type = message.get('event_type', '')
            topic = 'EmergencyAlertTriggered' if 'emergency' in event_type.lower(
            ) else 'WarningNotificationCreated'

            logger.info(
                f"Processing {topic} message: {message.get('event_id', 'unknown')}")

            # Send to Slack
            self.slack_notifier.send_alert(message, topic)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def start(self):
        """Start the alert worker"""
        self.running = True
        logger.info("Alert worker started")

        try:
            await self.consumer.start()
        except Exception as e:
            logger.error(f"Error in alert worker: {e}")
            await asyncio.sleep(5)

    async def stop(self):
        """Stop the alert worker"""
        self.running = False
        await self.consumer.stop()
        logger.info("Alert worker stopped")


async def main():
    worker = AlertWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        await worker.stop()

if __name__ == "__main__":
    asyncio.run(main())
