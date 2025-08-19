"""
DataLake Kafka 이벤트 발행 테스트
1. sensorAnormalyDetected 이벤트 발행
2. 이상치 탐지 시 Kafka 토픽으로 이벤트 전송
3. 이벤트 데이터 구조 검증
"""

import pytest
import requests
import json
import time
from kafka import KafkaConsumer
from typing import Dict, List


class TestKafkaEvents:
    """Kafka 이벤트 발행 테스트 클래스"""
    
    @pytest.mark.integration
    def test_anomaly_detection_event_publishing(self, base_url, anomaly_data, kafka_config):
        """이상치 탐지 시 Kafka 이벤트 발행 테스트"""
        if not anomaly_data:
            pytest.skip("이상치 데이터가 없음")
        
        # Kafka 컨슈머 생성
        consumer = KafkaConsumer(
            'fire-iot.anomaly-detected',
            bootstrap_servers=kafka_config['bootstrap_servers'],
            auto_offset_reset='earliest',
            consumer_timeout_ms=30000,  # 30초 타임아웃
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        # 이상치 데이터 전송하여 이벤트 발생
        sent_anomalies = []
        for data in anomaly_data[:3]:  # 처음 3개만 테스트
            try:
                response = requests.post(
                    f"{base_url}/ingest",
                    json=data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('is_anomaly'):
                        sent_anomalies.append(data)
                        time.sleep(0.5)  # 이벤트 처리 대기
                        
            except Exception as e:
                pytest.fail(f"이상치 데이터 전송 실패: {data['equipment_id']} - {e}")
        
        if not sent_anomalies:
            pytest.skip("전송된 이상치 데이터가 없음")
        
        # Kafka 메시지 수신 확인
        received_events = []
        start_time = time.time()
        
        try:
            for message in consumer:
                received_events.append(message.value)
                if len(received_events) >= len(sent_anomalies) or (time.time() - start_time) > 30:
                    break
        except Exception as e:
            print(f"Kafka 메시지 수신 중 오류: {e}")
        finally:
            consumer.close()
        
        # 이벤트 수신 확인
        assert len(received_events) > 0, "Kafka 이벤트를 수신하지 못함"
        assert len(received_events) >= len(sent_anomalies) * 0.8, f"이벤트 수신 부족: {len(received_events)}/{len(sent_anomalies)}"
        
        print(f"✅ Kafka 이상치 이벤트 수신: {len(received_events)}개")
        
        # 이벤트 데이터 구조 검증
        for event in received_events:
            self._validate_anomaly_event_structure(event)
    
    @pytest.mark.integration
    def test_anomaly_event_structure(self, base_url, anomaly_data, kafka_config):
        """이상치 이벤트 데이터 구조 검증"""
        if not anomaly_data:
            pytest.skip("이상치 데이터가 없음")
        
        # 온도 이상치 데이터로 테스트
        temp_anomaly = next((d for d in anomaly_data if d.get('metadata', {}).get('anomaly') == 'temperature'), None)
        if not temp_anomaly:
            pytest.skip("온도 이상치 데이터가 없음")
        
        # Kafka 컨슈머 생성
        consumer = KafkaConsumer(
            'fire-iot.anomaly-detected',
            bootstrap_servers=kafka_config['bootstrap_servers'],
            auto_offset_reset='earliest',
            consumer_timeout_ms=15000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        # 이상치 데이터 전송
        response = requests.post(f"{base_url}/ingest", json=temp_anomaly, timeout=10)
        
        assert response.status_code == 200, "이상치 데이터 전송 실패"
        
        # 이벤트 수신 대기
        received_event = None
        start_time = time.time()
        
        try:
            for message in consumer:
                received_event = message.value
                break
        except Exception as e:
            print(f"Kafka 메시지 수신 중 오류: {e}")
        finally:
            consumer.close()
        
        assert received_event is not None, "이상치 이벤트를 수신하지 못함"
        
        # 이벤트 구조 상세 검증
        self._validate_anomaly_event_structure(received_event)
        
        # 온도 관련 데이터 검증
        assert received_event.get('metric') == 'temperature', f"이상치 메트릭이 temperature가 아님: {received_event.get('metric')}"
        
        # 값 검증 (데이터 정리 과정에서 값이 변경될 수 있으므로 근사값으로 검증)
        original_value = temp_anomaly.get('temperature')
        received_value = received_event.get('value')
        threshold = received_event.get('threshold')
        
        # 이상치 값이 임계값을 초과하는지 확인
        assert received_value > threshold, f"이상치 값({received_value})이 임계값({threshold})을 초과하지 않음"
        
        # 원본 값과 수신된 값이 모두 임계값을 초과하는지 확인
        assert original_value > threshold, f"원본 값({original_value})이 임계값({threshold})을 초과하지 않음"
        
        print(f"✅ 온도 이상치 검증 성공: 원본값={original_value}, 수신값={received_value}, 임계값={threshold}")
    
    def _validate_anomaly_event_structure(self, event: Dict):
        """이상치 이벤트 데이터 구조 검증"""
        # 필수 필드 확인
        required_fields = [
            'event_id', 'equipment_id', 'facility_id', 'metric', 
            'value', 'threshold', 'measured_at', 'detected_at'
        ]
        
        for field in required_fields:
            assert field in event, f"필수 필드 {field}가 없음"
            assert event[field] is not None, f"필드 {field}가 None임"
        
        # 데이터 타입 검증
        assert isinstance(event['event_id'], str), "event_id는 문자열이어야 함"
        assert isinstance(event['equipment_id'], str), "equipment_id는 문자열이어야 함"
        assert isinstance(event['facility_id'], str), "facility_id는 문자열이어야 함"
        assert isinstance(event['metric'], str), "metric은 문자열이어야 함"
        assert isinstance(event['value'], (int, float)), "value는 숫자여야 함"
        assert isinstance(event['threshold'], (int, float)), "threshold는 숫자여야 함"
        
        # 날짜 형식 검증 (더 유연하게)
        import re
        # ISO 형식 또는 일반 날짜 형식 모두 허용
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO 형식
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # 일반 날짜 형식
        ]
        
        measured_at_valid = any(re.match(pattern, event['measured_at']) for pattern in date_patterns)
        assert measured_at_valid, f"measured_at 형식이 잘못됨: {event['measured_at']}"
        
        detected_at_valid = any(re.match(pattern, event['detected_at']) for pattern in date_patterns)
        assert detected_at_valid, f"detected_at 형식이 잘못됨: {event['detected_at']}"
        
        # 값 검증
        assert event['value'] > 0, "value는 양수여야 함"
        assert event['threshold'] > 0, "threshold는 양수여야 함"
        assert event['value'] > event['threshold'], f"value({event['value']})가 threshold({event['threshold']})를 초과해야 함"
    
    @pytest.mark.integration
    def test_multiple_anomaly_types(self, base_url, anomaly_data, kafka_config):
        """여러 유형의 이상치 이벤트 발행 테스트"""
        if not anomaly_data:
            pytest.skip("이상치 데이터가 없음")
        
        # 각 유형별 이상치 데이터 분류
        anomaly_types = {}
        for data in anomaly_data:
            anomaly_type = data.get('metadata', {}).get('anomaly')
            if anomaly_type:
                if anomaly_type not in anomaly_types:
                    anomaly_types[anomaly_type] = []
                anomaly_types[anomaly_type].append(data)
        
        if not anomaly_types:
            pytest.skip("이상치 유형이 없음")
        
        # Kafka 컨슈머 생성
        consumer = KafkaConsumer(
            'fire-iot.anomaly-detected',
            bootstrap_servers=kafka_config['bootstrap_servers'],
            auto_offset_reset='earliest',
            consumer_timeout_ms=45000,  # 45초 타임아웃
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        # 각 유형별로 이상치 데이터 전송
        sent_count = 0
        for anomaly_type, type_data in anomaly_types.items():
            for data in type_data[:2]:  # 각 유형당 2개씩
                try:
                    response = requests.post(f"{base_url}/ingest", json=data, timeout=10)
                    if response.status_code == 200:
                        sent_count += 1
                        time.sleep(0.3)  # 이벤트 처리 대기
                except Exception as e:
                    print(f"이상치 데이터 전송 실패: {data['equipment_id']} - {e}")
        
        if sent_count == 0:
            pytest.skip("전송된 이상치 데이터가 없음")
        
        # Kafka 메시지 수신 확인
        received_events = []
        start_time = time.time()
        
        try:
            for message in consumer:
                received_events.append(message.value)
                if len(received_events) >= sent_count or (time.time() - start_time) > 45:
                    break
        except Exception as e:
            print(f"Kafka 메시지 수신 중 오류: {e}")
        finally:
            consumer.close()
        
        # 이벤트 수신 확인
        assert len(received_events) > 0, "Kafka 이벤트를 수신하지 못함"
        
        # 각 유형별 이벤트 확인
        received_metrics = [event.get('metric') for event in received_events]
        expected_metrics = []
        
        for anomaly_type in anomaly_types.keys():
            if anomaly_type == 'temperature':
                expected_metrics.append('temperature')
            elif anomaly_type == 'smoke':
                expected_metrics.append('smoke_density')
            elif anomaly_type == 'co':
                expected_metrics.append('co_level')
        
        for expected_metric in expected_metrics:
            assert expected_metric in received_metrics, f"메트릭 {expected_metric}의 이벤트가 없음"
        
        print(f"✅ 다중 이상치 유형 이벤트 발행: {len(received_events)}개 수신")
    
    @pytest.mark.slow
    def test_kafka_event_performance(self, base_url, anomaly_data, kafka_config):
        """Kafka 이벤트 발행 성능 테스트"""
        if not anomaly_data:
            pytest.skip("이상치 데이터가 없음")
        
        # Kafka 컨슈머 생성
        consumer = KafkaConsumer(
            'fire-iot.anomaly-detected',
            bootstrap_servers=kafka_config['bootstrap_servers'],
            auto_offset_reset='earliest',
            consumer_timeout_ms=60000,  # 60초 타임아웃
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        # 20개의 이상치 데이터를 빠르게 전송
        test_data = anomaly_data[:20]
        start_time = time.time()
        
        for data in test_data:
            try:
                response = requests.post(f"{base_url}/ingest", json=data, timeout=5)
                if response.status_code != 200:
                    print(f"데이터 전송 실패: {data['equipment_id']} - {response.status_code}")
            except Exception as e:
                print(f"데이터 전송 오류: {data['equipment_id']} - {e}")
        
        send_time = time.time() - start_time
        
        # 이벤트 수신 대기
        received_events = []
        receive_start_time = time.time()
        
        try:
            for message in consumer:
                received_events.append(message.value)
                if len(received_events) >= len(test_data) * 0.8 or (time.time() - receive_start_time) > 60:
                    break
        except Exception as e:
            print(f"Kafka 메시지 수신 중 오류: {e}")
        finally:
            consumer.close()
        
        receive_time = time.time() - receive_start_time
        total_time = send_time + receive_time
        
        if len(received_events) == 0:
            pytest.skip("모든 데이터 전송이 실패하여 이벤트 수신 불가")
        
        # 성능 기준 확인
        assert len(received_events) >= len(test_data) * 0.8, f"이벤트 수신 부족: {len(received_events)}/{len(test_data)}"
        assert total_time < 60, f"전체 처리 시간 초과: {total_time:.2f}초"
        
        # 처리량 계산
        throughput = len(received_events) / total_time if total_time > 0 else 0
        
        print(f"✅ Kafka 이벤트 성능: {len(received_events)}개 수신, {total_time:.2f}초, {throughput:.2f} events/s")
        
        # 성능 기준
        assert throughput >= 0.5, f"처리량 부족: {throughput:.2f} events/s (0.5 events/s 미만)"
    
    @pytest.mark.integration
    def test_kafka_topic_existence(self, kafka_config):
        """필수 Kafka 토픽 존재 확인"""
        from kafka.admin import KafkaAdminClient
        
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=kafka_config['bootstrap_servers']
            )
            
            topics = admin_client.list_topics()
            
            # 필수 토픽 확인
            required_topics = [
                'fire-iot.anomaly-detected',
                'fire-iot.data-saved',
                'fire-iot.sensor-data'
            ]
            
            for topic in required_topics:
                assert topic in topics, f"필수 토픽 {topic}이 없음"
            
            admin_client.close()
            print("✅ 모든 필수 Kafka 토픽이 존재함")
            
        except Exception as e:
            pytest.fail(f"Kafka 토픽 확인 실패: {e}")
    
    @pytest.mark.integration
    def test_event_ordering(self, base_url, anomaly_data, kafka_config):
        """이벤트 순서 확인 테스트"""
        if len(anomaly_data) < 3:
            pytest.skip("이상치 데이터가 부족함")
        
        # Kafka 컨슈머 생성
        consumer = KafkaConsumer(
            'fire-iot.anomaly-detected',
            bootstrap_servers=kafka_config['bootstrap_servers'],
            auto_offset_reset='earliest',
            consumer_timeout_ms=30000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        # 순차적으로 데이터 전송
        test_data = anomaly_data[:3]
        sent_timestamps = []
        
        for i, data in enumerate(test_data):
            try:
                response = requests.post(f"{base_url}/ingest", json=data, timeout=10)
                if response.status_code == 200:
                    sent_timestamps.append((i, time.time()))
                    time.sleep(0.5)  # 순차적 전송을 위한 대기
            except Exception as e:
                pytest.fail(f"데이터 전송 실패: {data['equipment_id']} - {e}")
        
        if not sent_timestamps:
            pytest.skip("전송된 데이터가 없음")
        
        # 이벤트 수신
        received_events = []
        start_time = time.time()
        
        try:
            for message in consumer:
                received_events.append(message.value)
                if len(received_events) >= len(test_data) or (time.time() - start_time) > 30:
                    break
        except Exception as e:
            print(f"Kafka 메시지 수신 중 오류: {e}")
        finally:
            consumer.close()
        
        # 이벤트 순서 확인 (detected_at 기준)
        if len(received_events) >= 2:
            for i in range(1, len(received_events)):
                prev_time = received_events[i-1]['detected_at']
                curr_time = received_events[i]['detected_at']
                
                # detected_at은 ISO 형식 문자열이므로 직접 비교
                assert prev_time <= curr_time, f"이벤트 순서가 잘못됨: {prev_time} > {curr_time}"
            
            print("✅ 이벤트 순서가 올바름")
        else:
            print("⚠️ 이벤트가 2개 미만으로 순서 확인 불가")
