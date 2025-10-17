"""
LoadTest Demo Application - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from database import mongodb
from redis_client import redis_client
from api.routes import router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name} in {settings.app_env} mode")
    
    try:
        # Connect to MongoDB
        mongodb.connect()
        
        # Connect to Redis
        redis_client.connect()
        
        logger.info("All connections established successfully")
    except Exception as e:
        logger.error(f"Failed to establish connections: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    mongodb.disconnect()
    redis_client.disconnect()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Demo application for load testing with Kubernetes",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app_env == "development"
    )
