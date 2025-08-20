"""
Test configuration for separated DataLake API and Dashboard services
"""

import os
from typing import Dict, Any

# Test configuration for separated services
TEST_CONFIG = {
    # API Service Configuration
    'api': {
        'url': os.getenv('TEST_API_URL', 'http://localhost:8084'),
        'host': os.getenv('TEST_API_HOST', 'localhost'),
        'port': os.getenv('TEST_API_PORT', '8084'),
        'health_endpoint': '/healthz',
        'stats_endpoint': '/stats'
    },
    
    # Dashboard Service Configuration
    'dashboard': {
        'url': os.getenv('TEST_DASHBOARD_URL', 'http://localhost:8501'),
        'host': os.getenv('TEST_DASHBOARD_HOST', 'localhost'),
        'port': os.getenv('TEST_DASHBOARD_PORT', '8501'),
        'health_endpoint': '/_stcore/health'
    },
    
    # Database Configuration
    'database': {
        'host': os.getenv('TEST_DB_HOST', 'localhost'),
        'port': int(os.getenv('TEST_DB_PORT', '5433')),
        'database': os.getenv('TEST_DB_NAME', 'datalake'),
        'user': os.getenv('TEST_DB_USER', 'postgres'),
        'password': os.getenv('TEST_DB_PASSWORD', 'postgres')
    },
    
    # Redis Configuration
    'redis': {
        'host': os.getenv('TEST_REDIS_HOST', 'localhost'),
        'port': int(os.getenv('TEST_REDIS_PORT', '6379'))
    },
    
    # Kafka Configuration
    'kafka': {
        'bootstrap_servers': os.getenv('TEST_KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    }
}

def get_api_url() -> str:
    """Get API service URL for testing"""
    return TEST_CONFIG['api']['url']

def get_dashboard_url() -> str:
    """Get dashboard service URL for testing"""
    return TEST_CONFIG['dashboard']['url']

def get_db_config() -> Dict[str, Any]:
    """Get database configuration for testing"""
    return TEST_CONFIG['database']

def get_redis_config() -> Dict[str, Any]:
    """Get Redis configuration for testing"""
    return TEST_CONFIG['redis']

def get_kafka_config() -> Dict[str, Any]:
    """Get Kafka configuration for testing"""
    return TEST_CONFIG['kafka']

def is_api_available() -> bool:
    """Check if API service is available for testing"""
    try:
        import requests
        response = requests.get(f"{get_api_url()}/healthz", timeout=5)
        return response.status_code == 200
    except:
        return False

def is_dashboard_available() -> bool:
    """Check if dashboard service is available for testing"""
    try:
        import requests
        response = requests.get(f"{get_dashboard_url()}/_stcore/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def is_database_available() -> bool:
    """Check if database is available for testing"""
    try:
        import psycopg2
        db_config = get_db_config()
        conn = psycopg2.connect(**db_config)
        conn.close()
        return True
    except:
        return False
