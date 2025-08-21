"""
pytest 설정 및 공통 fixture 정의
DataLake 서비스 테스트를 위한 공통 설정
"""

import pytest
import asyncio
import requests
import time
import os
from typing import Dict, List, Generator
import json
import random
from datetime import datetime, timedelta

# 테스트 실행 전 환경변수 설정
def setup_test_environment():
    """테스트 환경 설정 - 호스트 포트로 통일"""
    # PostgreSQL 설정 (호스트 포트 5433)
    os.environ["POSTGRES_URL"] = "postgresql://postgres:postgres@localhost:5433/datalake"
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_PORT"] = "5433"
    os.environ["POSTGRES_DB"] = "datalake"
    os.environ["POSTGRES_USER"] = "postgres"
    os.environ["POSTGRES_PASSWORD"] = "postgres"
    
    # Redis 설정 (호스트 포트 6379)
    os.environ["REDIS_URL"] = "redis://localhost:6379"
    
    # Kafka 설정 (호스트 포트 9092)
    os.environ["KAFKA_BROKERS"] = "localhost:9092"
    os.environ["KAFKA_TOPIC_ANOMALY"] = "datalake.sensorDataAnomalyDetected"
    os.environ["KAFKA_TOPIC_DATA_SAVED"] = "datalake.sensorDataSaved"
    
    # 기타 설정
    os.environ["STORAGE_TYPE"] = "mock"
    os.environ["LOG_LEVEL"] = "INFO"

# 테스트 환경 설정 실행
setup_test_environment()

def parse_api_response(response_text):
    """API 응답 파싱 - 이중 JSON 인코딩 처리"""
    try:
        # 먼저 JSON 파싱 시도
        parsed = json.loads(response_text)
        
        # 만약 파싱된 결과가 문자열이고 JSON 형태라면 다시 파싱
        if isinstance(parsed, str) and (parsed.startswith('{') or parsed.startswith('[')):
            try:
                return json.loads(parsed)
            except json.JSONDecodeError:
                pass
        
        return parsed
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 원본 반환
        return response_text

# 테스트 설정
TEST_CONFIG = {
    'api_url': 'http://localhost:8084',
    'dashboard_url': 'http://localhost:8501',
    'db_config': {
        'host': 'localhost',
        'port': 5433,
        'database': 'datalake',  # docker-compose에서 설정한 데이터베이스명
        'user': 'postgres',
        'password': 'postgres'
    },
    'redis_config': {
        'host': 'localhost',
        'port': 6379
    },
    'kafka_config': {
        'bootstrap_servers': 'localhost:9092',
        'topic_anomaly': 'datalake.sensorDataAnomalyDetected',
        'topic_data_saved': 'datalake.sensorDataSaved'
    }
}

@pytest.fixture(scope="session")
def test_config():
    """테스트 설정 반환"""
    return TEST_CONFIG

@pytest.fixture(scope="session")
def api_url():
    """DataLake API 기본 URL"""
    return TEST_CONFIG['api_url']

@pytest.fixture(scope="session")
def base_url():
    """DataLake API 기본 URL (하위 호환성)"""
    return TEST_CONFIG['api_url']

@pytest.fixture(scope="session")
def dashboard_url():
    """대시보드 기본 URL"""
    return TEST_CONFIG['dashboard_url']

@pytest.fixture(scope="session")
def db_config():
    """데이터베이스 설정"""
    return TEST_CONFIG['db_config']

@pytest.fixture(scope="session")
def redis_config():
    """Redis 설정"""
    return TEST_CONFIG['redis_config']

@pytest.fixture(scope="session")
def kafka_config():
    """Kafka 설정"""
    return TEST_CONFIG['kafka_config']

@pytest.fixture(scope="session")
def test_data() -> List[Dict]:
    """테스트용 센서 데이터 생성"""
    data = []
    
    # 정상 데이터
    for i in range(20):
        data.append({
            "equipment_id": f"EQ{i:03d}",
            "facility_id": f"FAC{(i % 5) + 1:03d}",
            "equipment_location": f"Building{(i % 3) + 1}_Floor{(i % 10) + 1}",
            "measured_at": (datetime.utcnow() - timedelta(minutes=i)).isoformat() + "Z",
            "temperature": random.uniform(20.0, 30.0),
            "humidity": random.uniform(40.0, 70.0),
            "smoke_density": random.uniform(0.001, 0.050),
            "co_level": random.uniform(0.001, 0.020),
            "gas_level": random.uniform(0.001, 0.030),
            "metadata": {"test": True, "batch": i}
        })
    
    # 이상치 데이터 (온도)
    for i in range(5):
        data.append({
            "equipment_id": f"ANOM_T{i:02d}",
            "facility_id": f"FAC{(i % 3) + 1:03d}",
            "equipment_location": f"Building{(i % 2) + 1}_Floor{(i % 5) + 1}",
            "measured_at": (datetime.utcnow() - timedelta(minutes=i)).isoformat() + "Z",
            "temperature": random.uniform(85.0, 95.0),  # 임계값 초과
            "humidity": random.uniform(40.0, 70.0),
            "smoke_density": random.uniform(0.001, 0.050),
            "co_level": random.uniform(0.001, 0.020),
            "gas_level": random.uniform(0.001, 0.030),
            "metadata": {"test": True, "anomaly": "temperature", "batch": i}
        })
    
    # 이상치 데이터 (연기)
    for i in range(5):
        data.append({
            "equipment_id": f"ANOM_S{i:02d}",
            "facility_id": f"FAC{(i % 3) + 1:03d}",
            "equipment_location": f"Building{(i % 2) + 1}_Floor{(i % 5) + 1}",
            "measured_at": (datetime.utcnow() - timedelta(minutes=i)).isoformat() + "Z",
            "temperature": random.uniform(20.0, 30.0),
            "humidity": random.uniform(40.0, 70.0),
            "smoke_density": random.uniform(600.0, 800.0),  # 임계값 초과
            "co_level": random.uniform(0.001, 0.020),
            "gas_level": random.uniform(0.001, 0.030),
            "metadata": {"test": True, "anomaly": "smoke", "batch": i}
        })
    
    # 이상치 데이터 (CO)
    for i in range(5):
        data.append({
            "equipment_id": f"ANOM_C{i:02d}",
            "facility_id": f"FAC{(i % 3) + 1:03d}",
            "equipment_location": f"Building{(i % 2) + 1}_Floor{(i % 5) + 1}",
            "measured_at": (datetime.utcnow() - timedelta(minutes=i)).isoformat() + "Z",
            "temperature": random.uniform(20.0, 30.0),
            "humidity": random.uniform(40.0, 70.0),
            "smoke_density": random.uniform(0.001, 0.050),
            "co_level": random.uniform(250.0, 300.0),  # 임계값 초과
            "gas_level": random.uniform(0.001, 0.030),
            "metadata": {"test": True, "anomaly": "co", "batch": i}
        })
    
    return data

@pytest.fixture(scope="session")
def anomaly_data(test_data) -> List[Dict]:
    """이상치 데이터만 필터링"""
    return [d for d in test_data if d.get('metadata', {}).get('anomaly')]

@pytest.fixture(scope="session")
def normal_data(test_data) -> List[Dict]:
    """정상 데이터만 필터링"""
    return [d for d in test_data if not d.get('metadata', {}).get('anomaly')]

@pytest.fixture(scope="function")
def cleanup_test_data(base_url):
    """테스트 후 데이터 정리"""
    yield
    # 테스트 완료 후 정리 작업
    try:
        requests.delete(f"{base_url}/storage/batches", timeout=5)
    except:
        pass

@pytest.fixture(scope="session")
def event_loop():
    """비동기 테스트를 위한 이벤트 루프"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

def pytest_configure(config):
    """pytest 설정"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

def pytest_collection_modifyitems(config, items):
    """테스트 아이템 수정"""
    for item in items:
        # 기본적으로 모든 테스트를 integration으로 마킹
        if not any(marker for marker in item.iter_markers()):
            item.add_marker(pytest.mark.integration)
