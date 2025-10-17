"""
Redis client connection and utilities.
"""
import redis
from config import settings
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis connection manager."""
    
    def __init__(self):
        self.client: redis.Redis = None
    
    def connect(self):
        """Connect to Redis."""
        try:
            self.client = redis.from_url(
                settings.redis_url,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis: {settings.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from Redis")
    
    def get_client(self) -> redis.Redis:
        """Get Redis client instance."""
        if not self.client:
            raise RuntimeError("Redis not connected")
        return self.client


# Global Redis instance
redis_client = RedisClient()


def get_redis() -> redis.Redis:
    """Dependency for getting Redis client."""
    return redis_client.get_client()
