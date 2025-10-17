#!/bin/bash
# Delete ArgoCD Application and clean up ephemeral environment
# Usage: ./delete-argocd-app.sh <branch-name>

set -e

BRANCH_NAME=$1
APP_NAME="loadtest-${BRANCH_NAME}"
NAMESPACE="loadtest-${BRANCH_NAME}"

if [ -z "$BRANCH_NAME" ]; then
  echo "Error: Branch name is required"
  echo "Usage: $0 <branch-name>"
  exit 1
fi

echo "Deleting ArgoCD Application: $APP_NAME"

# Delete the Application (will cascade to namespace due to finalizer)
kubectl delete application -n argocd "$APP_NAME" --wait=true --timeout=5m || {
  echo "Warning: Failed to delete Application gracefully, forcing cleanup..."
  kubectl patch application -n argocd "$APP_NAME" -p '{"metadata":{"finalizers":[]}}' --type=merge || true
  kubectl delete application -n argocd "$APP_NAME" --force --grace-period=0 || true
}

echo "✓ Application deleted"

# Ensure namespace is deleted
if kubectl get namespace "$NAMESPACE" &>/dev/null; then
  echo "Cleaning up namespace: $NAMESPACE"
  kubectl delete namespace "$NAMESPACE" --wait=true --timeout=5m || {
    echo "Warning: Namespace stuck in Terminating state, forcing cleanup..."
    kubectl patch namespace "$NAMESPACE" -p '{"metadata":{"finalizers":[]}}' --type=merge || true
  }
  echo "✓ Namespace deleted"
else
  echo "✓ Namespace already deleted"
fi

echo ""
echo "Ephemeral environment for branch '$BRANCH_NAME' cleaned up successfully"
