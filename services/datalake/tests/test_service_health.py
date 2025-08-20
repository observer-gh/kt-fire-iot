"""
DataLake 서비스 상태 및 DB 연결 테스트
1. 서비스 헬스체크
2. PostgreSQL 연결
3. Redis 연결
4. Kafka 연결
"""

import pytest
import requests
import psycopg2
import redis
from kafka import KafkaProducer
import time


class TestServiceHealth:
    """서비스 상태 및 DB 연결 테스트 클래스"""
    
    @pytest.mark.unit
    def test_datalake_api_health(self, base_url):
        """DataLake API 서비스 헬스체크"""
        response = requests.get(f"{base_url}/healthz", timeout=10)
        
        assert response.status_code == 200, f"서비스 헬스체크 실패: {response.status_code}"
        
        data = response.json()
        assert data["status"] == "healthy", f"서비스 상태가 healthy가 아님: {data['status']}"
        assert data["service"] == "datalake", f"서비스명이 datalake가 아님: {data['service']}"
    
    @pytest.mark.unit
    def test_datalake_root_endpoint(self, base_url):
        """DataLake 루트 엔드포인트 테스트"""
        response = requests.get(f"{base_url}/", timeout=10)
        
        assert response.status_code == 200, f"루트 엔드포인트 실패: {response.status_code}"
        
        data = response.json()
        assert "message" in data, "응답에 message 필드가 없음"
        assert "DataLake Service" in data["message"], f"잘못된 메시지: {data['message']}"
    
    @pytest.mark.integration
    def test_postgresql_connection(self, db_config):
        """PostgreSQL 데이터베이스 연결 테스트"""
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            
            # 버전 확인
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            assert version is not None, "PostgreSQL 버전 정보를 가져올 수 없음"
            assert "PostgreSQL" in version[0], f"PostgreSQL이 아님: {version[0]}"
            
            # 테이블 존재 확인
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            # 필수 테이블 확인
            table_names = [table[0] for table in tables]
            expected_tables = ['realtime', 'alert']
            
            for expected_table in expected_tables:
                assert expected_table in table_names, f"필수 테이블 {expected_table}이 없음"
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            pytest.fail(f"PostgreSQL 연결 실패: {e}")
    
    @pytest.mark.integration
    def test_redis_connection(self, redis_config):
        """Redis 연결 테스트"""
        try:
            r = redis.Redis(**redis_config)
            
            # PING 테스트
            response = r.ping()
            assert response is True, "Redis PING 실패"
            
            # 간단한 데이터 쓰기/읽기 테스트
            test_key = "datalake_test_key"
            test_value = "datalake_test_value"
            
            r.set(test_key, test_value)
            retrieved_value = r.get(test_key)
            
            assert retrieved_value.decode('utf-8') == test_value, "Redis 데이터 읽기/쓰기 실패"
            
            # 테스트 데이터 정리
            r.delete(test_key)
            
        except Exception as e:
            pytest.fail(f"Redis 연결 실패: {e}")
    
    @pytest.mark.integration
    def test_kafka_connection(self, kafka_config):
        """Kafka 브로커 연결 테스트"""
        try:
            producer = KafkaProducer(
                bootstrap_servers=kafka_config['bootstrap_servers'],
                request_timeout_ms=10000
            )
            
            # 연결 확인
            assert producer.bootstrap_connected(), "Kafka 브로커에 연결할 수 없음"
            
            # 토픽 목록 확인
            from kafka.admin import KafkaAdminClient, ConfigResource, ConfigResourceType
            
            admin_client = KafkaAdminClient(
                bootstrap_servers=kafka_config['bootstrap_servers']
            )
            
            topics = admin_client.list_topics()
            
            # 필수 토픽 확인
            expected_topics = ['fire-iot.anomaly-detected', 'fire-iot.sensorDataSaved']
            
            for expected_topic in expected_topics:
                assert expected_topic in topics, f"필수 토픽 {expected_topic}이 없음"
            
            producer.close()
            admin_client.close()
            
        except Exception as e:
            pytest.fail(f"Kafka 연결 실패: {e}")
    
    @pytest.mark.integration
    def test_all_services_healthy(self, base_url, db_config, redis_config, kafka_config):
        """모든 서비스가 정상적으로 작동하는지 통합 테스트"""
        # API 서비스 확인
        api_healthy = False
        try:
            response = requests.get(f"{base_url}/healthz", timeout=5)
            api_healthy = response.status_code == 200
        except:
            pass
        
        # DB 연결 확인
        db_healthy = False
        try:
            conn = psycopg2.connect(**db_config)
            conn.close()
            db_healthy = True
        except:
            pass
        
        # Redis 연결 확인
        redis_healthy = False
        try:
            r = redis.Redis(**redis_config)
            r.ping()
            redis_healthy = True
        except:
            pass
        
        # Kafka 연결 확인
        kafka_healthy = False
        try:
            producer = KafkaProducer(bootstrap_servers=kafka_config['bootstrap_servers'])
            producer.close()
            kafka_healthy = True
        except:
            pass
        
        # 모든 서비스가 정상이어야 함
        assert api_healthy, "DataLake API 서비스가 정상이 아님"
        assert db_healthy, "PostgreSQL 데이터베이스가 정상이 아님"
        assert redis_healthy, "Redis가 정상이 아님"
        assert kafka_healthy, "Kafka가 정상이 아님"
    
    @pytest.mark.slow
    def test_service_stability(self, base_url):
        """서비스 안정성 테스트 (연속 요청)"""
        # 10번 연속으로 헬스체크 요청
        for i in range(10):
            response = requests.get(f"{base_url}/healthz", timeout=5)
            assert response.status_code == 200, f"연속 요청 {i+1}번째 실패: {response.status_code}"
            time.sleep(0.1)  # 100ms 간격
    
    @pytest.mark.integration
    def test_service_response_time(self, base_url):
        """서비스 응답 시간 테스트"""
        start_time = time.time()
        response = requests.get(f"{base_url}/healthz", timeout=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200, "서비스 응답 실패"
        assert response_time < 1.0, f"응답 시간이 너무 김: {response_time:.3f}초 (1초 초과)"
        
        # 응답 시간이 100ms 이하인지 확인 (로컬 환경 기준)
        if response_time < 0.1:
            print(f"✅ 빠른 응답 시간: {response_time:.3f}초")
        elif response_time < 0.5:
            print(f"⚠️ 보통 응답 시간: {response_time:.3f}초")
        else:
            print(f"🐌 느린 응답 시간: {response_time:.3f}초")
