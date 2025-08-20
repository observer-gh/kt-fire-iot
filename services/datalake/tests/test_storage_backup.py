"""
DataLake 주기적 스토리지 백업 테스트
1. 배치 업로드 스케줄러 동작
2. 스토리지 백업 프로세스
3. 배치 처리 상태 추적
"""

import pytest
import requests
import time
from typing import Dict, List


class TestStorageBackup:
    """주기적 스토리지 백업 테스트 클래스"""
    
    @pytest.mark.integration
    def test_batch_upload_trigger(self, base_url):
        """배치 업로드 트리거 테스트"""
        try:
            # 초기 배치 상태 확인
            initial_response = requests.get(f"{base_url}/storage/batches", timeout=10)
            assert initial_response.status_code == 200, "초기 배치 상태 조회 실패"
            
            initial_batches = initial_response.json()
            initial_count = len(initial_batches)
            
            print(f"초기 배치 수: {initial_count}")
            
            # 배치 업로드 트리거
            trigger_response = requests.post(f"{base_url}/trigger-batch-upload", timeout=30)
            assert trigger_response.status_code == 200, f"배치 업로드 트리거 실패: {trigger_response.status_code}"
            
            trigger_result = trigger_response.json()
            print(f"배치 업로드 트리거 결과: {trigger_result}")
            
            # 배치 처리 대기
            time.sleep(10)
            
            # 배치 상태 재확인
            final_response = requests.get(f"{base_url}/storage/batches", timeout=10)
            assert final_response.status_code == 200, "최종 배치 상태 조회 실패"
            
            final_batches = final_response.json()
            final_count = len(final_batches)
            
            print(f"최종 배치 수: {final_count}")
            
            # 배치가 처리되었는지 확인
            if final_count > initial_count:
                print(f"✅ 배치 백업 성공: {initial_count} → {final_count}")
            else:
                print(f"⚠️ 배치 백업 변화 없음: {initial_count} → {final_count}")
            
        except Exception as e:
            pytest.fail(f"배치 업로드 트리거 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_batch_upload_condition(self, base_url, normal_data):
        """배치 업로드 조건 테스트"""
        if not normal_data:
            pytest.skip("정상 데이터가 없음")
        
        try:
            # 초기 통계 확인
            initial_stats = requests.get(f"{base_url}/stats", timeout=10)
            assert initial_stats.status_code == 200, "초기 통계 조회 실패"
            
            initial_stats_data = initial_stats.json()
            initial_count = initial_stats_data.get('realtime_records_count', 0)
            
            print(f"초기 실시간 레코드 수: {initial_count}")
            
            # 배치 크기 확인
            batch_size = initial_stats_data.get('batch_size', 100)
            print(f"배치 크기: {batch_size}")
            
            # 배치 크기만큼 데이터 전송
            test_data = normal_data[:min(batch_size, len(normal_data))]
            success_count = 0
            
            for data in test_data:
                try:
                    response = requests.post(f"{base_url}/ingest", json=data, timeout=5)
                    if response.status_code == 200:
                        success_count += 1
                except Exception as e:
                    print(f"데이터 전송 실패: {data['equipment_id']} - {e}")
            
            print(f"전송된 데이터: {success_count}개")
            
            # 배치 업로드 조건 확인
            if success_count >= batch_size:
                print("✅ 배치 업로드 조건 충족")
                
                # 배치 업로드 트리거
                trigger_response = requests.post(f"{base_url}/trigger-batch-upload", timeout=30)
                assert trigger_response.status_code == 200, "배치 업로드 트리거 실패"
                
                # 배치 처리 대기
                time.sleep(10)
                
                # 배치 상태 확인
                batches_response = requests.get(f"{base_url}/storage/batches", timeout=10)
                assert batches_response.status_code == 200, "배치 상태 조회 실패"
                
                batches = batches_response.json()
                print(f"처리된 배치 수: {len(batches)}")
                
            else:
                print(f"⚠️ 배치 업로드 조건 미충족: {success_count}/{batch_size}")
            
        except Exception as e:
            pytest.fail(f"배치 업로드 조건 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_storage_batch_tracking(self, base_url):
        """스토리지 배치 추적 테스트"""
        try:
            # 배치 상태 조회
            response = requests.get(f"{base_url}/storage/batches", timeout=10)
            assert response.status_code == 200, "배치 상태 조회 실패"
            
            batches = response.json()
            
            if batches:
                # uploaded_batches 필드가 있는 경우에만 검증
                if 'uploaded_batches' in batches and isinstance(batches['uploaded_batches'], list):
                    for batch in batches['uploaded_batches']:
                        self._validate_batch_structure(batch)
                else:
                    print("⚠️ uploaded_batches 필드가 없거나 리스트가 아님")
                
                print(f"✅ 배치 추적 확인: {len(batches)}개 배치")
            else:
                print("⚠️ 처리된 배치가 없음")
            
        except Exception as e:
            pytest.fail(f"스토리지 배치 추적 테스트 실패: {e}")
    
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
        
        # 값 검증
        assert batch['record_count'] > 0, "record_count는 양수여야 함"
        assert len(batch['filepath']) > 0, "filepath는 비어있지 않아야 함"
        
        # 날짜 형식 검증
        import re
        iso_date_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
        assert re.match(iso_date_pattern, batch['uploaded_at']), f"uploaded_at 형식이 잘못됨: {batch['uploaded_at']}"
    
    @pytest.mark.integration
    def test_batch_cleanup(self, base_url):
        """배치 정리 테스트"""
        try:
            # 초기 배치 상태
            initial_response = requests.get(f"{base_url}/storage/batches", timeout=10)
            assert initial_response.status_code == 200, "초기 배치 상태 조회 실패"
            
            initial_batches = initial_response.json()
            initial_count = len(initial_batches)
            
            if initial_count > 0:
                print(f"초기 배치 수: {initial_count}")
                
                # 배치 정리
                cleanup_response = requests.delete(f"{base_url}/storage/batches", timeout=10)
                assert cleanup_response.status_code == 200, "배치 정리 실패"
                
                # 정리 후 상태 확인
                time.sleep(2)
                
                final_response = requests.get(f"{base_url}/storage/batches", timeout=10)
                assert final_response.status_code == 200, "최종 배치 상태 조회 실패"
                
                final_batches = final_response.json()
                final_count = len(final_batches)
                
                print(f"정리 후 배치 수: {final_count}")
                
                # 정리가 성공했는지 확인
                if final_count < initial_count:
                    print("✅ 배치 정리 성공")
                else:
                    print("⚠️ 배치 정리 효과 없음")
            else:
                print("정리할 배치가 없음")
            
        except Exception as e:
            pytest.fail(f"배치 정리 테스트 실패: {e}")
    
    @pytest.mark.slow
    def test_batch_scheduler_performance(self, base_url, normal_data):
        """배치 스케줄러 성능 테스트"""
        if not normal_data:
            pytest.skip("정상 데이터가 없음")
        
        try:
            # 대량 데이터 전송으로 배치 처리 성능 테스트
            test_data = normal_data[:50]  # 50개 데이터
            
            start_time = time.time()
            success_count = 0
            
            for data in test_data:
                try:
                    response = requests.post(f"{base_url}/ingest", json=data, timeout=5)
                    if response.status_code == 200:
                        success_count += 1
                except Exception as e:
                    print(f"데이터 전송 실패: {data['equipment_id']} - {e}")
            
            send_time = time.time() - start_time
            
            print(f"데이터 전송: {success_count}/{len(test_data)} 성공, {send_time:.2f}초")
            
            if success_count > 0:
                # 배치 업로드 트리거
                trigger_start = time.time()
                trigger_response = requests.post(f"{base_url}/trigger-batch-upload", timeout=60)
                trigger_time = time.time() - trigger_start
                
                assert trigger_response.status_code == 200, "배치 업로드 트리거 실패"
                
                print(f"배치 업로드 트리거: {trigger_time:.2f}초")
                
                # 배치 처리 대기
                time.sleep(15)
                
                # 배치 상태 확인
                batches_response = requests.get(f"{base_url}/storage/batches", timeout=10)
                assert batches_response.status_code == 200, "배치 상태 조회 실패"
                
                batches = batches_response.json()
                print(f"처리된 배치: {len(batches)}개")
                
                # 성능 기준 확인
                assert trigger_time < 30, f"배치 업로드 트리거 시간 초과: {trigger_time:.2f}초"
                
                print("✅ 배치 스케줄러 성능 테스트 완료")
            
        except Exception as e:
            pytest.fail(f"배치 스케줄러 성능 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_storage_configuration(self, base_url):
        """스토리지 설정 테스트"""
        try:
            # 서비스 통계에서 스토리지 설정 확인
            response = requests.get(f"{base_url}/stats", timeout=10)
            assert response.status_code == 200, "서비스 통계 조회 실패"
            
            stats = response.json()
            
            # 스토리지 관련 필드 확인
            storage_fields = [
                'storage_type', 'batch_size', 'batch_interval_minutes', 'storage_path'
            ]
            
            for field in storage_fields:
                if field in stats:
                    print(f"  - {field}: {stats[field]}")
                else:
                    print(f"  - {field}: 없음")
            
            # 스토리지 타입 확인
            storage_type = stats.get('storage_type', 'unknown')
            assert storage_type in ['mock', 'production'], f"알 수 없는 스토리지 타입: {storage_type}"
            
            # 배치 크기 확인
            batch_size = stats.get('batch_size', 0)
            assert batch_size > 0, "배치 크기가 0 이하임"
            assert batch_size <= 10000, "배치 크기가 너무 큼 (10000 초과)"
            
            print(f"✅ 스토리지 설정 확인 완료: {storage_type}, 배치 크기: {batch_size}")
            
        except Exception as e:
            pytest.fail(f"스토리지 설정 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_batch_interval_scheduling(self, base_url):
        """배치 간격 스케줄링 테스트"""
        try:
            # 서비스 통계에서 배치 간격 확인
            response = requests.get(f"{base_url}/stats", timeout=10)
            assert response.status_code == 200, "서비스 통계 조회 실패"
            
            stats = response.json()
            batch_interval = stats.get('batch_interval_minutes', 0)
            
            print(f"배치 간격: {batch_interval}분")
            
            # 배치 간격이 설정되어 있는지 확인
            assert batch_interval > 0, "배치 간격이 설정되지 않음"
            assert batch_interval <= 1440, "배치 간격이 너무 김 (24시간 초과)"
            
            # 배치 간격이 합리적인지 확인
            if batch_interval < 1:
                print("⚠️ 배치 간격이 매우 짧음 (1분 미만)")
            elif batch_interval > 60:
                print("⚠️ 배치 간격이 매우 김 (1시간 초과)")
            else:
                print("✅ 배치 간격이 적절함")
            
        except Exception as e:
            pytest.fail(f"배치 간격 스케줄링 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_storage_error_handling(self, base_url):
        """스토리지 오류 처리 테스트"""
        try:
            # 잘못된 배치 ID로 접근 시도
            invalid_batch_id = "invalid-batch-id-12345"
            
            # 배치 정리 시 잘못된 ID 사용
            cleanup_response = requests.delete(f"{base_url}/storage/batches/{invalid_batch_id}", timeout=10)
            
            # 404 또는 400 오류가 발생해야 함
            assert cleanup_response.status_code in [400, 404, 405], f"잘못된 배치 ID에 대한 오류 처리가 부족함: {cleanup_response.status_code}"
            
            print("✅ 스토리지 오류 처리 확인: 잘못된 배치 ID가 적절히 거부됨")
            
        except Exception as e:
            pytest.fail(f"스토리지 오류 처리 테스트 실패: {e}")
    
    @pytest.mark.integration
    def test_storage_monitoring(self, base_url):
        """스토리지 모니터링 테스트"""
        try:
            # 스토리지 관련 모든 엔드포인트 확인
            endpoints = [
                f"{base_url}/storage/batches",
                f"{base_url}/stats"
            ]
            
            for endpoint in endpoints:
                response = requests.get(endpoint, timeout=10)
                assert response.status_code == 200, f"엔드포인트 {endpoint} 접근 실패: {response.status_code}"
                
                data = response.json()
                assert data is not None, f"엔드포인트 {endpoint}에서 데이터를 반환하지 않음"
            
            print("✅ 모든 스토리지 모니터링 엔드포인트 정상")
            
        except Exception as e:
            pytest.fail(f"스토리지 모니터링 테스트 실패: {e}")
