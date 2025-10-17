# Building and Using Local Images with Docker Desktop Kubernetes

## Overview

When using Docker Desktop's built-in Kubernetes on macOS, images built locally with Docker are automatically available to Kubernetes. No need to push to a registry!

## Build the Images

### 1. Build Backend/Worker Image

```bash
cd /Users/andrejryzikov/loadtest-env-example/app/backend
docker build -t loadtest/app:1.0.0 .
```

This single image is used for both backend and workers (SERVICE_TYPE env var selects the mode).

### 2. Build Frontend Image

```bash
cd /Users/andrejryzikov/loadtest-env-example/app/frontend
docker build -t loadtest/frontend:1.0.0 .
```

### 3. Verify Images

```bash
docker images | grep loadtest
```

You should see:
```
loadtest/app        1.0.0    ...
loadtest/frontend   1.0.0    ...
```

## Configure Helm Chart for Local Images

Update the values to use local images with `imagePullPolicy: Never` or `IfNotPresent`:

```yaml
image:
  repository: loadtest/app
  tag: "1.0.0"
  pullPolicy: IfNotPresent  # Use local image if available

frontend:
  image:
    repository: loadtest/frontend
    tag: "1.0.0"
    pullPolicy: IfNotPresent
```

## Install the Chart

```bash
cd /Users/andrejryzikov/loadtest-env-example/app/helm

# Install with local images
helm install loadtest loadtest-app \
  --namespace loadtest \
  --create-namespace \
  --set image.pullPolicy=IfNotPresent \
  --set frontend.image.pullPolicy=IfNotPresent \
  --set mongodb.auth.password=testpass123 \
  --set mongodb.auth.rootPassword=rootpass123
```

## Development Workflow

When you make changes to your code:

```bash
# 1. Rebuild the image
cd /Users/andrejryzikov/loadtest-env-example/app/backend
docker build -t loadtest/app:1.0.0 .

# 2. Restart the pods to use new image
kubectl rollout restart deployment -n loadtest loadtest-backend
kubectl rollout restart deployment -n loadtest loadtest-worker

# Or delete pods to force recreation
kubectl delete pods -n loadtest -l app.kubernetes.io/component=backend
kubectl delete pods -n loadtest -l app.kubernetes.io/component=worker
```

## Using Dev Tag for Faster Iteration

For development, use a consistent tag like `dev` or `latest`:

```bash
# Build with dev tag
docker build -t loadtest/app:dev ./backend
docker build -t loadtest/frontend:dev ./frontend

# Install/upgrade with dev tag and Always pull policy
helm upgrade --install loadtest loadtest-app \
  --namespace loadtest \
  --create-namespace \
  -f loadtest-app/values-dev.yaml \
  --set image.tag=dev \
  --set image.pullPolicy=Always \
  --set frontend.image.tag=dev \
  --set frontend.image.pullPolicy=Always \
  --set mongodb.auth.password=devpass \
  --set mongodb.auth.rootPassword=devroot
```

With `pullPolicy: Always`, Kubernetes will check for image updates even with same tag.

## Troubleshooting

### Image Pull Errors

If you see `ImagePullBackOff` or `ErrImagePull`:

```bash
# Check if image exists locally
docker images loadtest/app
docker images loadtest/frontend

# Check pod events
kubectl describe pod -n loadtest <pod-name>
```

### Image Not Found

Kubernetes may not find the image if:
1. The image name/tag doesn't match exactly
2. The image was built on different Docker context

Solution:
```bash
# Verify Docker context
docker context ls

# Should show docker-desktop as current
# Rebuild images if needed
```

### Force Image Reload

```bash
# Delete the pod to force recreation
kubectl delete pod -n loadtest <pod-name>

# Or set imagePullPolicy to Always temporarily
helm upgrade loadtest loadtest-app \
  --set image.pullPolicy=Always \
  --set frontend.image.pullPolicy=Always \
  --reuse-values
```

## Quick Commands

```bash
# Build all images
cd /Users/andrejryzikov/loadtest-env-example/app
docker build -t loadtest/app:1.0.0 ./backend
docker build -t loadtest/frontend:1.0.0 ./frontend

# Install/upgrade chart
helm upgrade --install loadtest helm/loadtest-app \
  --namespace loadtest \
  --create-namespace \
  --set mongodb.auth.password=testpass123 \
  --set mongodb.auth.rootPassword=rootpass123

# Watch deployment
kubectl get pods -n loadtest -w

# Check logs
kubectl logs -n loadtest -l app.kubernetes.io/component=backend --tail=50 -f
```

## Complete Example

```bash
#!/bin/bash
set -e

echo "Building images..."
cd /Users/andrejryzikov/loadtest-env-example/app
docker build -t loadtest/app:1.0.0 ./backend
docker build -t loadtest/frontend:1.0.0 ./frontend

echo "Installing Helm chart..."
helm upgrade --install loadtest helm/loadtest-app \
  --namespace loadtest \
  --create-namespace \
  --set image.repository=loadtest/app \
  --set image.tag=1.0.0 \
  --set image.pullPolicy=IfNotPresent \
  --set frontend.image.repository=loadtest/frontend \
  --set frontend.image.tag=1.0.0 \
  --set frontend.image.pullPolicy=IfNotPresent \
  --set mongodb.auth.password=testpass123 \
  --set mongodb.auth.rootPassword=rootpass123 \
  --wait \
  --timeout 5m

echo "Checking deployment..."
kubectl get pods -n loadtest

echo "Done! Access at http://loadtest.local (add to /etc/hosts)"
```

Save this as `deploy-local.sh` and run:
```bash
chmod +x deploy-local.sh
./deploy-local.sh
```
