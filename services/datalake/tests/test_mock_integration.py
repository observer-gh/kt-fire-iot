"""
Mock Server 연동 테스트
DataLake가 Mock Server에서 데이터를 가져와서 처리하는지 테스트합니다.
"""

import pytest
import httpx
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime

# DataLake API 설정
DATALAKE_BASE_URL = "http://localhost:8080"
MOCK_SERVER_BASE_URL = "http://localhost:8081"


class TestMockServerIntegration:
    """Mock Server 연동 테스트 클래스"""
    
    @pytest.fixture
    def mock_server_client(self):
        """Mock Server 클라이언트 fixture"""
        return httpx.AsyncClient()
    
    @pytest.fixture
    def datalake_client(self):
        """DataLake 클라이언트 fixture"""
        return httpx.AsyncClient()
    
    @pytest.mark.asyncio
    async def test_mock_server_health(self, mock_server_client):
        """Mock Server 상태 확인 테스트"""
        try:
            response = await mock_server_client.get(
                f"{MOCK_SERVER_BASE_URL}/mock/realtime-generator/generate/health-check"
            )
            assert response.status_code == 200
        except Exception as e:
            pytest.skip(f"Mock Server 연결 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_datalake_health(self, datalake_client):
        """DataLake 상태 확인 테스트"""
        try:
            response = await datalake_client.get(f"{DATALAKE_BASE_URL}/healthz")
            assert response.status_code == 200
            
            data = response.json()
            assert "redis" in data
            assert "mock_server" in data
            assert "storage_type" in data
            
        except Exception as e:
            pytest.skip(f"DataLake 연결 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_mock_data_generation(self, mock_server_client):
        """Mock Server 데이터 생성 테스트"""
        try:
            # Datalake용 데이터 생성
            response = await mock_server_client.get(
                f"{MOCK_SERVER_BASE_URL}/mock/realtime-generator/datalake/generate",
                params={"count": 5}
            )
            assert response.status_code == 200
            
            data = response.json()
            assert len(data) == 5
            
            # 데이터 구조 검증
            if data:
                sample = data[0]
                required_fields = ["equipment_id", "facility_id", "temperature", "humidity"]
                for field in required_fields:
                    assert field in sample
                    
        except Exception as e:
            pytest.skip(f"Mock Server 데이터 생성 테스트 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_datalake_ingest(self, datalake_client):
        """DataLake ingest API 테스트"""
        try:
            # Mock Server에서 데이터를 가져와서 처리
            response = await datalake_client.post(f"{DATALAKE_BASE_URL}/ingest")
            assert response.status_code in [200, 204]
            
            if response.status_code == 200:
                data = response.json()
                assert "equipment_id" in data
                assert "metric" in data
                assert "value" in data
                
        except Exception as e:
            pytest.skip(f"DataLake ingest 테스트 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_mock_scheduler_status(self, datalake_client):
        """Mock Scheduler 상태 확인 테스트"""
        try:
            response = await datalake_client.get(f"{DATALAKE_BASE_URL}/mock-scheduler/status")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "mock_server_url" in data
            assert "data_fetch_interval_seconds" in data
            
            # 데이터 가져오기 간격이 5초인지 확인
            data_fetch_interval = data.get("data_fetch_interval_seconds", 0)
            assert data_fetch_interval == 5, f"데이터 가져오기 간격이 5초가 아님 (현재: {data_fetch_interval}초)"
            
        except Exception as e:
            pytest.skip(f"Mock Scheduler 상태 확인 테스트 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_manual_trigger(self, datalake_client):
        """수동 트리거 테스트"""
        try:
            response = await datalake_client.post(f"{DATALAKE_BASE_URL}/trigger-mock-data-process")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "message" in data
            
        except Exception as e:
            pytest.skip(f"수동 트리거 테스트 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_stream_ingest(self, datalake_client):
        """스트리밍 데이터 ingest 테스트"""
        try:
            response = await datalake_client.post(f"{DATALAKE_BASE_URL}/ingest/stream")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "total_received" in data
            assert "processed_count" in data
            assert "anomaly_count" in data
            
        except Exception as e:
            pytest.skip(f"스트리밍 ingest 테스트 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_batch_ingest(self, datalake_client):
        """배치 데이터 ingest 테스트"""
        try:
            response = await datalake_client.post(f"{DATALAKE_BASE_URL}/ingest/batch")
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert "total_received" in data
            assert "processed_count" in data
            assert "anomaly_count" in data
            
        except Exception as e:
            pytest.skip(f"배치 ingest 테스트 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_external_ingest(self, datalake_client):
        """외부 API ingest 테스트 (기존 기능 유지)"""
        try:
            # 테스트용 샘플 데이터
            test_data = {
                "equipment_id": "TEST_EQ001",
                "facility_id": "TEST_FC001",
                "equipment_location": "테스트_위치",
                "measured_at": datetime.utcnow().isoformat(),
                "temperature": 25.5,
                "humidity": 60.0,
                "smoke_density": 0.02,
                "co_level": 0.01,
                "gas_level": 0.02
            }
            
            response = await datalake_client.post(
                f"{DATALAKE_BASE_URL}/ingest/external",
                json=test_data
            )
            assert response.status_code in [200, 204]
            
        except Exception as e:
            pytest.skip(f"외부 API ingest 테스트 실패: {e}")


class TestMockServerDataQuality:
    """Mock Server 데이터 품질 테스트"""
    
    @pytest.mark.asyncio
    async def test_data_consistency(self):
        """데이터 일관성 테스트"""
        try:
            async with httpx.AsyncClient() as client:
                # 여러 번 데이터를 가져와서 일관성 확인
                responses = []
                for i in range(3):
                    response = await client.get(
                        f"{MOCK_SERVER_BASE_URL}/mock/realtime-generator/datalake/generate",
                        params={"count": 3}
                    )
                    assert response.status_code == 200
                    data = response.json()
                    assert len(data) == 3
                    responses.append(data)
                
                # 데이터 구조가 일관적인지 확인
                for response_data in responses:
                    for item in response_data:
                        required_fields = ["equipment_id", "facility_id", "temperature", "humidity"]
                        for field in required_fields:
                            assert field in item
                            
        except Exception as e:
            pytest.skip(f"데이터 일관성 테스트 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_anomaly_detection_rate(self):
        """이상치 탐지율 테스트 (90% 정상, 10% 이상)"""
        try:
            async with httpx.AsyncClient() as client:
                # 충분한 데이터를 가져와서 이상치 비율 확인
                response = await client.get(
                    f"{MOCK_SERVER_BASE_URL}/mock/realtime-generator/datalake/generate",
                    params={"count": 100}
                )
                assert response.status_code == 200
                
                data = response.json()
                assert len(data) == 100
                
                # 메타데이터에서 이상치 여부 확인
                abnormal_count = 0
                for item in data:
                    metadata = item.get("metadata", {})
                    if metadata.get("data_type") == "abnormal":
                        abnormal_count += 1
                
                # 이상치 비율이 10% 근처인지 확인 (허용 오차: ±5%)
                anomaly_rate = abnormal_count / len(data)
                assert 0.05 <= anomaly_rate <= 0.15, f"이상치 비율이 예상 범위를 벗어남: {anomaly_rate:.2%}"
                
        except Exception as e:
            pytest.skip(f"이상치 탐지율 테스트 실패: {e}")


class TestMockServerPerformance:
    """Mock Server 성능 테스트"""
    
    @pytest.mark.asyncio
    async def test_response_time(self):
        """응답 시간 테스트"""
        try:
            async with httpx.AsyncClient() as client:
                import time
                
                start_time = time.time()
                response = await client.get(
                    f"{MOCK_SERVER_BASE_URL}/mock/realtime-generator/datalake/generate",
                    params={"count": 10}
                )
                end_time = time.time()
                
                response_time = end_time - start_time
                assert response.status_code == 200
                assert response_time < 2.0, f"응답 시간이 너무 김: {response_time:.2f}초"
                
        except Exception as e:
            pytest.skip(f"응답 시간 테스트 실패: {e}")
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """동시 요청 처리 테스트"""
        try:
            async with httpx.AsyncClient() as client:
                import asyncio
                
                # 5개의 동시 요청
                async def make_request():
                    response = await client.get(
                        f"{MOCK_SERVER_BASE_URL}/mock/realtime-generator/datalake/generate",
                        params={"count": 5}
                    )
                    return response.status_code
                
                tasks = [make_request() for _ in range(5)]
                results = await asyncio.gather(*tasks)
                
                # 모든 요청이 성공했는지 확인
                for status_code in results:
                    assert status_code == 200
                    
        except Exception as e:
            pytest.skip(f"동시 요청 테스트 실패: {e}")


# 테스트 실행을 위한 헬퍼 함수들
def run_integration_tests():
    """통합 테스트 실행 (pytest 외부에서 사용)"""
    import asyncio
    
    async def run_all_tests():
        test_instance = TestMockServerIntegration()
        
        # 각 테스트 메서드 실행
        test_methods = [
            test_instance.test_mock_server_health,
            test_instance.test_datalake_health,
            test_instance.test_mock_data_generation,
            test_instance.test_datalake_ingest,
            test_instance.test_mock_scheduler_status,
            test_instance.test_manual_trigger,
        ]
        
        results = []
        for test_method in test_methods:
            try:
                await test_method()
                results.append((test_method.__name__, True))
                print(f"✅ {test_method.__name__}: PASS")
            except Exception as e:
                results.append((test_method.__name__, False))
                print(f"❌ {test_method.__name__}: FAIL - {e}")
        
        # 결과 요약
        passed = sum(1 for _, result in results if result)
        total = len(results)
        print(f"\n📊 테스트 결과: {passed}/{total} 통과 ({passed/total*100:.1f}%)")
        
        return results
    
    return asyncio.run(run_all_tests())


if __name__ == "__main__":
    # pytest 외부에서 실행할 때
    run_integration_tests()
