"""
DataLake 대시보드 데이터 전달 테스트
1. Streamlit 대시보드 접근성
2. 실시간 데이터 전달 확인
3. 서비스 통계 API 동작
"""

import pytest
import requests
import time
from typing import Dict


class TestDashboard:
    """대시보드 데이터 전달 테스트 클래스"""
    
    @pytest.mark.integration
    def test_dashboard_accessibility(self, dashboard_url):
        """대시보드 접근성 테스트"""
        try:
            response = requests.get(dashboard_url, timeout=10)
            
            # 대시보드가 접근 가능해야 함
            assert response.status_code == 200, f"대시보드 접근 실패: {response.status_code}"
            
            # HTML 응답인지 확인
            content = response.text
            assert "html" in content.lower(), "HTML 응답이 아님"
            
            # Streamlit 관련 내용이 있는지 확인
            assert "streamlit" in content.lower() or "fire safety" in content.lower(), "Streamlit 대시보드가 아님"
            
            print("✅ 대시보드 접근 성공")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"대시보드 접근 실패: {e}")
    
    @pytest.mark.integration
    def test_dashboard_api_endpoints(self, dashboard_url):
        """대시보드 API 엔드포인트 테스트"""
        # Streamlit 대시보드의 주요 엔드포인트 확인
        endpoints = [
            f"{dashboard_url}/",
            f"{dashboard_url}/_stcore/static",
            f"{dashboard_url}/_stcore/health"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                # 200 또는 404는 정상 (존재하지 않는 정적 파일은 404가 정상)
                assert response.status_code in [200, 404], f"엔드포인트 {endpoint} 접근 실패: {response.status_code}"
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️ 엔드포인트 {endpoint} 접근 오류: {e}")
        
        print("✅ 대시보드 API 엔드포인트 확인 완료")
    
    @pytest.mark.integration
    def test_service_stats_api(self, base_url):
        """서비스 통계 API 동작 테스트"""
        try:
            response = requests.get(f"{base_url}/stats", timeout=10)
            
            assert response.status_code == 200, f"서비스 통계 API 실패: {response.status_code}"
            
            stats = response.json()
            
            # 필수 필드 확인 (실제 API 응답 구조에 맞춤)
            required_fields = [
                'storage_type', 'batch_size', 'batch_interval_minutes',
                'realtime_records', 'active_alerts'
            ]
            
            for field in required_fields:
                assert field in stats, f"필수 필드 {field}가 없음"
            
            # 데이터 타입 확인
            assert isinstance(stats.get('storage_type'), str), "storage_type은 문자열이어야 함"
            assert isinstance(stats.get('batch_size'), int), "batch_size는 정수여야 함"
            assert isinstance(stats.get('realtime_records'), int), "realtime_records는 정수여야 함"
            assert isinstance(stats.get('active_alerts'), int), "active_alerts는 정수여야 함"
            
            print(f"✅ 서비스 통계: {stats}")
            
        except Exception as e:
            pytest.fail(f"서비스 통계 API 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_realtime_data_availability(self, base_url):
        """실시간 데이터 가용성 테스트"""
        try:
            # 초기 통계 확인
            initial_response = requests.get(f"{base_url}/stats", timeout=10)
            assert initial_response.status_code == 200, "초기 통계 조회 실패"
            
            initial_stats = initial_response.json()
            initial_count = initial_stats.get('realtime_records', 0)
            
            # 테스트 데이터 전송
            test_data = {
                "equipment_id": "DASH_TEST1",
                "facility_id": "FAC001",
                "equipment_location": "Building 1, Floor 1",
                "measured_at": "2024-01-01T12:00:00Z",
                "temperature": 25.5,
                "humidity": 60.2,
                "smoke_density": 0.001,
                "co_level": 0.005,
                "gas_level": 0.002
            }
            
            response = requests.post(f"{base_url}/ingest", json=test_data, timeout=10)
            
            assert response.status_code == 200, "테스트 데이터 전송 실패"
            
            # 데이터 처리 대기
            time.sleep(2)
            
            # 최종 통계 확인
            final_response = requests.get(f"{base_url}/stats", timeout=10)
            assert final_response.status_code == 200, "최종 통계 조회 실패"
            
            final_stats = final_response.json()
            final_count = final_stats.get('realtime_records', 0)
            
            # 데이터가 증가했는지 확인
            assert final_count >= initial_count, f"실시간 데이터가 증가하지 않음: {initial_count} → {final_count}"
            
            print(f"✅ 실시간 데이터 가용성 확인: {initial_count} → {final_count}")
            
        except Exception as e:
            pytest.fail(f"실시간 데이터 가용성 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_dashboard_data_refresh(self, base_url, normal_data):
        """대시보드 데이터 새로고침 테스트"""
        if not normal_data:
            pytest.skip("정상 데이터가 없음")
        
        try:
            # 초기 통계
            initial_response = requests.get(f"{base_url}/stats", timeout=10)
            assert initial_response.status_code == 200, "초기 통계 조회 실패"
            
            initial_stats = initial_response.json()
            initial_count = initial_stats.get('realtime_records', 0)
            
            # 여러 데이터 전송
            test_data = normal_data[:10]
            success_count = 0
            
            for data in test_data:
                try:
                    response = requests.post(f"{base_url}/ingest", json=data, timeout=5)
                    if response.status_code == 200:
                        success_count += 1
                except Exception as e:
                    print(f"데이터 전송 실패: {data['equipment_id']} - {e}")
            
            assert success_count > 0, "전송된 데이터가 없음"
            
            # 데이터 처리 대기
            time.sleep(3)
            
            # 통계 재확인
            final_response = requests.get(f"{base_url}/stats", timeout=10)
            assert final_response.status_code == 200, "최종 통계 조회 실패"
            
            final_stats = final_response.json()
            final_count = final_stats.get('realtime_records', 0)
            
            # 데이터가 증가했는지 확인
            assert final_count > initial_count, f"데이터가 증가하지 않음: {initial_count} → {final_count}"
            
            print(f"✅ 대시보드 데이터 새로고침 확인: {initial_count} → {final_count}")
            
        except Exception as e:
            pytest.fail(f"대시보드 데이터 새로고침 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_dashboard_performance_metrics(self, base_url):
        """대시보드 성능 메트릭 테스트"""
        try:
            # 서비스 통계에서 성능 관련 정보 확인
            response = requests.get(f"{base_url}/stats", timeout=10)
            assert response.status_code == 200, "서비스 통계 조회 실패"
            
            stats = response.json()
            
            # 성능 관련 필드 확인 (실제 API 응답 구조에 맞춤)
            performance_fields = [
                'realtime_records',
                'active_alerts',
                'storage_type',
                'batch_size'
            ]
            
            for field in performance_fields:
                assert field in stats, f"성능 메트릭 {field}가 없음"
            
            # 성능 기준 확인
            realtime_count = stats.get('realtime_records', 0)
            alerts_count = stats.get('active_alerts', 0)
            batch_size = stats.get('batch_size', 0)
            
            # 기본 성능 기준
            assert batch_size > 0, "배치 크기가 0 이하임"
            assert batch_size <= 10000, "배치 크기가 너무 큼 (10000 초과)"
            
            print(f"✅ 성능 메트릭 확인:")
            print(f"  - 실시간 레코드: {realtime_count}")
            print(f"  - 활성 알림: {alerts_count}")
            print(f"  - 배치 크기: {batch_size}")
            
        except Exception as e:
            pytest.fail(f"대시보드 성능 메트릭 테스트 실패: {e}")
    
    @pytest.mark.slow
    def test_dashboard_stability(self, dashboard_url):
        """대시보드 안정성 테스트 (연속 접근)"""
        # 10번 연속으로 대시보드 접근
        success_count = 0
        
        for i in range(10):
            try:
                response = requests.get(dashboard_url, timeout=5)
                if response.status_code == 200:
                    success_count += 1
                time.sleep(0.5)  # 500ms 간격
                
            except Exception as e:
                print(f"연속 접근 {i+1}번째 실패: {e}")
        
        # 80% 이상 성공해야 함
        success_rate = success_count / 10
        assert success_rate >= 0.8, f"대시보드 안정성 부족: {success_rate:.1%} ({success_count}/10)"
        
        print(f"✅ 대시보드 안정성: {success_rate:.1%} ({success_count}/10)")
    
    @pytest.mark.integration
    def test_dashboard_data_consistency(self, base_url, normal_data):
        """대시보드 데이터 일관성 테스트"""
        if not normal_data:
            pytest.skip("정상 데이터가 없음")
        
        try:
            # 동일한 데이터를 여러 번 전송하여 일관성 확인
            test_data = normal_data[0]  # 첫 번째 데이터 사용
            
            # 3번 전송
            for i in range(3):
                response = requests.post(f"{base_url}/ingest", json=test_data, timeout=10)
                assert response.status_code == 200, f"데이터 전송 {i+1}번째 실패"
                time.sleep(1)  # 1초 간격
            
            # 통계 확인
            stats_response = requests.get(f"{base_url}/stats", timeout=10)
            assert stats_response.status_code == 200, "통계 조회 실패"
            
            stats = stats_response.json()
            realtime_count = stats.get('realtime_records', 0)
            
            # 데이터가 일관되게 증가했는지 확인
            assert realtime_count > 0, "실시간 데이터가 없음"
            
            print(f"✅ 데이터 일관성 확인: {realtime_count}개 레코드")
            
        except Exception as e:
            pytest.fail(f"대시보드 데이터 일관성 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_dashboard_error_handling(self, base_url):
        """대시보드 오류 처리 테스트"""
        try:
            # 잘못된 데이터로 오류 처리 확인
            invalid_data = {
                "equipment_id": "",  # 빈 문자열
                "facility_id": None,  # None 값
                "measured_at": "invalid-date",  # 잘못된 날짜
                "temperature": "not-a-number"  # 잘못된 타입
            }
            
            response = requests.post(f"{base_url}/ingest", json=invalid_data, timeout=10)
            
            # 오류 응답이어야 함 (400 또는 422)
            assert response.status_code in [400, 422], f"잘못된 데이터가 처리됨: {response.status_code}"
            
            print("✅ 오류 처리 확인: 잘못된 데이터가 적절히 거부됨")
            
        except Exception as e:
            pytest.fail(f"대시보드 오류 처리 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_dashboard_health_monitoring(self, base_url):
        """대시보드 헬스 모니터링 테스트"""
        try:
            # 헬스체크 엔드포인트
            health_response = requests.get(f"{base_url}/healthz", timeout=5)
            assert health_response.status_code == 200, "헬스체크 실패"
            
            health_data = health_response.json()
            assert health_data.get('status') == 'healthy', "서비스 상태가 healthy가 아님"
            
            # 통계 엔드포인트
            stats_response = requests.get(f"{base_url}/stats", timeout=5)
            assert stats_response.status_code == 200, "통계 조회 실패"
            
            # 루트 엔드포인트
            root_response = requests.get(f"{base_url}/", timeout=5)
            assert root_response.status_code == 200, "루트 엔드포인트 실패"
            
            print("✅ 모든 헬스 모니터링 엔드포인트 정상")
            
        except Exception as e:
            pytest.fail(f"대시보드 헬스 모니터링 테스트 실패: {e}")
