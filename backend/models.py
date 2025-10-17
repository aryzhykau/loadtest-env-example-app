"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"


class DataEntryStatus(str, Enum):
    """Data entry status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


# Data Entry Models

class DataEntryBase(BaseModel):
    """Base model for data entries."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    value: float
    status: DataEntryStatus = DataEntryStatus.ACTIVE


class DataEntryCreate(DataEntryBase):
    """Model for creating a data entry."""
    pass


class DataEntryUpdate(BaseModel):
    """Model for updating a data entry."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    value: Optional[float] = None
    status: Optional[DataEntryStatus] = None


class DataEntry(DataEntryBase):
    """Model for a complete data entry."""
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


# Task Models

class TaskCreate(BaseModel):
    """Model for creating a task."""
    task_type: str = Field(..., description="Type of task to execute")
    params: Optional[dict[str, Any]] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Model for task response."""
    task_id: str
    status: TaskStatus
    task_type: str
    created_at: datetime
    result: Optional[Any] = None
    error: Optional[str] = None


# Health Check Models

class HealthCheck(BaseModel):
    """Model for health check response."""
    status: str
    mongodb: str
    redis: str
    celery: str


# Metrics Models

class Metrics(BaseModel):
    """Model for application metrics."""
    total_tasks: int
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_data_entries: int
