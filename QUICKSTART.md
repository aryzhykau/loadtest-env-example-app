# LoadTest Demo Application - Quick Start Guide

## Overview

The LoadTest demo application is now complete! Here's what we've built:

### Components
✅ **FastAPI Backend** - REST API with health checks, metrics, and CRUD operations  
✅ **React Frontend** - Modern UI with Dashboard, Data Manager, and Task Runner  
✅ **Celery Workers (x2)** - Background task processing  
✅ **MongoDB** - Data persistence  
✅ **Redis** - Message broker and caching  
✅ **Unified Docker Image** - Single image for backend and workers  
✅ **Docker Compose** - Complete local development environment

## Quick Start

### 1. Start the Application

```bash
cd /Users/andrejryzikov/loadtest-env-example/app
docker-compose up --build
```

This will:
- Build the backend/worker image
- Build the frontend image
- Start all 6 services (mongodb, redis, backend, 2 workers, frontend)
- Set up networking and health checks

### 2. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Interactive Swagger UI)
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

### 3. Test the Application

#### Via Frontend (http://localhost:3000)

1. **Dashboard Tab**:
   - View system health (MongoDB, Redis, Celery)
   - Monitor metrics (tasks, data entries)

2. **Data Manager Tab**:
   - Create new data entries
   - Edit existing entries
   - Delete entries
   - View all data in a table

3. **Task Runner Tab**:
   - Select task type (Process Data, Generate Report, Simulate Load)
   - Configure parameters
   - Run task and monitor progress
   - View results in real-time

#### Via API

```bash
# Health check
curl http://localhost:8000/api/health

# Create data entry
curl -X POST http://localhost:8000/api/data \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Entry",
    "description": "My first entry",
    "value": 123.45,
    "status": "active"
  }'

# List data entries
curl http://localhost:8000/api/data

# Run a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "simulate_load",
    "params": {
      "duration": 10,
      "intensity": "medium"
    }
  }'

# Check task status (replace TASK_ID)
curl http://localhost:8000/api/tasks/TASK_ID
```

## File Structure

```
app/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── celery_app.py        # Celery configuration  
│   ├── config.py            # Settings management
│   ├── models.py            # Pydantic models
│   ├── database.py          # MongoDB client
│   ├── redis_client.py      # Redis client
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── celery_tasks.py  # Background tasks
│   ├── Dockerfile           # Unified container
│   ├── entrypoint.sh        # Service selector
│   └── requirements.txt     # Python deps
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx         # Entry point
│   │   ├── App.tsx          # Main component
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── DataManager.tsx
│   │   │   └── TaskRunner.tsx
│   │   ├── services/
│   │   │   └── api.ts       # API client
│   │   └── types/
│   │       └── api.ts       # TypeScript types
│   ├── Dockerfile           # Multi-stage build
│   ├── nginx.conf           # Nginx config
│   ├── package.json         # Node deps
│   └── vite.config.ts       # Vite config
│
├── docker-compose.yml       # Local development
└── README.md                # Documentation
```

## How It Works

### Unified Image Strategy

The backend and workers use the **same Docker image** but run different services based on the `SERVICE_TYPE` environment variable:

```yaml
# Backend service
environment:
  - SERVICE_TYPE=backend

# Worker service  
environment:
  - SERVICE_TYPE=worker
  - WORKER_CONCURRENCY=4
```

The `entrypoint.sh` script checks `SERVICE_TYPE` and starts:
- `backend` → `uvicorn main:app --host 0.0.0.0 --port 8000`
- `worker` → `celery -A celery_app worker --loglevel=info`
- `beat` → `celery -A celery_app beat --loglevel=info`

**Benefits**:
- Single build pipeline
- Consistent dependencies
- Guaranteed code consistency
- Simplified version management

### Request Flow

1. User interacts with React frontend (http://localhost:3000)
2. Frontend sends API request to FastAPI backend (http://localhost:8000)
3. Backend processes request:
   - **Sync**: Query MongoDB, return response
   - **Async**: Queue task in Redis, return task ID
4. Celery workers pull tasks from Redis
5. Workers process tasks and store results
6. Frontend polls for task status

## Available Tasks

### 1. Process Data
Simulates data processing with progress tracking.

**Parameters**:
- `data_id` (string): ID to process
- `processing_time` (int): Duration in seconds

### 2. Generate Report
Generates different types of reports.

**Parameters**:
- `report_type` (string): summary, detailed, or analytics

### 3. Simulate Load
Simulates system load for testing.

**Parameters**:
- `duration` (int): Duration in seconds
- `intensity` (string): low, medium, or high

## Troubleshooting

### Services won't start
```bash
# Check service logs
docker-compose logs backend
docker-compose logs worker1
docker-compose logs frontend

# Restart specific service
docker-compose restart backend
```

### Frontend can't connect to backend
- Ensure backend is running: `docker-compose ps`
- Check backend health: `curl http://localhost:8000/api/health`
- Verify VITE_API_URL in frontend service

### Tasks not processing
- Check if workers are running: `docker-compose ps worker1 worker2`
- View worker logs: `docker-compose logs worker1`
- Verify Redis connection: `docker-compose logs redis`

### Database connection issues
- Check MongoDB health: `docker-compose ps mongodb`
- View MongoDB logs: `docker-compose logs mongodb`

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes all data)
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

## Next Steps

Now that the application is running locally, proceed to:

1. ✅ **Test Application** - Verify all features work
2. 📦 **Create Helm Chart** - Package for Kubernetes
3. 🚀 **Deploy to K8s** - Deploy using Helm
4. 🔄 **Setup ArgoCD** - Configure GitOps workflow
5. 📊 **Add Monitoring** - Integrate with Prometheus/Grafana

## Development Workflow

### Making Backend Changes

1. Edit backend files
2. Rebuild backend service: `docker-compose up -d --build backend worker1 worker2`
3. View logs: `docker-compose logs -f backend`

### Making Frontend Changes

1. Edit frontend files
2. Rebuild frontend service: `docker-compose up -d --build frontend`
3. View logs: `docker-compose logs -f frontend`

### Adding New Tasks

1. Add task function to `backend/tasks/celery_tasks.py`
2. Import in `backend/api/routes.py`
3. Add to task_map in create_task endpoint
4. Rebuild: `docker-compose up -d --build backend worker1 worker2`

## Support

For issues or questions:
- Check logs: `docker-compose logs <service_name>`
- View running services: `docker-compose ps`
- Inspect service: `docker-compose exec <service_name> sh`
