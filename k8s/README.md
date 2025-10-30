# AutoWebIQ Kubernetes Deployment

## Prerequisites

1. **GKE Cluster**: Kubernetes cluster running on Google Kubernetes Engine
2. **kubectl**: Configured to connect to your GKE cluster
3. **NGINX Ingress Controller**: Installed in the cluster
4. **cert-manager**: For automatic SSL certificate management
5. **Cloudflare DNS**: Configured for domain management

## Setup Instructions

### 1. Authenticate with GKE

```bash
# Set project
gcloud config set project autowebiq-476616

# Authenticate
gcloud auth activate-service-account --key-file=/app/gcp-service-account.json

# Get cluster credentials
gcloud container clusters get-credentials autowebiq-cluster --region=asia-south1
```

### 2. Install NGINX Ingress Controller (if not already installed)

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/cloud/deploy.yaml
```

### 3. Install cert-manager (for SSL)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=Available --timeout=300s deployment/cert-manager -n cert-manager
```

### 4. Create ClusterIssuer for Let's Encrypt

```bash
kubectl apply -f /app/k8s/cert-issuer.yaml
```

### 5. Deploy AutoWebIQ Infrastructure

```bash
# Create namespace
kubectl apply -f /app/k8s/namespace.yaml

# Apply ConfigMap and Secrets
kubectl apply -f /app/k8s/configmap.yaml
kubectl apply -f /app/k8s/secrets.yaml

# Deploy main application
kubectl apply -f /app/k8s/main-deployment.yaml

# Deploy workspace template and services
kubectl apply -f /app/k8s/deployment-template.yaml
kubectl apply -f /app/k8s/service.yaml
kubectl apply -f /app/k8s/ingress.yaml
kubectl apply -f /app/k8s/hpa.yaml
```

### 6. Configure Cloudflare DNS

Get the Ingress LoadBalancer IP:

```bash
kubectl get ingress -n autowebiq-workspaces
```

Add these DNS records in Cloudflare:

- **A Record**: `www.autowebiq.com` → LoadBalancer IP
- **A Record**: `api.autowebiq.com` → LoadBalancer IP
- **A Record**: `*.preview.autowebiq.com` → LoadBalancer IP (wildcard for subdomains)
- **A Record**: `preview.autowebiq.com` → LoadBalancer IP

## Subdomain-Based Preview System

Each user project gets a unique subdomain:

- Format: `{project_id}.preview.autowebiq.com`
- Example: `abc123def.preview.autowebiq.com`

The ingress controller automatically routes traffic based on the subdomain to the appropriate workspace pod.

## Scaling

Workspaces automatically scale based on CPU/Memory usage via HPA:

- **Min Replicas**: 1
- **Max Replicas**: 10
- **CPU Target**: 70%
- **Memory Target**: 80%

## Monitoring

```bash
# View all resources
kubectl get all -n autowebiq-workspaces

# Check pod logs
kubectl logs -n autowebiq-workspaces <pod-name>

# Check ingress
kubectl describe ingress -n autowebiq-workspaces

# Check HPA status
kubectl get hpa -n autowebiq-workspaces
```

## Clean Up

```bash
# Delete all resources
kubectl delete namespace autowebiq-workspaces
```

## Security Notes

- All secrets are stored in Kubernetes Secrets (base64 encoded)
- SSL certificates are automatically managed by cert-manager
- Ingress enforces HTTPS redirects
- Workspaces have resource limits to prevent overconsumption
