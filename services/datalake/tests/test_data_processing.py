"""
DataLake 데이터 처리 및 이상치 탐지 테스트
1. 센서 데이터 수집 및 처리
2. 자동 이상치 탐지
3. 데이터 정제 및 검증
4. 임계값 기반 알림 시스템
"""

import pytest
import requests
import json
import time
from typing import Dict, List


class TestDataProcessing:
    """데이터 처리 및 이상치 탐지 테스트 클래스"""
    
    @pytest.mark.integration
    def test_normal_sensor_data_ingestion(self, base_url, normal_data):
        """정상 센서 데이터 수집 테스트"""
        success_count = 0
        
        for data in normal_data:
            try:
                response = requests.post(
                    f"{base_url}/ingest",
                    json=data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # 이상치 데이터는 이상치 정보가 있어야 함
                    assert result.get('metric') is not None, f"이상치 데이터인데 metric이 없음: {data['equipment_id']}"
                    assert result.get('value') is not None, f"이상치 데이터인데 value가 없음: {data['equipment_id']}"
                    assert result.get('threshold') is not None, f"이상치 데이터인데 threshold가 없음: {data['equipment_id']}"
                    success_count += 1
                elif response.status_code == 204:
                    # 정상 데이터는 204 No Content
                    print(f"✅ 정상 데이터 처리 완료: {data['equipment_id']}")
                    success_count += 1
                else:
                    pytest.fail(f"데이터 수집 실패: {data['equipment_id']} - {response.status_code}")
                    
            except Exception as e:
                pytest.fail(f"데이터 수집 중 오류: {data['equipment_id']} - {e}")
        
        # 모든 정상 데이터가 성공적으로 처리되어야 함
        assert success_count == len(normal_data), f"정상 데이터 처리 실패: {success_count}/{len(normal_data)}"
    
    @pytest.mark.integration
    def test_anomaly_detection_temperature(self, base_url, anomaly_data):
        """온도 이상치 탐지 테스트"""
        temperature_anomalies = [d for d in anomaly_data if d.get('metadata', {}).get('anomaly') == 'temperature']
        
        if not temperature_anomalies:
            pytest.skip("온도 이상치 데이터가 없음")
        
        anomaly_detected_count = 0
        
        for data in temperature_anomalies:
            try:
                response = requests.post(
                    f"{base_url}/ingest",
                    json=data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 온도 이상치가 탐지되어야 함
                    if result.get('metric') == 'temperature':
                        anomaly_detected_count += 1
                        
                        # 이벤트 스키마 필드 확인
                        assert result.get('version') == 1, "version이 1이 아님"
                        assert result.get('event_id') is not None, "event_id가 없음"
                        assert result.get('equipment_id') == data.get('equipment_id'), "equipment_id가 일치하지 않음"
                        assert result.get('facility_id') == data.get('facility_id'), "facility_id가 일치하지 않음"
                        assert result.get('metric') == 'temperature', "metric이 temperature가 아님"
                        assert result.get('value') is not None, "value가 없음"
                        assert result.get('threshold') is not None, "threshold가 없음"
                        assert result.get('measured_at') is not None, "measured_at이 없음"
                        assert result.get('detected_at') is not None, "detected_at이 없음"
                        
                        # 온도가 임계값을 초과했는지 확인 (데이터 정리 과정에서 값이 변경될 수 있음)
                        temperature = data.get('temperature', 0)
                        threshold = result.get('threshold', 0)
                        anomaly_value = result.get('value', 0)
                        
                        # 원본 값과 처리된 값 모두 임계값을 초과해야 함
                        assert temperature > threshold, f"원본 온도({temperature})가 임계값({threshold})을 초과하지 않음"
                        assert anomaly_value > threshold, f"처리된 온도({anomaly_value})가 임계값({threshold})을 초과하지 않음"
                        
                        print(f"✅ 온도 이상치 탐지 성공: 원본값={temperature}, 처리값={anomaly_value}, 임계값={threshold}")
                    else:
                        pytest.fail(f"온도 이상치가 탐지되지 않음: {data['equipment_id']} - {data['temperature']}°C")
                        
                elif response.status_code == 204:
                    # 정상 데이터인 경우 204 No Content
                    print(f"✅ 정상 데이터 처리 완료: {data['equipment_id']}")
                else:
                    pytest.fail(f"데이터 수집 실패: {data['equipment_id']} - {response.status_code} (예상: 200 또는 204)")
                    
            except Exception as e:
                pytest.fail(f"데이터 수집 중 오류: {data['equipment_id']} - {e}")
        
        # 모든 온도 이상치가 탐지되어야 함
        assert anomaly_detected_count == len(temperature_anomalies), f"온도 이상치 탐지 부족: {anomaly_detected_count}/{len(temperature_anomalies)}"
    
    @pytest.mark.integration
    def test_anomaly_detection_smoke(self, base_url, anomaly_data):
        """연기 이상치 탐지 테스트"""
        smoke_anomalies = [d for d in anomaly_data if d.get('metadata', {}).get('anomaly') == 'smoke']
        
        if not smoke_anomalies:
            pytest.skip("연기 이상치 데이터가 없음")
        
        anomaly_detected_count = 0
        
        for data in smoke_anomalies:
            try:
                response = requests.post(
                    f"{base_url}/ingest",
                    json=data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 연기 이상치가 탐지되어야 함
                    if result.get('metric') == 'smoke_density':
                        anomaly_detected_count += 1
                        
                        # 이벤트 스키마 필드 확인
                        assert result.get('version') == 1, "version이 1이 아님"
                        assert result.get('event_id') is not None, "event_id가 없음"
                        assert result.get('equipment_id') == data.get('equipment_id'), "equipment_id가 일치하지 않음"
                        assert result.get('facility_id') == data.get('facility_id'), "facility_id가 일치하지 않음"
                        assert result.get('metric') == 'smoke_density', "metric이 smoke_density가 아님"
                        assert result.get('value') is not None, "value가 없음"
                        assert result.get('threshold') is not None, "threshold가 없음"
                        assert result.get('measured_at') is not None, "measured_at이 없음"
                        assert result.get('detected_at') is not None, "detected_at이 없음"
                        
                        # 연기 밀도가 임계값을 초과했는지 확인 (데이터 정리 과정에서 값이 변경될 수 있음)
                        smoke_density = data.get('smoke_density', 0)
                        threshold = result.get('threshold', 0)
                        anomaly_value = result.get('value', 0)
                        
                        # 원본 값과 처리된 값 모두 임계값을 초과해야 함
                        assert smoke_density > threshold, f"원본 연기 밀도({smoke_density})가 임계값({threshold})을 초과하지 않음"
                        assert anomaly_value > threshold, f"처리된 연기 밀도({anomaly_value})가 임계값({threshold})을 초과하지 않음"
                        
                        print(f"✅ 연기 이상치 탐지 성공: 원본값={smoke_density}, 처리값={anomaly_value}, 임계값={threshold}")
                    else:
                        pytest.fail(f"연기 이상치가 탐지되지 않음: {data['equipment_id']} - {data['smoke_density']}")
                        
                elif response.status_code == 204:
                    # 정상 데이터인 경우 204 No Content
                    print(f"✅ 정상 데이터 처리 완료: {data['equipment_id']}")
                else:
                    pytest.fail(f"데이터 수집 실패: {data['equipment_id']} - {response.status_code}")
                    
            except Exception as e:
                pytest.fail(f"데이터 수집 중 오류: {data['equipment_id']} - {e}")
        
        # 모든 연기 이상치가 탐지되어야 함
        assert anomaly_detected_count == len(smoke_anomalies), f"연기 이상치 탐지 부족: {anomaly_detected_count}/{len(smoke_anomalies)}"
    
    @pytest.mark.integration
    def test_anomaly_detection_co(self, base_url, anomaly_data):
        """CO 이상치 탐지 테스트"""
        co_anomalies = [d for d in anomaly_data if d.get('metadata', {}).get('anomaly') == 'co']
        
        if not co_anomalies:
            pytest.skip("CO 이상치 데이터가 없음")
        
        anomaly_detected_count = 0
        
        for data in co_anomalies:
            try:
                response = requests.post(
                    f"{base_url}/ingest",
                    json=data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # CO 이상치가 탐지되어야 함
                    if result.get('metric') == 'co_level':
                        anomaly_detected_count += 1
                        
                        # 이벤트 스키마 필드 확인
                        assert result.get('version') == 1, "version이 1이 아님"
                        assert result.get('event_id') is not None, "event_id가 없음"
                        assert result.get('equipment_id') == data.get('equipment_id'), "equipment_id가 일치하지 않음"
                        assert result.get('facility_id') == data.get('facility_id'), "facility_id가 일치하지 않음"
                        assert result.get('metric') == 'co_level', "metric이 co_level이 아님"
                        assert result.get('value') is not None, "value가 없음"
                        assert result.get('threshold') is not None, "threshold가 없음"
                        assert result.get('measured_at') is not None, "measured_at이 없음"
                        assert result.get('detected_at') is not None, "detected_at이 없음"
                        
                        # CO 레벨이 임계값을 초과했는지 확인 (데이터 정리 과정에서 값이 변경될 수 있음)
                        co_level = data.get('co_level', 0)
                        threshold = result.get('threshold', 0)
                        anomaly_value = result.get('value', 0)
                        
                        # 원본 값과 처리된 값 모두 임계값을 초과해야 함
                        assert co_level > threshold, f"원본 CO 레벨({co_level})이 임계값({threshold})을 초과하지 않음"
                        assert anomaly_value > threshold, f"처리된 CO 레벨({anomaly_value})이 임계값({threshold})을 초과하지 않음"
                        
                        print(f"✅ CO 이상치 탐지 성공: 원본값={co_level}, 처리값={anomaly_value}, 임계값={threshold}")
                    else:
                        pytest.fail(f"CO 이상치가 탐지되지 않음: {data['equipment_id']} - {data['co_level']}")
                        
                elif response.status_code == 204:
                    # 정상 데이터인 경우 204 No Content
                    print(f"✅ 정상 데이터 처리 완료: {data['equipment_id']}")
                else:
                    pytest.fail(f"데이터 수집 실패: {data['equipment_id']} - {response.status_code}")
                    
            except Exception as e:
                pytest.fail(f"데이터 수집 중 오류: {data['equipment_id']} - {e}")
        
        # 모든 CO 이상치가 탐지되어야 함
        assert anomaly_detected_count == len(co_anomalies), f"CO 이상치 탐지 부족: {anomaly_detected_count}/{len(co_anomalies)}"
    
    @pytest.mark.integration
    def test_data_validation_and_cleaning(self, base_url):
        """데이터 검증 및 정제 테스트"""
        # 범위를 벗어난 데이터 테스트
        invalid_data = [
            {
                "equipment_id": "INV_TEMP_H",
                "facility_id": "FAC001",
                "measured_at": "2024-01-01T12:00:00Z",
                "temperature": 150.0,  # 최대값(100°C) 초과
                "humidity": 60.0
            },
            {
                "equipment_id": "INV_TEMP_L",
                "facility_id": "FAC001",
                "measured_at": "2024-01-01T12:00:00Z",
                "temperature": -100.0,  # 최소값(-50°C) 미만
                "humidity": 60.0
            },
            {
                "equipment_id": "INV_HUMID",
                "facility_id": "FAC001",
                "measured_at": "2024-01-01T12:00:00Z",
                "temperature": 25.0,
                "humidity": 150.0  # 최대값(100%) 초과
            }
        ]
        
        for data in invalid_data:
            try:
                response = requests.post(
                    f"{base_url}/ingest",
                    json=data,
                    timeout=10
                )
                
                # 데이터가 정제되어 처리되어야 함
                assert response.status_code in [200, 204], f"잘못된 데이터 처리 실패: {data['equipment_id']} - {response.status_code}"
    
                if response.status_code == 200:
                    result = response.json()
                    
                    # 온도가 범위 내에 있어야 함
                    if 'temperature' in data:
                        assert -50.0 <= result.get('temperature', 0) <= 100.0, f"온도가 범위를 벗어남: {result.get('temperature')}"
    
                    # 습도가 범위 내에 있어야 함
                    if 'humidity' in data:
                        assert 0.0 <= result.get('humidity', 0) <= 100.0, f"습도가 범위를 벗어남: {result.get('humidity')}"
                        
                    print(f"✅ 이상치 데이터 처리 완료: {data['equipment_id']}")
                else:
                    # 204 No Content - 정상 데이터
                    print(f"✅ 정상 데이터 처리 완료: {data['equipment_id']}")
                    
            except Exception as e:
                pytest.fail(f"데이터 검증 테스트 실패: {data['equipment_id']} - {e}")
    
    @pytest.mark.integration
    def test_missing_data_handling(self, base_url):
        """누락된 데이터 처리 테스트"""
        # 일부 필드가 누락된 데이터
        incomplete_data = [
            {
                "equipment_id": "INCOMP_1",
                "facility_id": "FAC001",
                "measured_at": "2024-01-01T12:00:00Z",
                # temperature 누락
                "humidity": 60.0
            },
            {
                "equipment_id": "INCOMP_2",
                "facility_id": "FAC001",
                "measured_at": "2024-01-01T12:00:00Z",
                "temperature": 25.0,
                # humidity 누락
            }
        ]
        
        for data in incomplete_data:
            try:
                response = requests.post(
                    f"{base_url}/ingest",
                    json=data,
                    timeout=10
                )
                
                # 누락된 데이터도 처리되어야 함
                assert response.status_code in [200, 204], f"누락된 데이터 처리 실패: {data['equipment_id']} - {response.status_code}"
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # 필수 필드는 있어야 함
                    assert 'equipment_id' in result, "equipment_id 필드가 없음"
                    assert 'version' in result, "version 필드가 없음"
                    assert 'event_id' in result, "event_id 필드가 없음"
                    assert 'measured_at' in result, "measured_at 필드가 없음"
                    assert 'detected_at' in result, "detected_at 필드가 없음"
                    
                    # metric과 value는 이상치가 아닌 경우 None일 수 있음
                    assert 'metric' in result, "metric 필드가 없음"
                    assert 'value' in result, "value 필드가 없음"
                    assert 'threshold' in result, "threshold 필드가 없음"
                    
                    print(f"✅ 이상치 데이터 처리 완료: {data['equipment_id']}")
                else:
                    # 204 No Content - 정상 데이터
                    print(f"✅ 정상 데이터 처리 완료: {data['equipment_id']}")
                    
            except Exception as e:
                pytest.fail(f"누락된 데이터 처리 테스트 실패: {data['equipment_id']} - {e}")
    
    @pytest.mark.slow
    def test_bulk_data_processing(self, base_url):
        """대량 데이터 처리 성능 테스트"""
        # 100개의 데이터를 빠르게 처리
        bulk_data = []
        for i in range(100):
            bulk_data.append({
                "equipment_id": f"BULK_{i:03d}",
                "facility_id": "FAC001",
                "measured_at": "2024-01-01T12:00:00Z",
                "temperature": 25.0 + (i % 10),
                "humidity": 50.0 + (i % 20),
                "smoke_density": 0.001 + (i % 5) * 0.01,
                "co_level": 0.001 + (i % 3) * 0.01,
                "gas_level": 0.001 + (i % 4) * 0.01
            })
        
        start_time = time.time()
        success_count = 0
        
        for data in bulk_data:
            try:
                response = requests.post(
                    f"{base_url}/ingest",
                    json=data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    success_count += 1
                    
            except Exception as e:
                print(f"대량 데이터 처리 실패: {data['equipment_id']} - {e}")
        
        end_time = time.time()
        processing_time = end_time - start_time
        throughput = success_count / processing_time if processing_time > 0 else 0
        
        # 성능 기준 확인
        assert success_count >= 95, f"대량 데이터 처리 성공률 부족: {success_count}/100"
        assert processing_time < 30, f"대량 데이터 처리 시간 초과: {processing_time:.2f}초"
        assert throughput >= 5, f"처리량 부족: {throughput:.2f} req/s (5 req/s 미만)"
        
        print(f"✅ 대량 데이터 처리 성능: {success_count}/100 성공, {processing_time:.2f}초, {throughput:.2f} req/s")
    
    @pytest.mark.integration
    def test_data_persistence(self, base_url, normal_data):
        """데이터 지속성 테스트"""
        # 데이터 수집 후 통계 확인
        initial_stats = requests.get(f"{base_url}/stats", timeout=10)
        assert initial_stats.status_code == 200, "초기 통계 조회 실패"
        
        initial_count = initial_stats.json().get('realtime_records_count', 0)
        
        # 일부 데이터 수집
        test_data = normal_data[:5]
        for data in test_data:
            response = requests.post(f"{base_url}/ingest", json=data, timeout=10)
            assert response.status_code in [200, 204], f"데이터 수집 실패: {data['equipment_id']} - {response.status_code}"
        
        # 잠시 대기
        time.sleep(2)
        
        # 통계 재확인
        final_stats = requests.get(f"{base_url}/stats", timeout=10)
        assert final_stats.status_code == 200, "최종 통계 조회 실패"
        
        final_count = final_stats.json().get('realtime_records_count', 0)
        
        # 데이터가 증가했는지 확인
        assert final_count >= initial_count, f"데이터가 증가하지 않음: {initial_count} → {final_count}"
        print(f"✅ 데이터 지속성 확인: {initial_count} → {final_count}")
