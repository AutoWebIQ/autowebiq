#!/bin/bash
# AutoWebIQ GKE Deployment Script
# This script automates the deployment of AutoWebIQ to Google Kubernetes Engine

set -e

echo "========================================="
echo "AutoWebIQ GKE Deployment Script"
echo "========================================="
echo ""

# Configuration
PROJECT_ID="autowebiq-476616"
CLUSTER_NAME="autowebiq-cluster"
CLUSTER_REGION="asia-south1"
SERVICE_ACCOUNT_KEY="/app/gcp-service-account.json"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_step "Checking prerequisites..."

if [ ! -f "$SERVICE_ACCOUNT_KEY" ]; then
    print_error "Service account key not found at $SERVICE_ACCOUNT_KEY"
    exit 1
fi

if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Please install kubectl."
    exit 1
fi

print_step "Prerequisites check passed!"
echo ""

# Authenticate with GCP
print_step "Authenticating with Google Cloud..."
gcloud auth activate-service-account --key-file=$SERVICE_ACCOUNT_KEY
gcloud config set project $PROJECT_ID
print_step "Authentication successful!"
echo ""

# Get cluster credentials
print_step "Getting GKE cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --region=$CLUSTER_REGION
print_step "Credentials obtained!"
echo ""

# Create namespace
print_step "Creating Kubernetes namespace..."
kubectl apply -f /app/k8s/namespace.yaml
echo ""

# Apply ConfigMap and Secrets
print_step "Applying ConfigMap and Secrets..."
kubectl apply -f /app/k8s/configmap.yaml
kubectl apply -f /app/k8s/secrets.yaml
print_step "ConfigMap and Secrets applied!"
echo ""

# Check if cert-manager is installed
print_step "Checking for cert-manager..."
if ! kubectl get namespace cert-manager &> /dev/null; then
    print_warning "cert-manager not found. Installing..."
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml
    echo "Waiting for cert-manager to be ready..."
    kubectl wait --for=condition=Available --timeout=300s deployment/cert-manager -n cert-manager
    kubectl wait --for=condition=Available --timeout=300s deployment/cert-manager-webhook -n cert-manager
    print_step "cert-manager installed!"
else
    print_step "cert-manager already installed!"
fi
echo ""

# Check if NGINX Ingress Controller is installed
print_step "Checking for NGINX Ingress Controller..."
if ! kubectl get namespace ingress-nginx &> /dev/null; then
    print_warning "NGINX Ingress Controller not found. Installing..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/cloud/deploy.yaml
    echo "Waiting for ingress controller to be ready..."
    sleep 30
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
    print_step "NGINX Ingress Controller installed!"
else
    print_step "NGINX Ingress Controller already installed!"
fi
echo ""

# Apply ClusterIssuer for Let's Encrypt
print_step "Applying cert-manager ClusterIssuer..."
kubectl apply -f /app/k8s/cert-issuer.yaml
echo ""

# Deploy main application
print_step "Deploying main AutoWebIQ application..."
kubectl apply -f /app/k8s/main-deployment.yaml
echo ""

# Deploy workspace template
print_step "Deploying workspace template..."
kubectl apply -f /app/k8s/deployment-template.yaml
kubectl apply -f /app/k8s/service.yaml
kubectl apply -f /app/k8s/ingress.yaml
kubectl apply -f /app/k8s/hpa.yaml
print_step "Workspace infrastructure deployed!"
echo ""

# Wait for deployments to be ready
print_step "Waiting for deployments to be ready..."
echo "This may take a few minutes..."
kubectl wait --for=condition=Available --timeout=300s deployment/autowebiq-main -n autowebiq-workspaces || true
echo ""

# Get Ingress IP
print_step "Getting Ingress LoadBalancer IP..."
echo "Waiting for LoadBalancer IP assignment (this may take 2-3 minutes)..."
for i in {1..30}; do
    INGRESS_IP=$(kubectl get ingress autowebiq-ingress -n autowebiq-workspaces -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    if [ ! -z "$INGRESS_IP" ]; then
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 10
done

if [ -z "$INGRESS_IP" ]; then
    print_warning "LoadBalancer IP not assigned yet. Check manually with:"
    echo "kubectl get ingress -n autowebiq-workspaces"
else
    print_step "LoadBalancer IP: $INGRESS_IP"
    echo ""
    echo "========================================="
    echo "DNS CONFIGURATION REQUIRED"
    echo "========================================="
    echo "Add these DNS records in Cloudflare:"
    echo ""
    echo "Type: A  |  Name: www              |  Content: $INGRESS_IP"
    echo "Type: A  |  Name: api              |  Content: $INGRESS_IP"
    echo "Type: A  |  Name: *.preview        |  Content: $INGRESS_IP"
    echo "Type: A  |  Name: preview          |  Content: $INGRESS_IP"
    echo ""
fi

echo ""
echo "========================================="
echo "DEPLOYMENT SUMMARY"
echo "========================================="
echo ""
print_step "Deployment completed successfully!"
echo ""
echo "Resources created:"
echo "  - Namespace: autowebiq-workspaces"
echo "  - Main application deployment"
echo "  - Workspace template deployment"
echo "  - Services and Ingress"
echo "  - HPA (Horizontal Pod Autoscaler)"
echo "  - SSL certificates (via cert-manager)"
echo ""
echo "Next steps:"
echo "  1. Configure DNS records in Cloudflare (see above)"
echo "  2. Wait 5-10 minutes for SSL certificates to be issued"
echo "  3. Test your deployment:"
echo "     - Main app: https://www.autowebiq.com"
echo "     - API: https://api.autowebiq.com"
echo "     - Preview: https://preview.autowebiq.com"
echo ""
echo "Monitor deployment:"
echo "  kubectl get all -n autowebiq-workspaces"
echo "  kubectl logs -n autowebiq-workspaces <pod-name>"
echo "  kubectl describe ingress -n autowebiq-workspaces"
echo ""
echo "========================================="
