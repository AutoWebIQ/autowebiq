#!/bin/bash

# AutoWebIQ GKE Deployment Script
# This script builds Docker images, pushes to Docker Hub, and deploys to GKE

set -e  # Exit on error

echo "🚀 AutoWebIQ GKE Deployment Script"
echo "====================================="

# Load environment variables
source backend/.env

# Configuration
PROJECT_ID="autowebiq-476616"
CLUSTER_NAME="autowebiq-cluster"
CLUSTER_REGION="asia-south1"
DOCKER_REPO="aashikzm098"
NAMESPACE="autowebiq"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Step 1: Authenticating with GCP${NC}"
gcloud auth login --brief
gcloud config set project $PROJECT_ID

echo -e "${GREEN}Step 2: Connecting to GKE cluster${NC}"
gcloud container clusters get-credentials $CLUSTER_NAME --region=$CLUSTER_REGION

echo -e "${GREEN}Step 3: Building Docker images${NC}"
echo "Building backend image..."
docker build -t $DOCKER_REPO/autowebiq-backend:latest -t $DOCKER_REPO/autowebiq-backend:$(date +%Y%m%d-%H%M%S) ./backend

echo "Building frontend image..."
# Update frontend .env for production
cp frontend/.env frontend/.env.backup
cat > frontend/.env << EOF
REACT_APP_BACKEND_URL=https://autowebiq.com
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF

docker build -t $DOCKER_REPO/autowebiq-frontend:latest -t $DOCKER_REPO/autowebiq-frontend:$(date +%Y%m%d-%H%M%S) ./frontend

# Restore original .env
mv frontend/.env.backup frontend/.env

echo -e "${GREEN}Step 4: Pushing images to Docker Hub${NC}"
echo "$DOCKER_HUB_TOKEN" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin

docker push $DOCKER_REPO/autowebiq-backend:latest
docker push $DOCKER_REPO/autowebiq-frontend:latest

echo -e "${GREEN}Step 5: Creating Kubernetes namespace${NC}"
kubectl apply -f k8s/namespace.yaml

echo -e "${GREEN}Step 6: Creating ConfigMap${NC}"
kubectl apply -f k8s/configmap.yaml

echo -e "${GREEN}Step 7: Creating Secrets from .env file${NC}"
kubectl create secret generic autowebiq-secrets \
  --from-env-file=backend/.env \
  --namespace=$NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}Step 8: Deploying MongoDB${NC}"
kubectl apply -f k8s/mongodb-deployment.yaml

echo -e "${GREEN}Step 9: Deploying Redis${NC}"
kubectl apply -f k8s/redis-deployment.yaml

echo "Waiting for databases to be ready..."
sleep 30

echo -e "${GREEN}Step 10: Deploying Backend${NC}"
kubectl apply -f k8s/backend-deployment.yaml

echo -e "${GREEN}Step 11: Deploying Frontend${NC}"
kubectl apply -f k8s/frontend-deployment.yaml

echo -e "${GREEN}Step 12: Setting up Auto-scaling${NC}"
kubectl apply -f k8s/hpa.yaml

echo -e "${GREEN}Step 13: Installing Nginx Ingress Controller${NC}"
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.5/deploy/static/provider/cloud/deploy.yaml

echo "Waiting for ingress controller..."
sleep 60

echo -e "${GREEN}Step 14: Installing cert-manager for SSL${NC}"
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

echo "Waiting for cert-manager..."
sleep 30

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: aashikzm098@gmail.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

echo -e "${GREEN}Step 15: Creating Ingress${NC}"
kubectl apply -f k8s/ingress.yaml

echo -e "${GREEN}Step 16: Getting LoadBalancer IP${NC}"
echo "Waiting for LoadBalancer IP..."
sleep 30

LOAD_BALANCER_IP=$(kubectl get svc ingress-nginx-controller -n ingress-nginx -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ -z "$LOAD_BALANCER_IP" ]; then
    echo -e "${YELLOW}Warning: LoadBalancer IP not ready yet. Run this to get it:${NC}"
    echo "kubectl get svc ingress-nginx-controller -n ingress-nginx"
else
    echo -e "${GREEN}LoadBalancer IP: $LOAD_BALANCER_IP${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANT: Update your DNS records:${NC}"
    echo "autowebiq.com        A    $LOAD_BALANCER_IP"
    echo "www.autowebiq.com    A    $LOAD_BALANCER_IP"
    echo "api.autowebiq.com    A    $LOAD_BALANCER_IP"
fi

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "Check deployment status:"
echo "kubectl get pods -n $NAMESPACE"
echo "kubectl get svc -n $NAMESPACE"
echo "kubectl get ingress -n $NAMESPACE"
echo ""
echo "View logs:"
echo "kubectl logs -f deployment/autowebiq-backend -n $NAMESPACE"
echo "kubectl logs -f deployment/autowebiq-frontend -n $NAMESPACE"
echo ""
echo "Once DNS is configured, your app will be live at:"
echo "🌐 https://autowebiq.com"
echo ""
echo "SSL certificates will be automatically issued by Let's Encrypt within 5-10 minutes."