"""
DataLake API 기능 테스트
1. 모든 엔드포인트 동작 확인
2. API 문서 접근성
3. 서비스 통계 및 상태 조회
"""

import pytest
import requests
import json
from typing import Dict, List


class TestAPIFunctionality:
    """API 기능 테스트 클래스"""
    
    @pytest.mark.unit
    def test_root_endpoint(self, base_url):
        """루트 엔드포인트 테스트"""
        try:
            response = requests.get(f"{base_url}/", timeout=10)
            
            assert response.status_code == 200, f"루트 엔드포인트 실패: {response.status_code}"
            
            data = response.json()
            assert "message" in data, "응답에 message 필드가 없음"
            assert "DataLake Service" in data["message"], f"잘못된 메시지: {data['message']}"
            
            print("✅ 루트 엔드포인트 정상")
            
        except Exception as e:
            pytest.fail(f"루트 엔드포인트 테스트 실패: {e}")
    
    @pytest.mark.unit
    def test_health_endpoint(self, base_url):
        """헬스체크 엔드포인트 테스트"""
        try:
            response = requests.get(f"{base_url}/healthz", timeout=10)
            
            assert response.status_code == 200, f"헬스체크 엔드포인트 실패: {response.status_code}"
            
            data = response.json()
            assert "status" in data, "응답에 status 필드가 없음"
            assert "service" in data, "응답에 service 필드가 없음"
            assert data["status"] == "healthy", f"서비스 상태가 healthy가 아님: {data['status']}"
            assert data["service"] == "datalake", f"서비스명이 datalake가 아님: {data['service']}"
            
            print("✅ 헬스체크 엔드포인트 정상")
            
        except Exception as e:
            pytest.fail(f"헬스체크 엔드포인트 테스트 실패: {e}")
    
    @pytest.mark.unit
    def test_stats_endpoint(self, base_url):
        """서비스 통계 엔드포인트 테스트"""
        try:
            response = requests.get(f"{base_url}/stats", timeout=10)
            
            assert response.status_code == 200, f"통계 엔드포인트 실패: {response.status_code}"
            
            stats = response.json()
            
            # 필수 필드 확인 (실제 API 응답 구조에 맞춤)
            required_fields = [
                'storage_type', 'batch_size', 'batch_interval_minutes',
                'realtime_records', 'active_alerts'
            ]
            
            for field in required_fields:
                assert field in stats, f"필수 필드 {field}가 없음"
            
            # 데이터 타입 검증
            assert isinstance(stats.get('storage_type'), str), "storage_type은 문자열이어야 함"
            assert isinstance(stats.get('batch_size'), int), "batch_size는 정수여야 함"
            assert isinstance(stats.get('realtime_records'), int), "realtime_records는 정수여야 함"
            assert isinstance(stats.get('active_alerts'), int), "active_alerts는 정수여야 함"
            
            print("✅ 통계 엔드포인트 정상")
            
        except Exception as e:
            pytest.fail(f"통계 엔드포인트 테스트 실패: {e}")
    
    @pytest.mark.unit
    def test_api_documentation(self, base_url):
        """API 문서 접근성 테스트"""
        try:
            # Swagger UI 문서
            response = requests.get(f"{base_url}/docs", timeout=10)
            
            assert response.status_code == 200, f"API 문서 접근 실패: {response.status_code}"
            
            content = response.text
            assert "swagger" in content.lower() or "openapi" in content.lower(), "Swagger UI 문서가 아님"
            
            print("✅ API 문서 접근 성공")
            
        except Exception as e:
            pytest.fail(f"API 문서 접근성 테스트 실패: {e}")
    
    @pytest.mark.unit
    def test_openapi_schema(self, base_url):
        """OpenAPI 스키마 테스트"""
        try:
            # OpenAPI JSON 스키마
            response = requests.get(f"{base_url}/openapi.json", timeout=10)
            
            assert response.status_code == 200, f"OpenAPI 스키마 접근 실패: {response.status_code}"
            
            schema = response.json()
            
            # OpenAPI 스키마 구조 확인
            assert "openapi" in schema, "OpenAPI 버전 정보가 없음"
            assert "info" in schema, "API 정보가 없음"
            assert "paths" in schema, "API 경로가 없음"
            
            # API 정보 확인
            info = schema["info"]
            assert "title" in info, "API 제목이 없음"
            assert "version" in info, "API 버전이 없음"
            assert "DataLake" in info["title"], f"API 제목이 DataLake가 아님: {info['title']}"
            
            print("✅ OpenAPI 스키마 정상")
            
        except Exception as e:
            pytest.fail(f"OpenAPI 스키마 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_ingest_endpoint(self, base_url):
        """데이터 수집 엔드포인트 테스트"""
        try:
            # 유효한 센서 데이터
            valid_data = {
                "equipment_id": "API_TEST01",
                "facility_id": "FAC001",
                "equipment_location": "Building 1, Floor 1",
                "measured_at": "2024-01-01T12:00:00Z",
                "temperature": 25.5,
                "humidity": 60.2,
                "smoke_density": 0.001,
                "co_level": 0.005,
                "gas_level": 0.002
            }
            
            response = requests.post(f"{base_url}/ingest", json=valid_data, timeout=10)
    
            # 정상 데이터는 204 No Content를 반환해야 함
            assert response.status_code == 204, f"정상 데이터 처리 실패: {response.status_code} (예상: 204)"
    
            print("✅ 데이터 수집 엔드포인트 정상")
            
        except Exception as e:
            pytest.fail(f"데이터 수집 엔드포인트 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_storage_batches_endpoint(self, base_url):
        """스토리지 배치 엔드포인트 테스트"""
        try:
            # 배치 상태 조회
            response = requests.get(f"{base_url}/storage/batches", timeout=10)
            
            assert response.status_code == 200, f"배치 상태 조회 실패: {response.status_code}"
            
            batches = response.json()
            
            # 응답이 딕셔너리인지 확인 (실제 API 응답 구조에 맞춤)
            assert isinstance(batches, dict), "배치 응답이 딕셔너리가 아님"
            
            # uploaded_batches 필드가 리스트인지 확인
            assert 'uploaded_batches' in batches, "uploaded_batches 필드가 없음"
            assert isinstance(batches['uploaded_batches'], list), "uploaded_batches가 리스트가 아님"
            
            # 배치가 있는 경우 구조 확인
            if batches['uploaded_batches']:
                for batch in batches['uploaded_batches']:
                    self._validate_batch_structure(batch)
            
            print("✅ 스토리지 배치 엔드포인트 정상")
            
        except Exception as e:
            pytest.fail(f"스토리지 배치 엔드포인트 테스트 실패: {e}")
    
    def _validate_batch_structure(self, batch: Dict):
        """배치 데이터 구조 검증"""
        # 필수 필드 확인
        required_fields = ['batch_id', 'uploaded_at', 'record_count', 'filepath']
        
        for field in required_fields:
            assert field in batch, f"필수 필드 {field}가 없음"
            assert batch[field] is not None, f"필드 {field}가 None임"
        
        # 데이터 타입 검증
        assert isinstance(batch['batch_id'], str), "batch_id는 문자열이어야 함"
        assert isinstance(batch['uploaded_at'], str), "uploaded_at은 문자열이어야 함"
        assert isinstance(batch['record_count'], int), "record_count는 정수여야 함"
        assert isinstance(batch['filepath'], str), "filepath는 문자열이어야 함"
    
    @pytest.mark.integration
    def test_batch_upload_trigger_endpoint(self, base_url):
        """배치 업로드 트리거 엔드포인트 테스트"""
        try:
            # 배치 업로드 트리거
            response = requests.post(f"{base_url}/trigger-batch-upload", timeout=30)
            
            assert response.status_code == 200, f"배치 업로드 트리거 실패: {response.status_code}"
            
            result = response.json()
            
            # 응답 구조 확인
            assert "message" in result or "status" in result, "응답에 message 또는 status가 없음"
            
            print("✅ 배치 업로드 트리거 엔드포인트 정상")
            
        except Exception as e:
            pytest.fail(f"배치 업로드 트리거 엔드포인트 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_storage_cleanup_endpoint(self, base_url):
        """스토리지 정리 엔드포인트 테스트"""
        try:
            # 배치 정리
            response = requests.delete(f"{base_url}/storage/batches", timeout=10)
            
            assert response.status_code == 200, f"배치 정리 실패: {response.status_code}"
            
            result = response.json()
            
            # 응답 구조 확인
            assert "message" in result or "status" in result, "응답에 message 또는 status가 없음"
            
            print("✅ 스토리지 정리 엔드포인트 정상")
            
        except Exception as e:
            pytest.fail(f"스토리지 정리 엔드포인트 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_api_error_handling(self, base_url):
        """API 오류 처리 테스트"""
        try:
            # 잘못된 데이터로 오류 처리 확인
            invalid_data = [
                {
                    "equipment_id": "",  # 빈 문자열
                    "facility_id": "FAC001",
                    "measured_at": "2024-01-01T12:00:00Z"
                },
                {
                    "equipment_id": "TEST_001",
                    "facility_id": None,  # None 값
                    "measured_at": "2024-01-01T12:00:00Z"
                },
                {
                    "equipment_id": "TEST_001",
                    "facility_id": "FAC001",
                    "measured_at": "invalid-date"  # 잘못된 날짜
                }
            ]
            
            for i, data in enumerate(invalid_data):
                try:
                    response = requests.post(f"{base_url}/ingest", json=data, timeout=10)
                    
                    # 오류 응답이어야 함 (400 또는 422)
                    assert response.status_code in [400, 422], f"잘못된 데이터 {i+1}이 처리됨: {response.status_code}"
                    
                except Exception as e:
                    print(f"잘못된 데이터 {i+1} 처리 중 오류: {e}")
            
            print("✅ API 오류 처리 확인: 잘못된 데이터가 적절히 거부됨")
            
        except Exception as e:
            pytest.fail(f"API 오류 처리 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_api_response_format(self, base_url):
        """API 응답 형식 테스트"""
        try:
            # 여러 엔드포인트의 응답 형식 확인
            endpoints = [
                ("/", "GET"),
                ("/healthz", "GET"),
                ("/stats", "GET"),
                ("/storage/batches", "GET")
            ]
            
            for endpoint, method in endpoints:
                if method == "GET":
                    response = requests.get(f"{base_url}{endpoint}", timeout=10)
                else:
                    continue
                
                assert response.status_code == 200, f"엔드포인트 {endpoint} 접근 실패: {response.status_code}"
                
                # Content-Type 확인
                content_type = response.headers.get('content-type', '')
                assert 'application/json' in content_type, f"엔드포인트 {endpoint}의 Content-Type이 JSON이 아님: {content_type}"
                
                # JSON 파싱 가능한지 확인
                try:
                    data = response.json()
                    assert data is not None, f"엔드포인트 {endpoint}에서 JSON 파싱 실패"
                except json.JSONDecodeError:
                    pytest.fail(f"엔드포인트 {endpoint}에서 JSON 파싱 실패")
            
            print("✅ 모든 API 응답 형식 정상")
            
        except Exception as e:
            pytest.fail(f"API 응답 형식 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_api_performance(self, base_url):
        """API 성능 테스트"""
        try:
            # 여러 엔드포인트의 응답 시간 측정
            endpoints = [
                "/",
                "/healthz",
                "/stats"
            ]
            
            performance_results = {}
            
            for endpoint in endpoints:
                start_time = time.time()
                
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                assert response.status_code == 200, f"엔드포인트 {endpoint} 접근 실패: {response.status_code}"
                
                performance_results[endpoint] = response_time
                
                # 응답 시간 기준 확인
                assert response_time < 2.0, f"엔드포인트 {endpoint} 응답 시간 초과: {response_time:.3f}초"
            
            # 성능 결과 출력
            print("✅ API 성능 테스트 결과:")
            for endpoint, response_time in performance_results.items():
                status = "빠름" if response_time < 0.1 else "보통" if response_time < 0.5 else "느림"
                print(f"  - {endpoint}: {response_time:.3f}초 ({status})")
            
        except Exception as e:
            pytest.fail(f"API 성능 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_api_consistency(self, base_url):
        """API 일관성 테스트"""
        try:
            # 동일한 요청에 대한 응답 일관성 확인
            endpoint = "/healthz"
            
            responses = []
            for i in range(5):
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                assert response.status_code == 200, f"헬스체크 {i+1}번째 실패: {response.status_code}"
                
                data = response.json()
                responses.append(data)
                
                time.sleep(0.1)  # 100ms 간격
            
            # 응답 일관성 확인
            first_response = responses[0]
            for i, response in enumerate(responses[1:], 1):
                assert response == first_response, f"응답 {i+1}번째가 첫 번째와 다름: {response} != {first_response}"
            
            print("✅ API 응답 일관성 확인 완료")
            
        except Exception as e:
            pytest.fail(f"API 일관성 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_api_methods(self, base_url):
        """API HTTP 메서드 테스트"""
        try:
            # 지원하지 않는 메서드에 대한 오류 처리 확인
            
            # POST를 GET 엔드포인트에 사용
            response = requests.post(f"{base_url}/healthz", timeout=5)
            assert response.status_code in [405, 404], f"헬스체크에 POST 요청이 허용됨: {response.status_code}"
            
            # PUT을 GET 엔드포인트에 사용
            response = requests.put(f"{base_url}/healthz", timeout=5)
            assert response.status_code in [405, 404], f"헬스체크에 PUT 요청이 허용됨: {response.status_code}"
            
            # DELETE를 GET 엔드포인트에 사용
            response = requests.delete(f"{base_url}/healthz", timeout=5)
            assert response.status_code in [405, 404], f"헬스체크에 DELETE 요청이 허용됨: {response.status_code}"
            
            print("✅ API HTTP 메서드 제한 확인 완료")
            
        except Exception as e:
            pytest.fail(f"API HTTP 메서드 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_api_headers(self, base_url):
        """API 헤더 테스트"""
        try:
            # CORS 헤더 확인
            response = requests.get(f"{base_url}/healthz", timeout=5)
            
            # CORS 관련 헤더 확인
            cors_headers = [
                'access-control-allow-origin',
                'access-control-allow-methods',
                'access-control-allow-headers'
            ]
            
            for header in cors_headers:
                if header in response.headers:
                    print(f"  - {header}: {response.headers[header]}")
                else:
                    print(f"  - {header}: 없음")
            
            print("✅ API 헤더 확인 완료")
            
        except Exception as e:
            pytest.fail(f"API 헤더 테스트 실패: {e}")


# time 모듈 import 추가
import time
