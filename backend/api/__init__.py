"""
API dependencies.
"""
from database import get_db
from redis_client import get_redis


__all__ = ["get_db", "get_redis"]
