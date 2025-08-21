import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from .storage_service import StorageService
from .publisher import KafkaPublisher
from .redis_client import redis_client
from .models import ProcessedSensorData
from .config import settings

logger = logging.getLogger(__name__)

class BatchScheduler:
    """Schedules and manages batch upload operations and Redis flush operations"""
    
    def __init__(self, storage_service: StorageService, kafka_publisher: KafkaPublisher):
        self.storage_service = storage_service
        self.kafka_publisher = kafka_publisher
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.flush_interval_seconds = settings.redis_flush_interval_seconds  # 설정에서 가져온 flush 간격
    
    async def start(self):
        """Start the batch scheduler"""
        if self.is_running:
            logger.warning("Batch scheduler is already running")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._run_scheduler())
        logger.info(f"Batch scheduler started with {self.flush_interval_seconds}-second Redis flush interval")
    
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
        """Main scheduler loop - Redis flush every minute, batch upload when needed"""
        while self.is_running:
            try:
                # Redis 데이터 flush (설정된 간격으로)
                await self._flush_redis_data()
                
                # 배치 업로드 조건 확인
                if self.storage_service.should_upload_batch():
                    logger.info("Batch upload condition met, processing...")
                    await self._process_batch_upload()
                else:
                    logger.debug("Batch upload not needed yet")
                
                # 다음 flush까지 대기
                await asyncio.sleep(self.flush_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in batch scheduler: {e}")
                await asyncio.sleep(self.flush_interval_seconds)  # Wait before retrying
    
    async def _flush_redis_data(self):
        """Redis의 센서 데이터를 로컬 스토리지에 flush"""
        try:
            # Redis에서 모든 센서 데이터 조회
            sensor_data_list = redis_client.flush_sensor_data_to_storage()
            
            if not sensor_data_list:
                logger.debug("Redis에 저장할 센서 데이터가 없습니다")
                return
            
            logger.info(f"Redis에서 {len(sensor_data_list)}개의 센서 데이터를 로컬 스토리지로 flush 중...")
            
            # 각 센서 데이터를 로컬 스토리지에 저장
            saved_count = 0
            error_count = 0
            
            for sensor_data in sensor_data_list:
                try:
                    # 데이터 구조 검증
                    if not isinstance(sensor_data, dict):
                        logger.error(f"센서 데이터가 딕셔너리가 아님: {type(sensor_data)}")
                        error_count += 1
                        continue
                    
                    # 필수 필드 확인
                    required_fields = ['equipment_id', 'measured_at']
                    missing_fields = [field for field in required_fields if field not in sensor_data]
                    if missing_fields:
                        logger.error(f"필수 필드 누락: {missing_fields}, 데이터: {sensor_data.get('equipment_id', 'unknown')}")
                        error_count += 1
                        continue
                    
                    # ProcessedSensorData 객체로 변환
                    try:
                        processed_data = ProcessedSensorData(**sensor_data)
                    except Exception as e:
                        logger.error(f"ProcessedSensorData 변환 실패 ({sensor_data.get('equipment_id', 'unknown')}): {e}")
                        logger.error(f"데이터 내용: {sensor_data}")
                        error_count += 1
                        continue
                    
                    # 로컬 스토리지에 저장
                    save_success = self.storage_service.save_sensor_data(processed_data)
                    if save_success:
                        saved_count += 1
                        
                        # sensorDataSaved 이벤트 발행 (flush 시에만)
                        self.kafka_publisher.publish_data_saved(processed_data, f"redis_flush_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
                        
                    else:
                        logger.error(f"센서 데이터 저장 실패: {sensor_data.get('equipment_id', 'unknown')}")
                        error_count += 1
                        
                except Exception as e:
                    logger.error(f"개별 센서 데이터 flush 처리 오류: {e}")
                    logger.error(f"문제가 된 데이터: {sensor_data}")
                    error_count += 1
                    continue
            
            # 결과 요약
            if error_count > 0:
                logger.warning(f"Redis flush 완료: {saved_count}개 성공, {error_count}개 실패")
            else:
                logger.info(f"Redis flush 완료: {saved_count}개 모두 성공")
            
            # Redis 데이터 정리 (flush 완료 후)
            if saved_count > 0:
                clear_success = redis_client.clear_sensor_data()
                if clear_success:
                    logger.info(f"Redis 센서 데이터 {saved_count}개를 로컬 스토리지로 flush 완료")
                else:
                    logger.warning("Redis 센서 데이터 정리 실패")
            elif error_count > 0:
                logger.warning("일부 데이터 처리 실패로 Redis 정리 건너뜀")
            else:
                logger.debug("flush할 센서 데이터가 없습니다")
                
        except Exception as e:
            logger.error(f"Redis 데이터 flush 오류: {e}")
    
    async def _process_batch_upload(self):
        """Process a batch upload"""
        try:
            # Upload batch to storage
            filepath = self.storage_service.upload_batch_to_storage()
            if filepath:
                logger.info(f"Batch uploaded to storage: {filepath}")
                
                # Publish data saved event
                # Note: This is a simplified approach - you might want to track which data was uploaded
                data_saved_event = ProcessedSensorData(
                    equipment_id="batch_upload",
                    measured_at=datetime.utcnow(),
                    ingested_at=datetime.utcnow()
                )
                
                self.kafka_publisher.publish_data_saved(data_saved_event, f"batch_upload_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
                
                # Clean up uploaded data
                cleanup_success = self.storage_service.cleanup_uploaded_data(filepath)
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
        await self._process_batch_upload()
    
    async def force_redis_flush(self):
        """강제로 Redis 데이터 flush 실행"""
        logger.info("Forcing Redis data flush...")
        await self._flush_redis_data()
    
    def get_redis_data_count(self) -> int:
        """Redis에 저장된 센서 데이터 개수 반환"""
        return redis_client.get_sensor_data_count()
