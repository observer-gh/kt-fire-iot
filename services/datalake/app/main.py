from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
import asyncio
from sqlalchemy.orm import Session

from .models import RawSensorData, ProcessedSensorData
from .processor import DataProcessor
from .publisher import KafkaPublisher
from .storage_service import StorageService
from .mock_storage import MockStorage
from .scheduler import BatchScheduler
from .database import get_db, engine
from .db_models import Base
from .config import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DataLake API",
    description="Data ingestion and streaming processing for IoT fire monitoring",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services based on configuration
kafka_publisher = KafkaPublisher()

# Select storage service based on configuration
if settings.storage_type == "mock":
    storage_service = MockStorage(settings.storage_path)
    logger.info(f"Using MockStorage for local testing at: {settings.storage_path}")
else:
    storage_service = StorageService()
    logger.info(f"Using StorageService for production at: {settings.storage_path}")

batch_scheduler = BatchScheduler(storage_service, kafka_publisher)

@app.on_event("startup")
async def startup_event():
    """Startup event - start batch scheduler"""
    await batch_scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - stop batch scheduler and cleanup"""
    await batch_scheduler.stop()
    kafka_publisher.close()

@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": "datalake"}


@app.get("/")
async def root():
    return {"message": "DataLake Service"}


@app.post("/ingest")
async def ingest_sensor_data(
    raw_data: RawSensorData, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Ingest sensor data from external API"""
    try:
        logger.info(f"Received sensor data: {raw_data.equipment_id}")

        # Process the data
        processed_data = DataProcessor.process_sensor_data(raw_data)

        # Save to database
        save_success = storage_service.save_sensor_data(db, processed_data)
        if not save_success:
            raise HTTPException(status_code=500, detail="Failed to save data to database")

        # Check for anomalies and publish events
        if processed_data.is_anomaly:
            background_tasks.add_task(
                kafka_publisher.publish_anomaly_detected, 
                processed_data
            )
            logger.info(f"Anomaly detected for equipment {processed_data.equipment_id}")

        # Publish sensor data event
        background_tasks.add_task(
            kafka_publisher.publish_sensor_data, 
            processed_data
        )

        return {
            "status": "success",
            "message": "Data ingested and processed",
            "equipment_id": processed_data.equipment_id,
            "is_anomaly": processed_data.is_anomaly,
            "anomaly_metric": processed_data.anomaly_metric
        }

    except ValueError as e:
        logger.error(f"Data validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")


@app.post("/trigger-batch-upload")
async def trigger_batch_upload():
    """Manually trigger batch upload"""
    try:
        await batch_scheduler.force_batch_upload()
        return {"status": "success", "message": "Batch upload triggered"}
    except Exception as e:
        logger.error(f"Manual batch upload error: {e}")
        raise HTTPException(status_code=500, detail="Batch upload failed")


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get service statistics"""
    try:
        from sqlalchemy import func
        from .db_models import Realtime, Alert
        
        # Count records in realtime table
        realtime_count = db.query(func.count(Realtime.equipment_data_id)).scalar()
        
        # Count active alerts
        alert_count = db.query(func.count(Alert.alert_id)).filter(
            Alert.status == "ACTIVE"
        ).scalar()
        
        # Get storage stats
        storage_stats = storage_service.get_storage_stats() if hasattr(storage_service, 'get_storage_stats') else {}
        
        return {
            "realtime_records": realtime_count,
            "active_alerts": alert_count,
            "storage_type": settings.storage_type,
            "batch_size": storage_service.batch_size,
            "batch_interval_minutes": storage_service.batch_interval,
            "scheduler_running": batch_scheduler.is_running,
            "storage_stats": storage_stats
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")


@app.get("/storage/batches")
async def get_uploaded_batches():
    """Get uploaded batches (only available for MockStorage)"""
    if not hasattr(storage_service, 'get_uploaded_batches'):
        raise HTTPException(status_code=400, detail="This endpoint is only available for MockStorage")
    
    try:
        batches = storage_service.get_uploaded_batches()
        return {
            "storage_type": "mock",
            "uploaded_batches": batches
        }
    except Exception as e:
        logger.error(f"Error getting uploaded batches: {e}")
        raise HTTPException(status_code=500, detail="Failed to get uploaded batches")


@app.delete("/storage/batches")
async def clear_uploaded_batches():
    """Clear uploaded batches tracking (only available for MockStorage)"""
    if not hasattr(storage_service, 'clear_uploaded_batches'):
        raise HTTPException(status_code=400, detail="This endpoint is only available for MockStorage")
    
    try:
        storage_service.clear_uploaded_batches()
        return {"status": "success", "message": "Uploaded batches tracking cleared"}
    except Exception as e:
        logger.error(f"Error clearing uploaded batches: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear uploaded batches")


if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=settings.service_host, 
        port=settings.service_port
    )
