"""
Configuration management for the LoadTest application.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "LoadTest Demo"
    app_env: str = "development"
    log_level: str = "info"
    
    # MongoDB
    mongodb_url: str = "mongodb://mongodb:27017"
    mongodb_database: str = "loadtest_db"
    
    # Redis
    redis_url: str = "redis://redis:6379/0"
    
    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"
    
    # Service Type (backend, worker, beat)
    service_type: str = "backend"
    
    # Worker Configuration
    worker_concurrency: int = 4
    worker_prefetch_multiplier: int = 4
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
