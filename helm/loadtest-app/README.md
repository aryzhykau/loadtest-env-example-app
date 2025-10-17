# LoadTest Application Helm Chart

A production-ready Helm chart for deploying the LoadTest demo application to Kubernetes. This chart deploys a complete stack including FastAPI backend, React frontend, Celery workers, MongoDB, and Redis.

## TL;DR

```bash
# Install with default values
helm install loadtest ./helm/loadtest-app

# Install with development values
helm install loadtest ./helm/loadtest-app -f ./helm/loadtest-app/values-dev.yaml

# Install with production values and set passwords
helm install loadtest ./helm/loadtest-app \
  -f ./helm/loadtest-app/values-prod.yaml \
  --set mongodb.auth.password=securepass \
  --set mongodb.auth.rootPassword=rootpass
```

## Introduction

This chart deploys the LoadTest application on a Kubernetes cluster using the Helm package manager.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure (for persistence)
- Ingress controller (nginx-ingress recommended)
- cert-manager (optional, for TLS certificates)
- Prometheus Operator (optional, for monitoring)

## Architecture

The chart deploys the following components:

- **Backend API** (FastAPI): REST API server with health checks and metrics
- **Frontend** (React + Nginx): Single-page application
- **Workers** (Celery): Background task processing (uses same image as backend)
- **MongoDB**: Primary database for application data
- **Redis**: Message broker for Celery and caching

### Unified Image Strategy

The backend and workers use the **same Docker image** but run different services based on the `SERVICE_TYPE` environment variable:
- Backend: `SERVICE_TYPE=backend` → Runs FastAPI with uvicorn
- Worker: `SERVICE_TYPE=worker` → Runs Celery worker

This approach:
- Reduces build complexity (single build pipeline)
- Ensures code consistency between API and workers
- Simplifies version management
- Reduces total image storage

## Installing the Chart

### Basic Installation

```bash
helm install loadtest ./helm/loadtest-app --namespace loadtest --create-namespace
```

### Development Installation

```bash
helm install loadtest ./helm/loadtest-app \
  --namespace loadtest-dev \
  --create-namespace \
  -f ./helm/loadtest-app/values-dev.yaml \
  --set mongodb.auth.password=devpass \
  --set mongodb.auth.rootPassword=devroot
```

### Production Installation

```bash
helm install loadtest ./helm/loadtest-app \
  --namespace loadtest-prod \
  --create-namespace \
  -f ./helm/loadtest-app/values-prod.yaml \
  --set image.repository=yourregistry.io/loadtest/app \
  --set image.tag=1.0.0 \
  --set frontend.image.repository=yourregistry.io/loadtest/frontend \
  --set frontend.image.tag=1.0.0 \
  --set mongodb.auth.password=$(openssl rand -base64 32) \
  --set mongodb.auth.rootPassword=$(openssl rand -base64 32)
```

## Uninstalling the Chart

```bash
helm uninstall loadtest --namespace loadtest
```

This removes all the Kubernetes components associated with the chart and deletes the release.

To also delete PVCs:

```bash
kubectl delete pvc -n loadtest -l app.kubernetes.io/instance=loadtest
```

## Configuration

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.environment` | Environment name | `development` |
| `global.imagePullPolicy` | Image pull policy | `IfNotPresent` |
| `nameOverride` | Override chart name | `""` |
| `fullnameOverride` | Override full name | `""` |

### Image Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Backend/Worker image repository | `loadtest/app` |
| `image.tag` | Backend/Worker image tag | `1.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `image.pullSecrets` | Image pull secrets | `[]` |

### Backend Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `backend.enabled` | Enable backend deployment | `true` |
| `backend.replicaCount` | Number of replicas | `2` |
| `backend.service.type` | Service type | `ClusterIP` |
| `backend.service.port` | Service port | `8000` |
| `backend.resources.requests.cpu` | CPU request | `100m` |
| `backend.resources.requests.memory` | Memory request | `128Mi` |
| `backend.resources.limits.cpu` | CPU limit | `500m` |
| `backend.resources.limits.memory` | Memory limit | `512Mi` |
| `backend.autoscaling.enabled` | Enable HPA | `true` |
| `backend.autoscaling.minReplicas` | Min replicas | `2` |
| `backend.autoscaling.maxReplicas` | Max replicas | `10` |

### Frontend Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.enabled` | Enable frontend deployment | `true` |
| `frontend.replicaCount` | Number of replicas | `2` |
| `frontend.image.repository` | Frontend image repository | `loadtest/frontend` |
| `frontend.image.tag` | Frontend image tag | `1.0.0` |
| `frontend.service.type` | Service type | `ClusterIP` |
| `frontend.service.port` | Service port | `80` |
| `frontend.autoscaling.enabled` | Enable HPA | `true` |

### Worker Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `workers.enabled` | Enable workers | `true` |
| `workers.replicaCount` | Number of replicas | `2` |
| `workers.env.WORKER_CONCURRENCY` | Worker concurrency | `"4"` |
| `workers.autoscaling.enabled` | Enable HPA | `true` |
| `workers.autoscaling.minReplicas` | Min replicas | `2` |
| `workers.autoscaling.maxReplicas` | Max replicas | `10` |

### MongoDB Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mongodb.enabled` | Enable MongoDB | `true` |
| `mongodb.image.repository` | MongoDB image | `mongo` |
| `mongodb.image.tag` | MongoDB version | `7.0` |
| `mongodb.persistence.enabled` | Enable persistence | `true` |
| `mongodb.persistence.size` | PVC size | `5Gi` |
| `mongodb.auth.enabled` | Enable authentication | `true` |
| `mongodb.auth.database` | Database name | `loadtest_db` |
| `mongodb.auth.username` | Database username | `loadtest_user` |
| `mongodb.auth.password` | Database password | `""` (required) |
| `mongodb.auth.rootPassword` | Root password | `""` (required) |

### Redis Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.enabled` | Enable Redis | `true` |
| `redis.image.repository` | Redis image | `redis` |
| `redis.image.tag` | Redis version | `7.2-alpine` |
| `redis.persistence.enabled` | Enable persistence | `true` |
| `redis.persistence.size` | PVC size | `1Gi` |
| `redis.config.maxmemory` | Max memory | `256mb` |

### Ingress Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class | `nginx` |
| `ingress.hosts[0].host` | Hostname | `loadtest.local` |
| `ingress.tls` | TLS configuration | `[]` |

### Monitoring Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `monitoring.enabled` | Enable monitoring | `true` |
| `monitoring.serviceMonitor.enabled` | Enable ServiceMonitor | `true` |
| `monitoring.serviceMonitor.interval` | Scrape interval | `30s` |

## Examples

### Install with Custom Domain

```bash
helm install loadtest ./helm/loadtest-app \
  --set ingress.hosts[0].host=myapp.example.com \
  --set ingress.tls[0].secretName=myapp-tls \
  --set ingress.tls[0].hosts[0]=myapp.example.com
```

### Scale Workers

```bash
helm upgrade loadtest ./helm/loadtest-app \
  --set workers.replicaCount=5 \
  --set workers.autoscaling.minReplicas=5 \
  --set workers.autoscaling.maxReplicas=20
```

### Use External MongoDB

```bash
helm install loadtest ./helm/loadtest-app \
  --set mongodb.enabled=false \
  --set mongodb.externalUrl=mongodb://external-mongo:27017
```

### Disable Persistence

```bash
helm install loadtest ./helm/loadtest-app \
  --set mongodb.persistence.enabled=false \
  --set redis.persistence.enabled=false
```

## Upgrading

```bash
# Upgrade with new values
helm upgrade loadtest ./helm/loadtest-app -f values-prod.yaml

# Upgrade and change image tag
helm upgrade loadtest ./helm/loadtest-app --set image.tag=1.1.0
```

## Testing the Installation

```bash
# Check pods
kubectl get pods -n loadtest

# Check services
kubectl get svc -n loadtest

# Check ingress
kubectl get ingress -n loadtest

# Test backend health
kubectl port-forward -n loadtest svc/loadtest-backend 8000:8000
curl http://localhost:8000/api/health

# View backend logs
kubectl logs -n loadtest -l app.kubernetes.io/component=backend --tail=100

# View worker logs
kubectl logs -n loadtest -l app.kubernetes.io/component=worker --tail=100
```

## Troubleshooting

### Pods not starting

```bash
# Check events
kubectl get events -n loadtest --sort-by='.lastTimestamp'

# Describe pod
kubectl describe pod -n loadtest <pod-name>

# Check logs
kubectl logs -n loadtest <pod-name>
```

### MongoDB connection issues

```bash
# Check MongoDB pod
kubectl get pod -n loadtest -l app.kubernetes.io/component=mongodb

# Test MongoDB connection
kubectl exec -n loadtest -it <mongodb-pod> -- mongosh
```

### Redis connection issues

```bash
# Check Redis pod
kubectl get pod -n loadtest -l app.kubernetes.io/component=redis

# Test Redis connection
kubectl exec -n loadtest -it <redis-pod> -- redis-cli ping
```

### Ingress not working

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress rules
kubectl describe ingress -n loadtest

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

## Values Files

The chart includes environment-specific values files:

- `values.yaml` - Default values with reasonable defaults
- `values-dev.yaml` - Development environment (reduced resources, no persistence)
- `values-prod.yaml` - Production environment (HA, persistence, monitoring)

## License

MIT

## Maintainers

- LoadTest Team <team@example.com>
