# LoadTest Demo Application

A demo application for load testing with Kubernetes, featuring a FastAPI backend, React frontend, and Celery workers.

## Architecture

- **Backend**: FastAPI application providing REST API
- **Frontend**: React + TypeScript with Material-UI
- **Workers**: 2 Celery workers for background processing
- **Database**: MongoDB for data storage
- **Cache/Broker**: Redis for Celery message queue and caching

## Project Structure

```
app/
├── backend/               # FastAPI backend and Celery workers
│   ├── main.py           # FastAPI application entry point
│   ├── celery_app.py     # Celery configuration
│   ├── config.py         # Configuration management
│   ├── models.py         # Pydantic models
│   ├── database.py       # MongoDB connection
│   ├── redis_client.py   # Redis connection
│   ├── api/              # API routes
│   ├── tasks/            # Celery tasks
│   ├── Dockerfile        # Unified Docker image
│   ├── entrypoint.sh     # Service type selector
│   └── requirements.txt  # Python dependencies
├── frontend/             # React frontend
│   ├── src/              # Source code
│   │   ├── components/   # React components
│   │   ├── services/     # API services
│   │   └── types/        # TypeScript types
│   ├── Dockerfile        # Multi-stage build
│   ├── nginx.conf        # Nginx configuration
│   └── package.json      # Node dependencies
└── docker-compose.yml    # Local development setup
```

## Features

### Backend API Endpoints

- `GET /api/health` - Health check for all services
- `GET /api/metrics` - Application metrics
- `POST /api/tasks` - Create async task
- `GET /api/tasks/{id}` - Get task status
- `GET /api/data` - List data entries
- `POST /api/data` - Create data entry
- `GET /api/data/{id}` - Get data entry
- `PUT /api/data/{id}` - Update data entry
- `DELETE /api/data/{id}` - Delete data entry

### Celery Tasks

- **process_data**: Process data entries with progress tracking
- **generate_report**: Generate reports (summary, detailed, analytics)
- **simulate_load**: Simulate load for testing (low, medium, high intensity)
- **long_running_task**: Long-running task for testing

### Frontend Features

- **Dashboard**: System health and metrics overview
- **Data Manager**: CRUD operations for data entries
- **Task Runner**: Submit and monitor background tasks

## Getting Started

### Prerequisites

- Docker and Docker Compose
- (Optional) Node.js 20+ for local frontend development
- (Optional) Python 3.11+ for local backend development

### Running Locally with Docker Compose

1. **Build and start all services**:
   ```bash
   cd app
   docker-compose up --build
   ```

2. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - MongoDB: localhost:27017
   - Redis: localhost:6379

3. **Stop all services**:
   ```bash
   docker-compose down
   ```

4. **Clean up volumes** (removes all data):
   ```bash
   docker-compose down -v
   ```

### Development Mode

#### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MONGODB_URL=mongodb://localhost:27017
export REDIS_URL=redis://localhost:6379/0
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Run backend
python main.py

# In another terminal, run worker
celery -A celery_app worker --loglevel=info
```

#### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
export VITE_API_URL=http://localhost:8000/api

# Run development server
npm run dev
```

## Unified Docker Image

The backend and Celery workers use the same Docker image with different configurations:

**Backend**:
```yaml
environment:
  - SERVICE_TYPE=backend
```

**Worker**:
```yaml
environment:
  - SERVICE_TYPE=worker
  - WORKER_CONCURRENCY=4
```

**Beat Scheduler**:
```yaml
environment:
  - SERVICE_TYPE=beat
```

The `entrypoint.sh` script determines which service to start based on `SERVICE_TYPE`.

## Testing the Application

1. **Check system health**:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Create a data entry**:
   ```bash
   curl -X POST http://localhost:8000/api/data \
     -H "Content-Type: application/json" \
     -d '{"name":"Test","value":123.45,"status":"active"}'
   ```

3. **Submit a task**:
   ```bash
   curl -X POST http://localhost:8000/api/tasks \
     -H "Content-Type: application/json" \
     -d '{"task_type":"simulate_load","params":{"duration":10,"intensity":"medium"}}'
   ```

4. **Check task status** (replace TASK_ID):
   ```bash
   curl http://localhost:8000/api/tasks/TASK_ID
   ```

## Environment Variables

### Backend & Workers

| Variable | Default | Description |
|----------|---------|-------------|
| SERVICE_TYPE | backend | Service type: backend, worker, beat |
| MONGODB_URL | mongodb://mongodb:27017 | MongoDB connection string |
| MONGODB_DATABASE | loadtest_db | MongoDB database name |
| REDIS_URL | redis://redis:6379/0 | Redis connection string |
| CELERY_BROKER_URL | redis://redis:6379/0 | Celery broker URL |
| CELERY_RESULT_BACKEND | redis://redis:6379/1 | Celery result backend |
| APP_ENV | development | Application environment |
| LOG_LEVEL | info | Logging level |
| WORKER_CONCURRENCY | 4 | Number of worker processes |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| VITE_API_URL | http://localhost:8000/api | Backend API URL |

## Building for Production

### Backend/Worker Image

```bash
cd backend
docker build -t loadtest-app:latest .
```

### Frontend Image

```bash
cd frontend
docker build -t loadtest-frontend:latest .
```

## Next Steps

After successfully running the application locally:

1. Create Helm chart for Kubernetes deployment
2. Set up ArgoCD GitOps workflow
3. Deploy to Kubernetes cluster
4. Configure monitoring and alerting

## License

MIT
