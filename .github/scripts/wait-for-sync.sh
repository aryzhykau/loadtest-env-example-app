#!/bin/bash
# Wait for ArgoCD Application to sync and become healthy
# Usage: ./wait-for-sync.sh <branch-name> [timeout-seconds]

set -e

BRANCH_NAME=$1
TIMEOUT=${2:-600}  # Default 10 minutes
APP_NAME="loadtest-${BRANCH_NAME}"

if [ -z "$BRANCH_NAME" ]; then
  echo "Error: Branch name is required"
  echo "Usage: $0 <branch-name> [timeout-seconds]"
  exit 1
fi

echo "Waiting for ArgoCD Application '$APP_NAME' to sync (timeout: ${TIMEOUT}s)..."

START_TIME=$(date +%s)

while true; do
  CURRENT_TIME=$(date +%s)
  ELAPSED=$((CURRENT_TIME - START_TIME))
  
  if [ $ELAPSED -gt $TIMEOUT ]; then
    echo "✗ Timeout waiting for Application to sync"
    kubectl get application -n argocd "$APP_NAME" -o yaml
    exit 1
  fi
  
  # Get sync and health status
  SYNC_STATUS=$(kubectl get application -n argocd "$APP_NAME" -o jsonpath='{.status.sync.status}' 2>/dev/null || echo "Unknown")
  HEALTH_STATUS=$(kubectl get application -n argocd "$APP_NAME" -o jsonpath='{.status.health.status}' 2>/dev/null || echo "Unknown")
  
  echo "[${ELAPSED}s] Sync: $SYNC_STATUS | Health: $HEALTH_STATUS"
  
  if [ "$SYNC_STATUS" = "Synced" ] && [ "$HEALTH_STATUS" = "Healthy" ]; then
    echo "✓ Application is Synced and Healthy!"
    break
  fi
  
  if [ "$SYNC_STATUS" = "Unknown" ] || [ "$HEALTH_STATUS" = "Degraded" ]; then
    echo "Warning: Application in degraded state. Checking resources..."
    kubectl get application -n argocd "$APP_NAME" -o jsonpath='{.status.conditions}' | jq '.' || true
  fi
  
  sleep 10
done

echo ""
echo "Application resources:"
kubectl get pods -n "loadtest-${BRANCH_NAME}"
