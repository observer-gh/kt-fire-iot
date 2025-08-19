import pytest
import redis
from unittest.mock import patch, MagicMock
from app.redis_client import RedisClient
from app.config import settings


class TestRedisClient:
    """Test Redis client functionality"""
    
    def test_redis_client_initialization(self):
        """Test Redis client initialization"""
        client = RedisClient()
        assert client is not None
    
    @patch('redis.Redis')
    def test_redis_connection_success(self, mock_redis):
        """Test successful Redis connection"""
        mock_instance = MagicMock()
        mock_instance.ping.return_value = True
        mock_redis.return_value = mock_instance
        
        client = RedisClient()
        assert client.is_connected() is True
    
    @patch('redis.Redis')
    def test_redis_connection_failure(self, mock_redis):
        """Test failed Redis connection"""
        mock_instance = MagicMock()
        mock_instance.ping.side_effect = Exception("Connection failed")
        mock_redis.return_value = mock_instance
        
        client = RedisClient()
        assert client.is_connected() is False
    
    @patch('redis.Redis')
    def test_redis_get_set_operations(self, mock_redis):
        """Test Redis GET and SET operations"""
        mock_instance = MagicMock()
        mock_instance.ping.return_value = True
        mock_instance.get.return_value = "test_value"
        mock_instance.set.return_value = True
        mock_redis.return_value = mock_instance
        
        client = RedisClient()
        
        # Test set operation
        result = client.set("test_key", "test_value")
        assert result is True
        
        # Test get operation
        value = client.get("test_key")
        assert value == "test_value"
    
    @patch('redis.Redis')
    def test_redis_delete_operation(self, mock_redis):
        """Test Redis DELETE operation"""
        mock_instance = MagicMock()
        mock_instance.ping.return_value = True
        mock_instance.delete.return_value = 1
        mock_redis.return_value = mock_instance
        
        client = RedisClient()
        
        result = client.delete("test_key")
        assert result is True
    
    @patch('redis.Redis')
    def test_redis_exists_operation(self, mock_redis):
        """Test Redis EXISTS operation"""
        mock_instance = MagicMock()
        mock_instance.ping.return_value = True
        mock_instance.exists.return_value = 1
        mock_redis.return_value = mock_instance
        
        client = RedisClient()
        
        result = client.exists("test_key")
        assert result is True
    
    def test_redis_url_parsing(self):
        """Test Redis URL parsing from settings"""
        # Test default Redis URL
        assert hasattr(settings, 'redis_url')
        assert settings.redis_url is not None
    
    @patch('redis.Redis')
    def test_redis_operations_when_disconnected(self, mock_redis):
        """Test Redis operations when disconnected"""
        mock_instance = MagicMock()
        mock_instance.ping.side_effect = Exception("Connection failed")
        mock_redis.return_value = mock_instance
        
        client = RedisClient()
        
        # All operations should return None/False when disconnected
        assert client.get("test_key") is None
        assert client.set("test_key", "value") is False
        assert client.delete("test_key") is False
        assert client.exists("test_key") is False
    
    @patch('redis.Redis')
    def test_redis_close(self, mock_redis):
        """Test Redis connection close"""
        mock_instance = MagicMock()
        mock_instance.ping.return_value = True
        mock_redis.return_value = mock_instance
        
        client = RedisClient()
        assert client.is_connected() is True
        
        client.close()
        assert client.is_connected() is False


class TestRedisIntegration:
    """Test Redis integration with the application"""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client for testing"""
        with patch('app.redis_client.redis_client') as mock_client:
            mock_client.is_connected.return_value = True
            mock_client.get.return_value = None
            mock_client.set.return_value = True
            yield mock_client
    
    def test_health_check_with_redis(self, client, mock_redis_client):
        """Test health check endpoint includes Redis status"""
        response = client.get("/healthz")
        assert response.status_code == 200
        
        data = response.json()
        assert "redis" in data
        assert data["redis"] in ["healthy", "unhealthy"]
    
    def test_redis_status_endpoint(self, client, mock_redis_client):
        """Test Redis status endpoint"""
        response = client.get("/redis/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "connected" in data
        assert "url" in data
    
    def test_stats_with_redis_caching(self, client, mock_redis_client):
        """Test stats endpoint with Redis caching"""
        # First call - should not be cached
        mock_redis_client.get.return_value = None
        response1 = client.get("/stats")
        assert response1.status_code == 200
        
        # Second call - should return cached data
        cached_data = {"cached": True, "test": "data"}
        mock_redis_client.get.return_value = cached_data
        response2 = client.get("/stats")
        assert response2.status_code == 200
        
        # Verify cache was set
        mock_redis_client.set.assert_called()
    
    def test_cache_clear_endpoint(self, client, mock_redis_client):
        """Test cache clear endpoint"""
        mock_redis_client.delete.return_value = True
        
        response = client.delete("/cache")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "cleared" in data["message"]
    
    def test_cache_clear_when_redis_disconnected(self, client, mock_redis_client):
        """Test cache clear when Redis is disconnected"""
        mock_redis_client.is_connected.return_value = False
        
        response = client.delete("/cache")
        assert response.status_code == 503
        
        data = response.json()
        assert "Redis is not connected" in data["detail"]


@pytest.fixture
def client():
    """Test client fixture"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
