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
        self.heartbeat_task = None

    def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming alert messages"""
        try:
            # Extract topic from message or determine based on event type
            event_type = message.get('event_type', '')
            severity = message.get('severity', '')
            
            # Determine topic based on severity and message content
            if severity == 'EMERGENCY' or 'emergency' in event_type.lower():
                topic = 'controlTower.emergencyAlertIssued'
            else:
                topic = 'controlTower.warningAlertIssued'

            logger.info(
                f"Processing {topic} message: {message.get('alert_id', 'unknown')}")

            # Send to Slack
            self.slack_notifier.send_alert(message, topic)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def _heartbeat_task(self):
        """Send heartbeat message every 10 seconds"""
        while self.running:
            try:
                self.slack_notifier.send_heartbeat()
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Error in heartbeat task: {e}")
                await asyncio.sleep(10)

    async def start(self):
        """Start the alert worker"""
        self.running = True
        logger.info("Alert worker started")
        
        # 환경 정보 로깅
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Kafka Bootstrap Servers: {settings.kafka_bootstrap_servers}")
        logger.info(f"Kafka Security Protocol: {settings.kafka_security_protocol}")
        logger.info(f"Azure Event Hub Connection: {'Configured' if settings.azure_eventhub_connection_string else 'Not configured'}")

        try:
            # Start heartbeat task
            self.heartbeat_task = asyncio.create_task(self._heartbeat_task())
            
            # Start consumer
            await self.consumer.start()
        except Exception as e:
            logger.error(f"Error in alert worker: {e}")
            # Azure 환경에서 연결 실패 시 재시도 로직
            if settings.kafka_security_protocol == 'SASL_SSL':
                logger.info("Retrying connection in 10 seconds...")
                await asyncio.sleep(10)
                await self.start()
            else:
                await asyncio.sleep(5)

    async def stop(self):
        """Stop the alert worker"""
        self.running = False
        
        # Cancel heartbeat task
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        await self.consumer.stop()
        
        # Close Kafka producer
        if hasattr(self.slack_notifier, 'close'):
            self.slack_notifier.close()
            
        logger.info("Alert worker stopped")


async def main():
    worker = AlertWorker()
    try:
        # Start the worker
        await worker.start()
        
        # Keep the main thread alive
        logger.info("Alert worker is running. Press Ctrl+C to stop.")
        while worker.running:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                await asyncio.sleep(5)
                
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        await worker.stop()
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        await worker.stop()
    finally:
        logger.info("Alert worker service stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)
