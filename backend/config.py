"""
Configuration management for the LoadTest application.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "LoadTest Demo"
    app_env: str = "development"
    log_level: str = "info"
    
    # MongoDB
    mongodb_url: str = "mongodb://mongodb:27017"
    mongodb_database: str = "loadtest_db"
    mongodb_username: Optional[str] = None
    mongodb_password: Optional[str] = None
    
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
    
    @property
    def mongodb_connection_url(self) -> str:
        """Construct MongoDB connection URL with authentication if credentials are provided."""
        if self.mongodb_username and self.mongodb_password:
            # Parse the base URL to inject credentials
            base_url = self.mongodb_url.replace("mongodb://", "")
            return f"mongodb://{self.mongodb_username}:{self.mongodb_password}@{base_url}"
        return self.mongodb_url
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
