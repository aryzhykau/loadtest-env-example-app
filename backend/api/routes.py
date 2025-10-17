"""
API routes for the LoadTest application.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from bson import ObjectId
from datetime import datetime
from typing import List
import redis

from database import get_db
from redis_client import get_redis
from models import (
    DataEntry, DataEntryCreate, DataEntryUpdate,
    TaskCreate, TaskResponse, TaskStatus,
    HealthCheck, Metrics
)

router = APIRouter(prefix="/api")


# Helper functions

def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def get_object_id(id_str: str) -> ObjectId:
    """Convert string ID to ObjectId."""
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )


# Health Check Endpoint

@router.get("/health", response_model=HealthCheck)
async def health_check(
    db: Database = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    Health check endpoint to verify all services are operational.
    """
    health = {
        "status": "healthy",
        "mongodb": "unknown",
        "redis": "unknown",
        "celery": "unknown"
    }
    
    # Check MongoDB
    try:
        db.command("ping")
        health["mongodb"] = "connected"
    except Exception as e:
        health["mongodb"] = f"error: {str(e)}"
        health["status"] = "unhealthy"
    
    # Check Redis
    try:
        redis_client.ping()
        health["redis"] = "connected"
    except Exception as e:
        health["redis"] = f"error: {str(e)}"
        health["status"] = "unhealthy"
    
    # Check Celery (via Redis)
    try:
        # Check if there are any workers
        from celery_app import celery_app
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        if active_workers:
            health["celery"] = f"connected ({len(active_workers)} workers)"
        else:
            health["celery"] = "no workers"
    except Exception as e:
        health["celery"] = f"error: {str(e)}"
    
    return health


# Metrics Endpoint

@router.get("/metrics", response_model=Metrics)
async def get_metrics(
    db: Database = Depends(get_db)
):
    """
    Get application metrics.
    """
    tasks_collection = db["tasks"]
    data_collection = db["data_entries"]
    
    total_tasks = tasks_collection.count_documents({})
    active_tasks = tasks_collection.count_documents({"status": "started"})
    completed_tasks = tasks_collection.count_documents({"status": "success"})
    failed_tasks = tasks_collection.count_documents({"status": "failure"})
    total_data_entries = data_collection.count_documents({})
    
    return {
        "total_tasks": total_tasks,
        "active_tasks": active_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "total_data_entries": total_data_entries
    }


# Task Endpoints

@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Database = Depends(get_db)
):
    """
    Create and queue an async task.
    """
    from celery_app import celery_app
    from tasks.celery_tasks import process_data, generate_report, simulate_load
    
    # Map task types to Celery tasks
    task_map = {
        "process_data": process_data,
        "generate_report": generate_report,
        "simulate_load": simulate_load
    }
    
    if task_data.task_type not in task_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown task type: {task_data.task_type}"
        )
    
    # Queue the task
    celery_task = task_map[task_data.task_type]
    result = celery_task.delay(**task_data.params)
    
    # Store task metadata in MongoDB
    task_doc = {
        "task_id": result.id,
        "task_type": task_data.task_type,
        "status": TaskStatus.PENDING,
        "params": task_data.params,
        "created_at": datetime.utcnow(),
        "result": None,
        "error": None
    }
    
    db["tasks"].insert_one(task_doc)
    
    return TaskResponse(
        task_id=result.id,
        status=TaskStatus.PENDING,
        task_type=task_data.task_type,
        created_at=task_doc["created_at"]
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    db: Database = Depends(get_db)
):
    """
    Get the status and result of a task.
    """
    from celery_app import celery_app
    from celery.result import AsyncResult
    
    # Get task result from Celery
    result = AsyncResult(task_id, app=celery_app)
    
    # Get task metadata from MongoDB
    task_doc = db["tasks"].find_one({"task_id": task_id})
    
    if not task_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update status from Celery
    task_status = TaskStatus(result.state.lower())
    
    response = TaskResponse(
        task_id=task_id,
        status=task_status,
        task_type=task_doc["task_type"],
        created_at=task_doc["created_at"]
    )
    
    if result.ready():
        if result.successful():
            response.result = result.result
        else:
            response.error = str(result.info)
    
    return response


# Data CRUD Endpoints

@router.get("/data", response_model=List[DataEntry])
async def list_data_entries(
    skip: int = 0,
    limit: int = 100,
    db: Database = Depends(get_db)
):
    """
    List all data entries with pagination.
    """
    collection = db["data_entries"]
    
    cursor = collection.find().skip(skip).limit(limit).sort("created_at", -1)
    entries = [serialize_doc(doc) for doc in cursor]
    
    return entries


@router.post("/data", response_model=DataEntry, status_code=status.HTTP_201_CREATED)
async def create_data_entry(
    entry: DataEntryCreate,
    db: Database = Depends(get_db)
):
    """
    Create a new data entry.
    """
    collection = db["data_entries"]
    
    now = datetime.utcnow()
    doc = {
        **entry.model_dump(),
        "created_at": now,
        "updated_at": now
    }
    
    result = collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    
    return doc


@router.get("/data/{entry_id}", response_model=DataEntry)
async def get_data_entry(
    entry_id: str,
    db: Database = Depends(get_db)
):
    """
    Get a specific data entry by ID.
    """
    collection = db["data_entries"]
    obj_id = get_object_id(entry_id)
    
    doc = collection.find_one({"_id": obj_id})
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data entry not found"
        )
    
    return serialize_doc(doc)


@router.put("/data/{entry_id}", response_model=DataEntry)
async def update_data_entry(
    entry_id: str,
    entry: DataEntryUpdate,
    db: Database = Depends(get_db)
):
    """
    Update a data entry.
    """
    collection = db["data_entries"]
    obj_id = get_object_id(entry_id)
    
    # Get existing document
    existing = collection.find_one({"_id": obj_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data entry not found"
        )
    
    # Update only provided fields
    update_data = entry.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
    
    # Return updated document
    updated_doc = collection.find_one({"_id": obj_id})
    return serialize_doc(updated_doc)


@router.delete("/data/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data_entry(
    entry_id: str,
    db: Database = Depends(get_db)
):
    """
    Delete a data entry.
    """
    collection = db["data_entries"]
    obj_id = get_object_id(entry_id)
    
    result = collection.delete_one({"_id": obj_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data entry not found"
        )
    
    return None
