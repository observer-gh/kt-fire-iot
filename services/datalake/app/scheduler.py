import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from .storage_service import StorageService
from .publisher import KafkaPublisher
from .database import SessionLocal

logger = logging.getLogger(__name__)

class BatchScheduler:
    """Schedules and manages batch upload operations"""
    
    def __init__(self, storage_service: StorageService, kafka_publisher: KafkaPublisher):
        self.storage_service = storage_service
        self.kafka_publisher = kafka_publisher
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the batch scheduler"""
        if self.is_running:
            logger.warning("Batch scheduler is already running")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._run_scheduler())
        logger.info("Batch scheduler started")
    
    async def stop(self):
        """Stop the batch scheduler"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Batch scheduler stopped")
    
    async def _run_scheduler(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                # Check if batch upload is needed
                db = SessionLocal()
                try:
                    if self.storage_service.should_upload_batch(db):
                        logger.info("Batch upload condition met, processing...")
                        await self._process_batch_upload(db)
                    else:
                        logger.debug("Batch upload not needed yet")
                finally:
                    db.close()
                
                # Wait for next check
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in batch scheduler: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _process_batch_upload(self, db: Session):
        """Process a batch upload"""
        try:
            # Upload batch to storage
            filepath = self.storage_service.upload_batch_to_storage(db)
            if filepath:
                logger.info(f"Batch uploaded to storage: {filepath}")
                
                # Publish data saved event
                # Note: This is a simplified approach - you might want to track which data was uploaded
                from .models import ProcessedSensorData
                
                data_saved_event = ProcessedSensorData(
                    equipment_id="batch_upload",
                    measured_at=datetime.utcnow(),
                    ingested_at=datetime.utcnow()
                )
                
                self.kafka_publisher.publish_data_saved(data_saved_event, filepath)
                
                # Clean up uploaded data
                cleanup_success = self.storage_service.cleanup_uploaded_data(db, filepath)
                if cleanup_success:
                    logger.info("Uploaded data cleaned up successfully")
                else:
                    logger.warning("Failed to cleanup uploaded data")
            else:
                logger.warning("No data to upload in batch")
                
        except Exception as e:
            logger.error(f"Error processing batch upload: {e}")
    
    async def force_batch_upload(self):
        """Force a batch upload regardless of conditions"""
        logger.info("Forcing batch upload...")
        db = SessionLocal()
        try:
            await self._process_batch_upload(db)
        finally:
            db.close()
