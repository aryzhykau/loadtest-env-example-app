#!/bin/bash
# Create ArgoCD Application for ephemeral environment
# Usage: ./create-argocd-app.sh <branch-name>

set -e

BRANCH_NAME=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILE="${SCRIPT_DIR}/../argocd-app-template.yaml"
APP_NAME="loadtest-${BRANCH_NAME}"

if [ -z "$BRANCH_NAME" ]; then
  echo "Error: Branch name is required"
  echo "Usage: $0 <branch-name>"
  exit 1
fi

# Sanitize branch name for Kubernetes resource names (lowercase, replace / with -)
SANITIZED_BRANCH=$(echo "$BRANCH_NAME" | tr '[:upper:]' '[:lower:]' | tr '/' '-')

echo "Creating ArgoCD Application for branch: $BRANCH_NAME"
echo "Sanitized name: loadtest-$SANITIZED_BRANCH"

# Create temporary file with substituted values
TMP_FILE=$(mktemp)
sed "s/{BRANCH_NAME}/${SANITIZED_BRANCH}/g" "$TEMPLATE_FILE" > "$TMP_FILE"

# Apply the Application
kubectl apply -f "$TMP_FILE"

# Clean up
rm "$TMP_FILE"

echo "✓ ArgoCD Application 'loadtest-${SANITIZED_BRANCH}' created successfully"
echo ""
echo "Monitor sync status with:"
echo "  kubectl get application -n argocd loadtest-${SANITIZED_BRANCH}"
echo ""
echo "Or wait for sync:"
echo "  $SCRIPT_DIR/wait-for-sync.sh ${SANITIZED_BRANCH}"
