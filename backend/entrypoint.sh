#!/bin/bash
set -e

echo "Service Type: ${SERVICE_TYPE}"

case "${SERVICE_TYPE}" in
  backend)
    echo "Starting FastAPI Backend on port 8000..."
    exec uvicorn main:app --host 0.0.0.0 --port 8000
    ;;
  
  worker)
    echo "Starting Celery Worker..."
    echo "Concurrency: ${WORKER_CONCURRENCY:-4}"
    echo "Prefetch Multiplier: ${WORKER_PREFETCH_MULTIPLIER:-4}"
    exec celery -A celery_app worker \
      --loglevel=${LOG_LEVEL:-info} \
      --concurrency=${WORKER_CONCURRENCY:-4} \
      --prefetch-multiplier=${WORKER_PREFETCH_MULTIPLIER:-4}
    ;;
  
  beat)
    echo "Starting Celery Beat scheduler..."
    exec celery -A celery_app beat --loglevel=${LOG_LEVEL:-info}
    ;;
  
  *)
    echo "ERROR: Unknown SERVICE_TYPE: ${SERVICE_TYPE}"
    echo "Valid options: backend, worker, beat"
    exit 1
    ;;
esac
