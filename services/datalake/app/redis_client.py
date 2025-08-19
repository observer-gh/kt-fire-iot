import redis
import logging
from typing import Optional, Any
from .config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis client wrapper for caching and session management"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self):
        """Establish Redis connection"""
        try:
            # Parse Redis URL
            if settings.redis_url.startswith('redis://'):
                # Remove 'redis://' prefix and parse
                url_parts = settings.redis_url[8:].split('@')
                if len(url_parts) == 2:
                    # Format: redis://password@host:port
                    password, host_port = url_parts
                    if ':' in host_port:
                        host, port = host_port.split(':')
                        self.client = redis.Redis(
                            host=host,
                            port=int(port),
                            password=password if password else None,
                            decode_responses=True,
                            socket_connect_timeout=5,
                            socket_timeout=5
                        )
                    else:
                        self.client = redis.Redis(
                            host=host_port,
                            password=password if password else None,
                            decode_responses=True,
                            socket_connect_timeout=5,
                            socket_timeout=5
                        )
                else:
                    # Format: redis://host:port
                    host_port = url_parts[0]
                    if ':' in host_port:
                        host, port = host_port.split(':')
                        self.client = redis.Redis(
                            host=host,
                            port=int(port),
                            decode_responses=True,
                            socket_connect_timeout=5,
                            socket_timeout=5
                        )
                    else:
                        self.client = redis.Redis(
                            host=host_port,
                            decode_responses=True,
                            socket_connect_timeout=5,
                            socket_timeout=5
                        )
            else:
                # Fallback to default localhost
                self.client = redis.Redis(
                    host='localhost',
                    port=6379,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            
            # Test connection
            self.client.ping()
            logger.info(f"Redis connected successfully to {settings.redis_url}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        if not self.is_connected():
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration"""
        if not self.is_connected():
            return False
        try:
            return self.client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.is_connected():
            return False
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        if not self.is_connected():
            return False
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False
    
    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
            self.client = None

# Global Redis client instance
redis_client = RedisClient()
