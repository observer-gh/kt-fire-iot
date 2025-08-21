from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
import asyncio
import uuid

from .models import RawSensorData, ProcessedSensorData
from .processor import DataProcessor
from .publisher import KafkaPublisher
from .storage_service import StorageService
from .mock_storage import MockStorage
from .scheduler import BatchScheduler
from .database import create_tables
from .config import settings
from .redis_client import redis_client
from .mock_server_client import MockServerClient
from .mock_data_scheduler import MockDataScheduler

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Create database tables
create_tables()

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
mock_server_client = MockServerClient()

# Select storage service based on configuration
if settings.storage_type == "mock":
    storage_service = MockStorage(settings.storage_path)
    logger.info(f"Using MockStorage for local testing at: {settings.storage_path}")
else:
    storage_service = StorageService()
    logger.info(f"Using StorageService for production at: {settings.storage_path}")

batch_scheduler = BatchScheduler(storage_service, kafka_publisher)
mock_data_scheduler = MockDataScheduler(storage_service, kafka_publisher)

@app.on_event("startup")
async def startup_event():
    """Startup event - start batch scheduler and mock data scheduler"""
    await batch_scheduler.start()
    await mock_data_scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - stop schedulers and cleanup"""
    await batch_scheduler.stop()
    await mock_data_scheduler.stop()
    kafka_publisher.close()
    redis_client.close()

@app.get("/healthz")
async def health_check():
    """Health check endpoint with Redis status"""
    redis_status = "healthy" if redis_client.is_connected() else "unhealthy"
    
    # Mock Server 상태도 확인
    mock_server_status = "healthy" if await mock_server_client.health_check() else "unhealthy"
    
    return {
        "status": "healthy", 
        "service": "datalake",
        "redis": redis_status,
        "mock_server": mock_server_status,
        "storage_type": settings.storage_type
    }


@app.get("/redis/status")
async def redis_status():
    """Get Redis connection status and info"""
    try:
        if not redis_client.is_connected():
            return {
                "connected": False,
                "url": settings.redis_url,
                "error": "Redis connection failed"
            }
        
        # Get Redis info
        redis_info = {
            "connected": True,
            "url": settings.redis_url,
            "ping": "pong",
            "sensor_data_count": redis_client.get_sensor_data_count()
        }
        
        return redis_info
    except Exception as e:
        logger.error(f"Redis status check error: {e}")
        return {
            "connected": False,
            "url": settings.redis_url,
            "error": str(e)
        }


@app.get("/")
async def root():
    return {"message": "DataLake Service"}


@app.post("/ingest")
async def ingest_sensor_data(
    background_tasks: BackgroundTasks
):
    """Mock Server에서 실시간 데이터를 가져와서 처리하고 이상치를 탐지합니다."""
    try:
        logger.info("Mock Server에서 실시간 데이터를 가져오는 중...")
        
        # Mock Server에서 데이터 가져오기
        raw_data_list = await mock_server_client.get_realtime_data()
        
        if not raw_data_list:
            logger.warning("Mock Server에서 데이터를 받지 못했습니다.")
            return Response(status_code=204)
        
        logger.info(f"Mock Server에서 {len(raw_data_list)}개의 데이터를 받았습니다.")
        
        # 각 데이터를 처리하고 이상치 탐지
        anomaly_detected = False
        anomaly_data = None
        
        for raw_data in raw_data_list:
            try:
                # 데이터 처리
                processed_data = DataProcessor.process_sensor_data(raw_data)
                
                # Redis에 센서 데이터 저장 (실시간 저장)
                redis_save_success = redis_client.save_sensor_data(processed_data.dict())
                if not redis_save_success:
                    logger.error(f"Redis 저장 실패: {raw_data.equipment_id}")
                    continue
                
                # 이상치 탐지 및 이벤트 발행
                if processed_data.is_anomaly:
                    anomaly_detected = True
                    anomaly_data = processed_data
                    
                    background_tasks.add_task(
                        kafka_publisher.publish_anomaly_detected, 
                        processed_data
                    )
                    logger.info(f"🚨 이상치 탐지됨: {processed_data.equipment_id} - {processed_data.anomaly_metric} = {processed_data.anomaly_value}")
                
                # 센서 데이터 이벤트는 Redis flush 시에만 발행되므로 여기서는 발행하지 않음
                logger.info(f"✅ 센서 데이터 Redis 저장 완료: {processed_data.equipment_id}")
                
            except Exception as e:
                logger.error(f"개별 데이터 처리 오류 ({raw_data.equipment_id}): {e}")
                continue
        
        # 이상치가 있는 경우에만 응답 반환
        if anomaly_detected and anomaly_data:
            response_data = {
                "version": 1,
                "event_id": str(uuid.uuid4()),
                "equipment_id": anomaly_data.equipment_id,
                "facility_id": anomaly_data.facility_id,
                "metric": anomaly_data.anomaly_metric,
                "value": anomaly_data.anomaly_value,
                "threshold": anomaly_data.anomaly_threshold,
                "rule_id": None,
                "measured_at": anomaly_data.measured_at,
                "detected_at": anomaly_data.ingested_at,
                "total_processed": len(raw_data_list),
                "anomalies_found": 1
            }
            logger.info(f"📤 이상치 응답 반환: {response_data}")
            return response_data
        else:
            # 정상 데이터인 경우 204 No Content 반환
            logger.info(f"✅ 정상 데이터 처리 완료: 총 {len(raw_data_list)}개 Redis에 저장됨")
            return Response(status_code=204)

    except Exception as e:
        logger.error(f"Mock Server 데이터 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Mock Server 데이터 처리 실패: {str(e)}")

@app.post("/ingest/stream")
async def ingest_stream_data(
    background_tasks: BackgroundTasks
):
    """Mock Server에서 스트리밍 데이터를 가져와서 처리합니다."""
    try:
        logger.info("Mock Server에서 스트리밍 데이터를 가져오는 중...")
        
        # Mock Server에서 스트리밍 데이터 가져오기
        raw_data_list = await mock_server_client.get_stream_data()
        
        if not raw_data_list:
            logger.warning("Mock Server에서 스트리밍 데이터를 받지 못했습니다.")
            return Response(status_code=204)
        
        logger.info(f"Mock Server에서 {len(raw_data_list)}개의 스트리밍 데이터를 받았습니다.")
        
        # 각 데이터를 처리
        processed_count = 0
        anomaly_count = 0
        
        for raw_data in raw_data_list:
            try:
                # 데이터 처리
                processed_data = DataProcessor.process_sensor_data(raw_data)
                
                # Redis에 센서 데이터 저장
                redis_save_success = redis_client.save_sensor_data(processed_data.dict())
                if not redis_save_success:
                    logger.error(f"Redis 저장 실패: {raw_data.equipment_id}")
                    continue
                
                processed_count += 1
                
                # 이상치 탐지 및 이벤트 발행
                if processed_data.is_anomaly:
                    anomaly_count += 1
                    background_tasks.add_task(
                        kafka_publisher.publish_anomaly_detected, 
                        processed_data
                    )
                    logger.info(f"🚨 스트리밍 이상치 탐지: {processed_data.equipment_id}")
                
                # 센서 데이터 이벤트는 Redis flush 시에만 발행
                logger.info(f"✅ 스트리밍 데이터 Redis 저장 완료: {processed_data.equipment_id}")
                
            except Exception as e:
                logger.error(f"스트리밍 데이터 처리 오류 ({raw_data.equipment_id}): {e}")
                continue
        
        return {
            "status": "success",
            "message": "스트리밍 데이터 처리 완료",
            "total_received": len(raw_data_list),
            "processed_count": processed_count,
            "anomaly_count": anomaly_count,
            "processed_at": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Mock Server 스트리밍 데이터 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Mock Server 스트리밍 데이터 처리 실패: {str(e)}")

@app.post("/ingest/batch")
async def ingest_batch_data(
    background_tasks: BackgroundTasks
):
    """Mock Server에서 배치 데이터를 가져와서 처리합니다."""
    try:
        logger.info("Mock Server에서 배치 데이터를 가져오는 중...")
        
        # Mock Server에서 배치 데이터 가져오기
        raw_data_list = await mock_server_client.get_batch_data()
        
        if not raw_data_list:
            logger.warning("Mock Server에서 배치 데이터를 받지 못했습니다.")
            return Response(status_code=204)
        
        logger.info(f"Mock Server에서 {len(raw_data_list)}개의 배치 데이터를 받았습니다.")
        
        # 각 데이터를 처리
        processed_count = 0
        anomaly_count = 0
        
        for raw_data in raw_data_list:
            try:
                # 데이터 처리
                processed_data = DataProcessor.process_sensor_data(raw_data)
                
                # Redis에 센서 데이터 저장
                redis_save_success = redis_client.save_sensor_data(processed_data.dict())
                if not redis_save_success:
                    logger.error(f"Redis 저장 실패: {raw_data.equipment_id}")
                    continue
                
                processed_count += 1
                
                # 이상치 탐지 및 이벤트 발행
                if processed_data.is_anomaly:
                    anomaly_count += 1
                    background_tasks.add_task(
                        kafka_publisher.publish_anomaly_detected, 
                        processed_data
                    )
                    logger.info(f"🚨 배치 이상치 탐지: {processed_data.equipment_id}")
                
                # 센서 데이터 이벤트는 Redis flush 시에만 발행
                logger.info(f"✅ 배치 데이터 Redis 저장 완료: {processed_data.equipment_id}")
                
            except Exception as e:
                logger.error(f"배치 데이터 처리 오류 ({raw_data.equipment_id}): {e}")
                continue
        
        return {
            "status": "success",
            "message": "배치 데이터 처리 완료",
            "total_received": len(raw_data_list),
            "processed_count": processed_count,
            "anomaly_count": anomaly_count,
            "processed_at": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Mock Server 배치 데이터 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Mock Server 배치 데이터 처리 실패: {str(e)}")


@app.post("/ingest/external")
async def ingest_external_sensor_data(
    raw_data: RawSensorData, 
    background_tasks: BackgroundTasks
):
    """외부 API에서 센서 데이터를 받아서 처리합니다 (기존 기능 유지)"""
    try:
        logger.info(f"외부 API에서 센서 데이터 수신: {raw_data.equipment_id}")

        # 데이터 처리
        processed_data = DataProcessor.process_sensor_data(raw_data)

        # Redis에 센서 데이터 저장
        redis_save_success = redis_client.save_sensor_data(processed_data.dict())
        if not redis_save_success:
            raise HTTPException(status_code=500, detail="Failed to save data to Redis")

        # 이상치 탐지 및 이벤트 발행
        if processed_data.is_anomaly:
            background_tasks.add_task(
                kafka_publisher.publish_anomaly_detected, 
                processed_data
            )
            logger.info(f"🚨 외부 API 이상치 탐지: {processed_data.equipment_id} - {processed_data.anomaly_metric} = {processed_data.anomaly_value}")

        # 센서 데이터 이벤트는 Redis flush 시에만 발행
        logger.info(f"✅ 외부 API 데이터 Redis 저장 완료: {processed_data.equipment_id}")

        # 이상치가 있는 경우에만 응답 반환
        if processed_data.is_anomaly:
            response_data = {
                "version": 1,
                "event_id": str(uuid.uuid4()),
                "equipment_id": processed_data.equipment_id,
                "facility_id": processed_data.facility_id,
                "metric": processed_data.anomaly_metric,
                "value": processed_data.anomaly_value,
                "threshold": processed_data.anomaly_threshold,
                "rule_id": None,
                "measured_at": processed_data.measured_at,
                "detected_at": processed_data.ingested_at
            }
            logger.info(f"📤 외부 API 이상치 응답 반환: {response_data}")
            return response_data
        else:
            # 정상 데이터인 경우 204 No Content 반환
            logger.info(f"✅ 외부 API 정상 데이터 처리 완료: {processed_data.equipment_id}")
            return Response(status_code=204)

    except ValueError as e:
        logger.error(f"외부 API 데이터 검증 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"외부 API 처리 오류: {e}")
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

@app.post("/trigger-redis-flush")
async def trigger_redis_flush():
    """Manually trigger Redis data flush"""
    try:
        await batch_scheduler.force_redis_flush()
        return {"status": "success", "message": "Redis flush triggered"}
    except Exception as e:
        logger.error(f"Manual Redis flush error: {e}")
        raise HTTPException(status_code=500, detail="Redis flush failed")

@app.post("/trigger-mock-data-process")
async def trigger_mock_data_process():
    """Manually trigger mock data processing"""
    try:
        await mock_data_scheduler.force_process()
        return {"status": "success", "message": "Mock data processing triggered"}
    except Exception as e:
        logger.error(f"Manual mock data processing error: {e}")
        raise HTTPException(status_code=500, detail="Mock data processing failed")

@app.get("/mock-scheduler/status")
async def get_mock_scheduler_status():
    """Get Mock Data Scheduler status"""
    try:
        status = mock_data_scheduler.get_status()
        return {
            "scheduler": "mock_data",
            "status": status,
            "mock_server_url": settings.mock_server_url,
            "data_fetch_interval_seconds": settings.mock_server_data_fetch_interval_seconds
        }
    except Exception as e:
        logger.error(f"Mock scheduler status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get mock scheduler status")


@app.get("/stats")
async def get_stats():
    """Get service statistics with Redis caching"""
    try:
        # Try to get stats from Redis cache first
        cache_key = "datalake:stats"
        cached_stats = redis_client.get(cache_key)
        
        if cached_stats:
            logger.info("Returning cached stats from Redis")
            return cached_stats
        
        from .database import execute_query
        
        # Count records in realtime table
        realtime_count_result = execute_query("SELECT COUNT(*) as count FROM realtime")
        realtime_count = realtime_count_result[0]['count'] if realtime_count_result else 0
        
        # Count active alerts
        alert_count_result = execute_query("SELECT COUNT(*) as count FROM alert WHERE status = %s", ("ACTIVE",))
        alert_count = alert_count_result[0]['count'] if alert_count_result else 0
        
        # Get storage metadata stats
        metadata_stats = {}
        try:
            metadata_count = execute_query("SELECT COUNT(*) as count FROM storage_metadata")[0]['count']
            total_records_processed = execute_query("SELECT SUM(record_count) as total FROM storage_metadata")[0]['total'] or 0
            recent_flushes = execute_query("""
                SELECT COUNT(*) as count FROM storage_metadata 
                WHERE flush_timestamp >= NOW() - INTERVAL '1 hour'
            """)[0]['count']
            
            metadata_stats = {
                "total_flushes": metadata_count,
                "total_records_processed": total_records_processed,
                "recent_flushes_1h": recent_flushes
            }
        except Exception as e:
            logger.warning(f"Could not get metadata stats: {e}")
            metadata_stats = {"error": "Metadata stats unavailable"}
        
        # Get storage stats
        storage_stats = storage_service.get_storage_stats() if hasattr(storage_service, 'get_storage_stats') else {}
        
        # Get mock scheduler status
        mock_scheduler_status = mock_data_scheduler.get_status()
        
        # Get Redis data count
        redis_data_count = redis_client.get_sensor_data_count()
        
        stats_data = {
            "realtime_records": realtime_count,
            "active_alerts": alert_count,
            "storage_type": settings.storage_type,
            "batch_size": storage_service.batch_size,
            "batch_interval_minutes": storage_service.batch_interval,
            "scheduler_running": batch_scheduler.is_running,
            "mock_scheduler": mock_scheduler_status,
            "mock_server_url": settings.mock_server_url,
            "mock_server_data_fetch_interval": settings.mock_server_data_fetch_interval_seconds,
            "storage_stats": storage_stats,
            "storage_metadata": metadata_stats,
            "redis_sensor_data_count": redis_data_count,
            "redis_flush_interval_seconds": batch_scheduler.flush_interval_seconds,
            "cached": False
        }
        
        # Cache the stats in Redis for 5 minutes
        if redis_client.is_connected():
            redis_client.set(cache_key, stats_data, ex=300)
            stats_data["cached"] = True
        
        return stats_data
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


@app.get("/storage/metadata")
async def get_storage_metadata(
    limit: int = 100,
    offset: int = 0,
    storage_type: str = None,
    start_date: str = None,
    end_date: str = None
):
    """Get storage metadata with filtering and pagination"""
    try:
        from .database import execute_query
        
        # Build query with filters
        query = "SELECT * FROM storage_metadata WHERE 1=1"
        params = []
        
        if storage_type:
            query += " AND storage_type = %s"
            params.append(storage_type)
        
        if start_date:
            query += " AND flush_timestamp >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND flush_timestamp <= %s"
            params.append(end_date)
        
        # Add ordering and pagination
        query += " ORDER BY flush_timestamp DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        # Execute query
        results = execute_query(query, params)
        
        # Get total count for pagination
        count_query = "SELECT COUNT(*) as total FROM storage_metadata WHERE 1=1"
        count_params = []
        
        if storage_type:
            count_query += " AND storage_type = %s"
            count_params.append(storage_type)
        
        if start_date:
            count_query += " AND flush_timestamp >= %s"
            count_params.append(start_date)
        
        if end_date:
            count_query += " AND flush_timestamp <= %s"
            count_params.append(end_date)
        
        total_count = execute_query(count_query, count_params)[0]['total']
        
        return {
            "metadata": results,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total_count,
                "has_more": offset + limit < total_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting storage metadata: {e}")
        raise HTTPException(status_code=500, detail="Failed to get storage metadata")


@app.get("/storage/metadata/{metadata_id}")
async def get_storage_metadata_by_id(metadata_id: str):
    """Get specific storage metadata by ID"""
    try:
        from .database import execute_query
        
        query = "SELECT * FROM storage_metadata WHERE metadata_id = %s"
        result = execute_query(query, (metadata_id,))
        
        if not result:
            raise HTTPException(status_code=404, detail="Storage metadata not found")
        
        return result[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting storage metadata by ID: {e}")
        raise HTTPException(status_code=500, detail="Failed to get storage metadata")


@app.get("/storage/metadata/stats/summary")
async def get_storage_metadata_summary():
    """Get summary statistics of storage metadata"""
    try:
        from .database import execute_query
        
        # Get basic counts
        total_count = execute_query("SELECT COUNT(*) as count FROM storage_metadata")[0]['count']
        
        # Get counts by storage type
        type_counts = execute_query("""
            SELECT storage_type, COUNT(*) as count 
            FROM storage_metadata 
            GROUP BY storage_type
        """)
        
        # Get recent activity (last 24 hours)
        recent_count = execute_query("""
            SELECT COUNT(*) as count 
            FROM storage_metadata 
            WHERE flush_timestamp >= NOW() - INTERVAL '24 hours'
        """)[0]['count']
        
        # Get total records processed
        total_records = execute_query("""
            SELECT SUM(record_count) as total 
            FROM storage_metadata
        """)[0]['total'] or 0
        
        # Get average processing time
        avg_processing_time = execute_query("""
            SELECT AVG(processing_duration_ms) as avg_time 
            FROM storage_metadata 
            WHERE processing_duration_ms IS NOT NULL
        """)[0]['avg_time'] or 0
        
        return {
            "total_flushes": total_count,
            "recent_flushes_24h": recent_count,
            "total_records_processed": total_records,
            "average_processing_time_ms": round(avg_processing_time, 2),
            "storage_type_breakdown": type_counts
        }
        
    except Exception as e:
        logger.error(f"Error getting storage metadata summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get storage metadata summary")


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


@app.delete("/cache")
async def clear_cache():
    """Clear Redis cache"""
    try:
        if not redis_client.is_connected():
            raise HTTPException(status_code=503, detail="Redis is not connected")
        
        # Clear all datalake related cache keys
        cache_patterns = ["datalake:*"]
        cleared_count = 0
        
        # For simplicity, we'll clear specific known keys
        known_keys = ["datalake:stats"]
        for key in known_keys:
            if redis_client.delete(key):
                cleared_count += 1
        
        return {
            "status": "success", 
            "message": f"Cache cleared successfully. Cleared {cleared_count} keys."
        }
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=settings.service_host, 
        port=settings.service_port
    )
