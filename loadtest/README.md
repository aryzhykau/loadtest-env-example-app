# Load Testing with GitHub Actions and ArgoCD

Automated load testing workflow that creates ephemeral test environments using ArgoCD and runs Locust tests on self-hosted ARC (Actions Runner Controller) runners in Kubernetes.

## Overview

This workflow automates the following process:
1. **Build Images**: Build and push Docker images for the branch being tested
2. **Create Environment**: Deploy an ephemeral ArgoCD Application for the test environment
3. **Run Load Tests**: Execute Locust load tests against the deployed application
4. **Extract Reports**: Upload test results as GitHub artifacts
5. **Cleanup**: Delete the ephemeral environment

## Prerequisites

### 1. Actions Runner Controller (ARC) Setup

The workflow uses `runs-on: self-hosted` which requires ARC to be installed in your Kubernetes cluster.

**Verify ARC is running:**
```bash
kubectl get pods -n actions-runner-system
```

You should see runner pods with labels matching your repository.

### 2. ArgoCD Access

The self-hosted runner needs access to create/delete ArgoCD Applications:

```bash
# Verify kubectl access from runner
kubectl get application -n argocd
```

### 3. Container Registry

Images are pushed to GitHub Container Registry (ghcr.io). Ensure:
- Repository has `packages: write` permission
- GITHUB_TOKEN is available (automatic in GitHub Actions)

## Triggering the Workflow

### Option 1: Manual Trigger (workflow_dispatch)

Go to Actions → Load Test with Ephemeral Environment → Run workflow

**Parameters:**
- **Branch**: Branch to test (defaults to current branch)
- **Users**: Number of concurrent users (default: 50)
- **Spawn Rate**: Users spawned per second (default: 5)
- **Duration**: Test duration (default: 5m)

### Option 2: Pull Request Label

Add the `loadtest` label to any PR to automatically trigger the workflow.

```bash
# Using GitHub CLI
gh pr edit <PR_NUMBER> --add-label loadtest
```

## Load Test Scenarios

The Locust test suite (`loadtest/locustfile.py`) includes two user classes:

### LoadTestUser (Realistic Behavior)
- **Weight**: 70% of users
- **Wait Time**: 1-3 seconds between tasks
- **Tasks**:
  - Health checks (50% frequency)
  - Metrics retrieval (30%)
  - Data entry CRUD operations (15%)
  - Task creation (5%)

### HighLoadUser (Stress Testing)
- **Weight**: 30% of users
- **Wait Time**: 0.1-0.5 seconds (aggressive)
- **Tasks**:
  - Rapid health checks (60%)
  - Rapid data creation (30%)
  - Rapid task creation (10%)

## Understanding Results

### Artifacts

After each run, the following artifacts are uploaded:
- `report.html` - Interactive HTML report with charts
- `results_stats.csv` - Request statistics
- `results_failures.csv` - Failed requests details
- `results_exceptions.csv` - Exception details

Download from Actions → Workflow Run → Artifacts

### Key Metrics

**Response Times:**
- P50 (median): 50% of requests were faster than this
- P95: 95% of requests were faster than this
- P99: 99% of requests were faster than this

**Failure Rate:**
- Should be < 1% for healthy services
- > 5% indicates issues

**Requests Per Second (RPS):**
- Total throughput of the application
- Compare across runs to detect regression

### Example Summary Output

```
## Load Test Results for branch: feature/new-api

**Test Parameters:**
- Users: 50
- Spawn Rate: 5 users/sec
- Duration: 5m

**Results Summary:**
| Endpoint         | Requests | Failures | Median | P95   | P99   | RPS  |
|------------------|----------|----------|--------|-------|-------|------|
| /api/health      | 15000    | 0        | 12ms   | 25ms  | 35ms  | 50.0 |
| /api/data [GET]  | 6000     | 5        | 45ms   | 120ms | 180ms | 20.0 |
| /api/data [POST] | 3000     | 2        | 65ms   | 150ms | 220ms | 10.0 |
```

## Workflow Architecture

```
┌─────────────────┐
│ GitHub Actions  │
│  (ARC Runner)   │
└────────┬────────┘
         │
         ├─> Build Images ──> ghcr.io
         │
         ├─> Create ArgoCD App ──┐
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │  Kubernetes     │
         │              │  ┌────────────┐ │
         │              │  │ Backend    │ │
         │              │  │ Frontend   │ │
         │              │  │ Workers    │ │
         │              │  │ MongoDB    │ │
         │              │  │ Redis      │ │
         │              │  └────────────┘ │
         │              └─────────────────┘
         │                       │
         ├─> Run Locust Tests <──┘
         │         │
         │         ▼
         │    ┌─────────┐
         │    │ Reports │
         │    └─────────┘
         │
         └─> Cleanup ArgoCD App
```

## Customizing Tests

### Modify Test Scenarios

Edit `loadtest/locustfile.py`:

```python
@task(10)  # Task weight (higher = more frequent)
def my_custom_test(self):
    """My custom load test."""
    self.client.get("/api/my-endpoint")
```

### Change Test Parameters

In the workflow file (`.github/workflows/loadtest.yml`), modify defaults:

```yaml
users:
  description: 'Number of concurrent users'
  default: '100'  # Changed from 50
```

### Add Custom Metrics

Locust supports custom metrics:

```python
from locust import events

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Load test starting...")

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    if exception:
        print(f"Request failed: {name}")
```

## Troubleshooting

### Issue: Runner not found

**Error**: `No runner matching the specified labels was found`

**Solution**:
1. Check ARC installation: `kubectl get pods -n actions-runner-system`
2. Verify runner labels match `runs-on: self-hosted`
3. Scale runners if needed:
   ```bash
   kubectl scale deployment -n actions-runner-system <runner-deployment> --replicas=3
   ```

### Issue: ArgoCD Application won't sync

**Error**: `Timeout waiting for Application to sync`

**Solution**:
1. Check ArgoCD server: `kubectl get pods -n argocd`
2. View Application status:
   ```bash
   kubectl describe application -n argocd loadtest-<branch>
   ```
3. Check repository credentials in ArgoCD

### Issue: Pods not starting

**Error**: `Timeout waiting for pods to be ready`

**Solution**:
1. Check pod status:
   ```bash
   kubectl get pods -n loadtest-<branch>
   kubectl describe pod -n loadtest-<branch> <pod-name>
   ```
2. Common issues:
   - Image pull failures (check registry credentials)
   - Resource limits (insufficient CPU/memory)
   - PVC provisioning (check StorageClass)

### Issue: Load test fails to connect

**Error**: `Connection refused` or `Name resolution failed`

**Solution**:
1. Verify ingress controller: `kubectl get svc -n ingress-nginx`
2. Check /etc/hosts entry was added correctly
3. Verify DNS resolution: `nslookup loadtest-<branch>.local`
4. Test manually: `curl http://loadtest-<branch>.local/api/health`

## CI/CD Integration

### Automatic PR Testing

Add to `.github/workflows/pr-checks.yml`:

```yaml
name: PR Checks

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  trigger-loadtest:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.title, '[loadtest]')
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.addLabels({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              labels: ['loadtest']
            })
```

### Performance Regression Detection

Compare results across runs:

```python
# Add to locustfile.py
import os

def on_test_stop(environment, **kwargs):
    stats = environment.stats.total
    
    # Define SLOs
    if stats.avg_response_time > 100:  # 100ms avg
        environment.process_exit_code = 1
        print("FAIL: Average response time exceeded SLO")
    
    if stats.fail_ratio > 0.01:  # 1% failure rate
        environment.process_exit_code = 1
        print("FAIL: Failure rate exceeded SLO")
```

## Best Practices

1. **Start Small**: Begin with 10-20 users, gradually increase
2. **Warm-up**: Allow 1-2 minutes for pods to warm up JIT compilers
3. **Realistic Scenarios**: Model actual user behavior, not just endpoint hammering
4. **Monitor Resources**: Watch CPU/memory during tests
5. **Clean Data**: Reset databases between major test runs
6. **Document Changes**: Update this README when modifying tests

## Resources

- [Locust Documentation](https://docs.locust.io/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Actions Runner Controller](https://github.com/actions/actions-runner-controller)
- [GitHub Actions Self-hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners)
