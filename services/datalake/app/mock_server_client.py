import httpx
import logging
from typing import List, Optional
from .models import RawSensorData
from .config import settings

logger = logging.getLogger(__name__)

class MockServerClient:
    """Mock Server에서 실시간 데이터를 가져오는 클라이언트"""
    
    def __init__(self):
        self.base_url = settings.mock_server_url
        self.default_count = settings.mock_server_data_count
        self.timeout = httpx.Timeout(30.0)
    
    async def get_realtime_data(self, count: Optional[int] = None) -> List[RawSensorData]:
        """Mock Server에서 실시간 데이터를 가져옵니다."""
        try:
            data_count = count or self.default_count
            url = f"{self.base_url}/mock/realtime-generator/datalake/generate"
            params = {"count": data_count}
            
            logger.info(f"Mock Server에서 데이터 요청: {url}?count={data_count}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Mock Server에서 {len(data)}개의 데이터를 받았습니다.")
                
                # Mock Server 응답을 RawSensorData 모델로 변환
                raw_sensor_data_list = []
                for item in data:
                    raw_sensor_data = RawSensorData(
                        equipment_id=item.get("equipment_id"),
                        facility_id=item.get("facility_id"),
                        equipment_location=item.get("equipment_location"),
                        measured_at=item.get("measured_at"),
                        temperature=item.get("temperature"),
                        humidity=item.get("humidity"),
                        smoke_density=item.get("smoke_density"),
                        co_level=item.get("co_level"),
                        gas_level=item.get("gas_level"),
                        metadata=item.get("metadata", {})
                    )
                    raw_sensor_data_list.append(raw_sensor_data)
                
                return raw_sensor_data_list
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Mock Server HTTP 오류: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Mock Server 요청 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"Mock Server 데이터 가져오기 오류: {e}")
            raise
    
    async def get_stream_data(self, count: Optional[int] = None) -> List[RawSensorData]:
        """Mock Server에서 스트리밍용 데이터를 가져옵니다."""
        try:
            if count is None:
                from .config import settings
                data_count = settings.mock_server_stream_data_count
            else:
                data_count = count
                
            url = f"{self.base_url}/mock/realtime-generator/datalake/generate/stream"
            params = {"count": data_count}
            
            logger.info(f"Mock Server에서 스트리밍 데이터 요청: {url}?count={data_count}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Mock Server에서 {len(data)}개의 스트리밍 데이터를 받았습니다.")
                
                # Mock Server 응답을 RawSensorData 모델로 변환
                raw_sensor_data_list = []
                for item in data:
                    raw_sensor_data = RawSensorData(
                        equipment_id=item.get("equipment_id"),
                        facility_id=item.get("facility_id"),
                        equipment_location=item.get("equipment_location"),
                        measured_at=item.get("measured_at"),
                        temperature=item.get("temperature"),
                        humidity=item.get("humidity"),
                        smoke_density=item.get("smoke_density"),
                        co_level=item.get("co_level"),
                        gas_level=item.get("gas_level"),
                        metadata=item.get("metadata", {})
                    )
                    raw_sensor_data_list.append(raw_sensor_data)
                
                return raw_sensor_data_list
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Mock Server 스트리밍 HTTP 오류: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Mock Server 스트리밍 요청 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"Mock Server 스트리밍 데이터 가져오기 오류: {e}")
            raise
    
    async def get_batch_data(self, count: Optional[int] = None) -> List[RawSensorData]:
        """Mock Server에서 배치용 데이터를 가져옵니다."""
        try:
            if count is None:
                from .config import settings
                data_count = settings.mock_server_batch_data_count
            else:
                data_count = count
                
            url = f"{self.base_url}/mock/realtime-generator/datalake/generate/batch"
            params = {"count": data_count}
            
            logger.info(f"Mock Server에서 배치 데이터 요청: {url}?count={data_count}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Mock Server에서 {len(data)}개의 배치 데이터를 받았습니다.")
                
                # Mock Server 응답을 RawSensorData 모델로 변환
                raw_sensor_data_list = []
                for item in data:
                    raw_sensor_data = RawSensorData(
                        equipment_id=item.get("equipment_id"),
                        facility_id=item.get("facility_id"),
                        equipment_location=item.get("equipment_location"),
                        measured_at=item.get("measured_at"),
                        temperature=item.get("temperature"),
                        humidity=item.get("humidity"),
                        smoke_density=item.get("smoke_density"),
                        co_level=item.get("co_level"),
                        gas_level=item.get("gas_level"),
                        metadata=item.get("metadata", {})
                    )
                    raw_sensor_data_list.append(raw_sensor_data)
                
                return raw_sensor_data_list
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Mock Server 배치 HTTP 오류: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Mock Server 배치 요청 오류: {e}")
            raise
        except Exception as e:
            logger.error(f"Mock Server 배치 데이터 가져오기 오류: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Mock Server 연결 상태를 확인합니다."""
        try:
            url = f"{self.base_url}/mock/realtime-generator/generate/health-check"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Mock Server 헬스체크 오류: {e}")
            return False
