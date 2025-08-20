import asyncio
import logging
from datetime import datetime
from typing import Optional
from .mock_server_client import MockServerClient
from .processor import DataProcessor
from .storage_service import StorageService
from .publisher import KafkaPublisher
from .config import settings

logger = logging.getLogger(__name__)

class MockDataScheduler:
    """Mock Server에서 주기적으로 데이터를 가져와서 처리하는 스케줄러"""
    
    def __init__(self, storage_service: StorageService, kafka_publisher: KafkaPublisher):
        self.storage_service = storage_service
        self.kafka_publisher = kafka_publisher
        self.mock_server_client = MockServerClient()
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.data_fetch_interval = settings.mock_server_data_fetch_interval_seconds
        
    async def start(self):
        """스케줄러를 시작합니다."""
        if self.is_running:
            logger.warning("Mock Data Scheduler가 이미 실행 중입니다.")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._run_scheduler())
        logger.info(f"Mock Data Scheduler가 시작되었습니다. 폴링 간격: {self.data_fetch_interval}초")
    
    async def stop(self):
        """스케줄러를 중지합니다."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Mock Data Scheduler가 중지되었습니다.")
    
    async def _run_scheduler(self):
        """스케줄러 메인 루프"""
        while self.is_running:
            try:
                await self._process_mock_data()
                await asyncio.sleep(self.data_fetch_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Mock Data Scheduler 오류: {e}")
                await asyncio.sleep(10)  # 오류 발생 시 10초 대기
    
    async def _process_mock_data(self):
        """Mock Server에서 데이터를 가져와서 처리합니다."""
        try:
            logger.info("Mock Server에서 데이터를 폴링하는 중...")
            
            # Mock Server 상태 확인
            if not await self.mock_server_client.health_check():
                logger.warning("Mock Server가 응답하지 않습니다. 다음 폴링까지 대기합니다.")
                return
            
            # 스트리밍 데이터 가져오기 (설정값 사용)
            from .config import settings
            stream_count = settings.mock_server_stream_data_count
            raw_data_list = await self.mock_server_client.get_stream_data(stream_count)
            
            if not raw_data_list:
                logger.info("Mock Server에서 데이터를 받지 못했습니다.")
                return
            
            logger.info(f"Mock Server에서 {len(raw_data_list)}개의 데이터를 받았습니다.")
            
            # 각 데이터를 처리
            processed_count = 0
            anomaly_count = 0
            
            for raw_data in raw_data_list:
                try:
                    # 데이터 처리
                    processed_data = DataProcessor.process_sensor_data(raw_data)
                    
                    # 데이터베이스에 저장
                    save_success = self.storage_service.save_sensor_data(processed_data)
                    if not save_success:
                        logger.error(f"Mock 데이터 저장 실패: {raw_data.equipment_id}")
                        continue
                    
                    processed_count += 1
                    
                    # 이상치 탐지 및 이벤트 발행
                    if processed_data.is_anomaly:
                        anomaly_count += 1
                        await self.kafka_publisher.publish_anomaly_detected(processed_data)
                        logger.info(f"🚨 Mock 데이터 이상치 탐지: {processed_data.equipment_id} - {processed_data.anomaly_metric} = {processed_data.anomaly_value}")
                    
                    # 센서 데이터 이벤트 발행
                    await self.kafka_publisher.publish_sensor_data(processed_data)
                    
                except Exception as e:
                    logger.error(f"Mock 데이터 처리 오류 ({raw_data.equipment_id}): {e}")
                    continue
            
            logger.info(f"Mock 데이터 처리 완료: {processed_count}개 처리됨, {anomaly_count}개 이상치 탐지")
            
        except Exception as e:
            logger.error(f"Mock 데이터 처리 중 오류 발생: {e}")
    
    async def force_process(self):
        """강제로 Mock 데이터를 처리합니다."""
        if not self.is_running:
            logger.warning("Mock Data Scheduler가 실행되지 않고 있습니다.")
            return
        
        await self._process_mock_data()
    
    def get_status(self):
        """스케줄러 상태를 반환합니다."""
        return {
            "is_running": self.is_running,
            "polling_interval_seconds": self.data_fetch_interval,
            "last_check": datetime.utcnow().isoformat() if self.is_running else None
        }
