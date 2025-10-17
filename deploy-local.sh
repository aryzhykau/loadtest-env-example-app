#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== LoadTest Application - Local Deployment ===${NC}\n"

# Navigate to app directory
APP_DIR="/Users/andrejryzikov/loadtest-env-example/app"
cd "$APP_DIR"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Building backend/worker image...${NC}"
docker build -t loadtest/app:1.0.0 ./backend
echo -e "${GREEN}✓ Backend/worker image built${NC}\n"

echo -e "${YELLOW}Step 2: Building frontend image...${NC}"
docker build -t loadtest/frontend:1.0.0 ./frontend
echo -e "${GREEN}✓ Frontend image built${NC}\n"

echo -e "${YELLOW}Step 3: Verifying images...${NC}"
docker images | grep loadtest
echo ""

echo -e "${YELLOW}Step 4: Installing/Upgrading Helm chart...${NC}"
helm upgrade --install loadtest ./helm/loadtest-app \
  --namespace loadtest \
  --create-namespace \
  --set image.repository=loadtest/app \
  --set image.tag=1.0.0 \
  --set image.pullPolicy=IfNotPresent \
  --set frontend.image.repository=loadtest/frontend \
  --set frontend.image.tag=1.0.0 \
  --set frontend.image.pullPolicy=IfNotPresent \
  --set mongodb.auth.password=rootpass123 \
  --set mongodb.auth.rootPassword=rootpass123 \
  --wait \
  --timeout 5m

echo -e "${GREEN}✓ Helm chart installed${NC}\n"

echo -e "${YELLOW}Step 5: Checking deployment status...${NC}"
kubectl get pods -n loadtest
echo ""

echo -e "${GREEN}=== Deployment Complete ===${NC}\n"

echo -e "Access URLs:"
echo -e "  Frontend: ${YELLOW}http://loadtest.local${NC}"
echo -e "  Backend API: ${YELLOW}http://loadtest.local/api${NC}"
echo -e "  API Docs: ${YELLOW}http://loadtest.local/docs${NC}"
echo ""

echo -e "${YELLOW}Note:${NC} Add to /etc/hosts if not already done:"
echo -e "  ${YELLOW}127.0.0.1 loadtest.local${NC}"
echo ""

echo -e "Useful commands:"
echo -e "  View pods: ${YELLOW}kubectl get pods -n loadtest${NC}"
echo -e "  Backend logs: ${YELLOW}kubectl logs -n loadtest -l app.kubernetes.io/component=backend -f${NC}"
echo -e "  Worker logs: ${YELLOW}kubectl logs -n loadtest -l app.kubernetes.io/component=worker -f${NC}"
echo -e "  Uninstall: ${YELLOW}helm uninstall loadtest -n loadtest${NC}"
