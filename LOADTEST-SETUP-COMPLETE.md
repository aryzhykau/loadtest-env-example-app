# GitHub Actions Load Testing Setup - Complete

## What Was Created

✅ **Load Test Scripts**
- `app/loadtest/locustfile.py` - Locust test scenarios with two user classes (normal and high-load)
- `app/loadtest/requirements.txt` - Python dependencies for Locust

✅ **ArgoCD Integration**
- `app/.github/argocd-app-template.yaml` - Template for ephemeral test environments
- Creates isolated namespace per branch: `loadtest-{branch-name}`

✅ **Helper Scripts** (executable)
- `app/.github/scripts/create-argocd-app.sh` - Create ArgoCD Application
- `app/.github/scripts/wait-for-sync.sh` - Wait for sync completion
- `app/.github/scripts/delete-argocd-app.sh` - Clean up environment

✅ **GitHub Actions Workflow**
- `app/.github/workflows/loadtest.yml` - Complete automated workflow
- Runs on self-hosted ARC runners in Kubernetes

✅ **Documentation**
- `app/loadtest/README.md` - Comprehensive usage guide

## How It Works

### Workflow Trigger Options

**1. Manual (workflow_dispatch)**
```bash
# Via GitHub UI: Actions → Load Test → Run workflow
# Choose branch, users, spawn rate, duration
```

**2. Pull Request Label**
```bash
# Add 'loadtest' label to any PR
gh pr edit <PR_NUMBER> --add-label loadtest
```

### Workflow Steps

1. **Check Trigger** → Determines if workflow should run
2. **Build Images** → Builds and pushes Docker images to ghcr.io
3. **Create Environment** → Deploys ArgoCD Application with namespace `loadtest-{branch}`
4. **Run Load Test** → Executes Locust tests against deployed app
5. **Upload Reports** → Saves HTML report and CSV data as artifacts
6. **Cleanup** → Deletes ArgoCD Application and namespace

### Test Environment Details

Each branch gets:
- **Namespace**: `loadtest-{sanitized-branch-name}`
- **Domain**: `loadtest-{branch}.local`
- **Resources**: Backend (2 replicas), Frontend (2 replicas), Workers (2 replicas), MongoDB, Redis
- **ArgoCD**: Auto-sync enabled with pruning

## What You Need to Configure

### 1. Actions Runner Controller (ARC) Setup

The workflow uses `runs-on: self-hosted` which requires ARC runners in your Kubernetes cluster.

**Check if ARC is installed:**
```bash
kubectl get pods -n actions-runner-system
```

If not installed, ARC was deployed via your Terraform infra. Verify the runner is registered:
```bash
kubectl get runners -n actions-runner-system
```

**Configure runner for your repository:**

The runner needs:
- Access to GitHub repository
- Kubernetes RBAC to create/delete ArgoCD Applications
- Network access to ingress controller

### 2. Container Registry Authentication

Images are pushed to GitHub Container Registry (ghcr.io).

**Enable in repository:**
1. Go to Settings → Actions → General
2. Workflow permissions → Enable "Read and write permissions"
3. Save

No manual token needed - GITHUB_TOKEN is automatic.

### 3. ArgoCD Repository Credentials

The ArgoCD Application template references your Git repository.

**Already configured** in your infra Terraform:
- `infra/config/argocd-values.yaml` has repository credentials

**Verify:**
```bash
kubectl get secret -n argocd -l argocd.argoproj.io/secret-type=repository
```

### 4. Ingress DNS Resolution

The load test connects to `http://loadtest-{branch}.local`.

**For local testing**, add to runner's `/etc/hosts`:
```bash
127.0.0.1 loadtest-main.local
127.0.0.1 loadtest-feature-xyz.local
```

**For production**, use real DNS with wildcard:
```
*.loadtest.yourdomain.com → Ingress Controller IP
```

## Testing the Workflow

### Quick Test

1. **Trigger manually** from GitHub Actions UI:
   - Branch: `main`
   - Users: `10` (start small)
   - Spawn Rate: `2`
   - Duration: `1m`

2. **Monitor progress**:
   ```bash
   # Watch ArgoCD Application
   kubectl get application -n argocd -w
   
   # Watch pods
   kubectl get pods -n loadtest-main -w
   
   # Check load test logs (when running)
   # The workflow output will show Locust progress
   ```

3. **Download results**:
   - Go to workflow run → Artifacts
   - Download `loadtest-results-main`
   - Open `report.html` in browser

### Expected Results (Healthy System)

For 10 users, 1 minute test:
- **Success Rate**: > 99%
- **Median Response Time**: < 100ms for `/api/health`
- **P95 Response Time**: < 200ms
- **No 5xx errors**

## Advanced Configuration

### Customize Test Scenarios

Edit `app/loadtest/locustfile.py`:

```python
@task(10)  # Weight: how often this runs
def my_test(self):
    self.client.get("/api/my-endpoint")
```

### Change Default Parameters

Edit `app/.github/workflows/loadtest.yml`:

```yaml
users:
  default: '100'  # More aggressive
duration:
  default: '10m'  # Longer test
```

### Add Performance SLOs

Add to `locustfile.py`:

```python
from locust import events

@events.test_stop.add_listener
def check_slo(environment, **kwargs):
    stats = environment.stats.total
    if stats.avg_response_time > 100:  # 100ms SLO
        print("❌ FAIL: Response time SLO violated")
        environment.process_exit_code = 1
```

### Use Different Image Registry

Edit workflow to use Docker Hub or ECR:

```yaml
env:
  REGISTRY: docker.io  # or: 123456789.dkr.ecr.us-east-1.amazonaws.com
  IMAGE_NAME_BACKEND: youruser/loadtest-app
```

## Troubleshooting

### Runner Not Found
```
Error: No runner matching the specified labels was found
```

**Solution:**
```bash
# Check ARC runners
kubectl get pods -n actions-runner-system

# If missing, check Terraform deployment
cd infra
terraform apply -target=helm_release.k8s_services["github-actions-operator"]
```

### ArgoCD Sync Timeout
```
Error: Timeout waiting for Application to sync
```

**Solution:**
```bash
# Check ArgoCD status
kubectl get pods -n argocd

# View Application details
kubectl describe application -n argocd loadtest-<branch>

# Check repository credentials
kubectl get secret -n argocd -l argocd.argoproj.io/secret-type=repository
```

### Image Pull Errors
```
Error: Failed to pull image ghcr.io/...
```

**Solution:**
```bash
# Verify GITHUB_TOKEN permissions (in repo settings)
# Or create imagePullSecret:
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=$GITHUB_ACTOR \
  --docker-password=$GITHUB_TOKEN \
  -n loadtest-<branch>
```

## Next Steps

1. **Test the workflow** with a small load (10 users, 1 minute)
2. **Review results** in the HTML report artifact
3. **Gradually increase** load to find your system limits
4. **Set up alerts** based on P95/P99 response times
5. **Add to CI/CD** by auto-labeling PRs with `loadtest`

## Files Reference

```
app/
├── .github/
│   ├── workflows/
│   │   └── loadtest.yml              # Main workflow
│   ├── scripts/
│   │   ├── create-argocd-app.sh     # Create test env
│   │   ├── wait-for-sync.sh         # Wait for ready
│   │   └── delete-argocd-app.sh     # Cleanup
│   └── argocd-app-template.yaml     # ArgoCD template
└── loadtest/
    ├── locustfile.py                # Test scenarios
    ├── requirements.txt             # Python deps
    └── README.md                    # Usage guide
```

## Success Criteria

✅ Workflow triggers manually or via PR label
✅ Images build and push to registry
✅ ArgoCD creates ephemeral environment
✅ Pods start and become healthy
✅ Load test runs and completes
✅ Reports upload as artifacts
✅ Environment cleans up automatically

---

**Ready to test!** Trigger the workflow from GitHub Actions UI with default parameters (10 users, 1 min) to validate the setup.
