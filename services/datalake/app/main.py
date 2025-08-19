from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime

from .models import RawSensorData, ProcessedSensorData
from .processor import DataProcessor
from .publisher import KafkaPublisher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Initialize Kafka publisher
kafka_publisher = KafkaPublisher()


@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": "datalake"}


@app.get("/")
async def root():
    return {"message": "DataLake Service"}


@app.post("/ingest")
async def ingest_sensor_data(raw_data: RawSensorData):
    """Ingest sensor data from external API"""
    try:
        logger.info(
            f"Received sensor data: {raw_data.station_id} - {raw_data.sensor_type}")

        # Process the data
        processed_data = DataProcessor.process_sensor_data(raw_data)

        # Publish to Kafka
        success = kafka_publisher.publish_sensor_data(processed_data)

        if not success:
            raise HTTPException(
                status_code=500, detail="Failed to publish to Kafka")

        return {
            "status": "success",
            "message": "Data ingested and published",
            "processed_data": processed_data.dict()
        }

    except ValueError as e:
        logger.error(f"Data validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal processing error")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    kafka_publisher.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
