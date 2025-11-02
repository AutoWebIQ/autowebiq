# AutoWebIQ GKE Deployment Guide

## 🚀 Production Deployment to autowebiq.com

This guide will help you deploy AutoWebIQ to Google Kubernetes Engine (GKE) with:
- Auto-scaling
- Load balancing
- SSL certificates (Let's Encrypt)
- High availability
- Production-grade infrastructure

---

## Prerequisites

1. **GCP Account** with billing enabled
2. **GKE Cluster** (autowebiq-cluster in asia-south1) ✅ Already configured
3. **Docker Hub Account** ✅ Already configured
4. **Domain** (autowebiq.com) ✅ Already owned
5. **gcloud CLI** installed
6. **kubectl** installed
7. **docker** installed

---

## Step-by-Step Deployment

### 1. Prepare Environment

```bash
# Make scripts executable
chmod +x deploy-gke.sh update-deployment.sh rollback.sh

# Verify GCP configuration
gcloud config list
gcloud container clusters list
```

### 2. Run Deployment Script

```bash
# This will:
# - Build Docker images
# - Push to Docker Hub
# - Deploy to GKE
# - Set up auto-scaling
# - Configure SSL
# - Create ingress

./deploy-gke.sh
```

**This takes approximately 10-15 minutes.**

### 3. Get LoadBalancer IP

The script will output the LoadBalancer IP. If not, run:

```bash
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

Look for `EXTERNAL-IP`.

### 4. Configure DNS

Update your DNS records (Cloudflare or your DNS provider):

```
Type  Name              Value              TTL
A     autowebiq.com     <LOADBALANCER_IP>  Auto
A     www               <LOADBALANCER_IP>  Auto
A     api               <LOADBALANCER_IP>  Auto
```

**Using Cloudflare:**
- Go to DNS settings
- Add/Update A records
- Set to "DNS only" (not proxied initially)
- After SSL is working, you can enable proxy

### 5. Wait for SSL Certificates

Let's Encrypt will automatically issue SSL certificates within 5-10 minutes.

Check cert status:
```bash
kubectl get certificate -n autowebiq
kubectl describe certificate autowebiq-tls -n autowebiq
```

### 6. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n autowebiq

# Check services
kubectl get svc -n autowebiq

# Check ingress
kubectl get ingress -n autowebiq

# View backend logs
kubectl logs -f deployment/autowebiq-backend -n autowebiq

# View frontend logs
kubectl logs -f deployment/autowebiq-frontend -n autowebiq
```

### 7. Test Your Application

Once DNS propagates (1-5 minutes):

```bash
# Test frontend
curl -I https://autowebiq.com

# Test backend
curl https://autowebiq.com/api/health

# Test API endpoint
curl https://api.autowebiq.com/health
```

Open in browser:
- https://autowebiq.com
- https://www.autowebiq.com
- https://api.autowebiq.com/docs

---

## Updating Your Application

When you make code changes:

```bash
# Build new images and deploy
./update-deployment.sh
```

This performs a **rolling update** with zero downtime.

---

## Rolling Back

If something goes wrong:

```bash
./rollback.sh
```

This reverts to the previous version.

---

## Monitoring

### View Logs
```bash
# Backend logs
kubectl logs -f -l app=autowebiq-backend -n autowebiq

# Frontend logs
kubectl logs -f -l app=autowebiq-frontend -n autowebiq

# MongoDB logs
kubectl logs -f -l app=autowebiq-mongodb -n autowebiq
```

### Check Pod Status
```bash
kubectl get pods -n autowebiq -w
```

### Check Resource Usage
```bash
kubectl top pods -n autowebiq
kubectl top nodes
```

### Check Auto-scaling
```bash
kubectl get hpa -n autowebiq
```

---

## Architecture

```
                    Internet
                       |
                       v
               Google Cloud LoadBalancer
                       |
                       v
              Nginx Ingress Controller
                       |
         +-------------+-------------+
         |                           |
         v                           v
  Frontend Service            Backend Service
  (2-5 replicas)             (3-10 replicas)
         |                           |
         +-------------+-------------+
                       |
           +-----------+-----------+
           |                       |
           v                       v
      MongoDB Service         Redis Service
      (Persistent)            (In-Memory)
```

---

## Scaling

### Manual Scaling
```bash
# Scale backend
kubectl scale deployment autowebiq-backend --replicas=5 -n autowebiq

# Scale frontend
kubectl scale deployment autowebiq-frontend --replicas=3 -n autowebiq
```

### Auto-scaling (Already Configured)
- Backend: 3-10 replicas (based on CPU/memory)
- Frontend: 2-5 replicas (based on CPU)

---

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n autowebiq
kubectl logs <pod-name> -n autowebiq
```

### Ingress not working
```bash
kubectl describe ingress autowebiq-ingress -n autowebiq
kubectl get svc -n ingress-nginx
```

### SSL certificate issues
```bash
kubectl describe certificate autowebiq-tls -n autowebiq
kubectl describe challenge -n autowebiq
kubectl logs -n cert-manager deployment/cert-manager
```

### Database connection issues
```bash
# Test MongoDB connection
kubectl exec -it deployment/autowebiq-backend -n autowebiq -- python -c "from pymongo import MongoClient; print(MongoClient('mongodb://autowebiq-mongodb:27017').server_info())"

# Test Redis connection
kubectl exec -it deployment/autowebiq-backend -n autowebiq -- redis-cli -h autowebiq-redis ping
```

---

## Cost Optimization

### Current Resources:
- **Backend**: 3-10 pods × 512MB RAM = ~1.5-5GB
- **Frontend**: 2-5 pods × 256MB RAM = ~0.5-1.25GB
- **MongoDB**: 1 pod × 2GB RAM = 2GB
- **Redis**: 1 pod × 512MB RAM = 0.5GB

**Total**: ~4.5-8.75GB RAM + CPU

**Estimated Cost**: ~$150-300/month (GKE + LoadBalancer)

### To Reduce Costs:
1. Use preemptible nodes
2. Reduce min replicas
3. Use smaller instance types
4. Use GKE Autopilot

---

## Security Checklist

- ✅ SSL/TLS encryption (Let's Encrypt)
- ✅ Secrets management (Kubernetes Secrets)
- ✅ Network policies (pod isolation)
- ✅ Resource limits (prevent resource exhaustion)
- ✅ Health checks (automatic recovery)
- ✅ Rolling updates (zero downtime)
- ⚠️ Setup firewall rules (recommended)
- ⚠️ Enable Pod Security Policies (recommended)
- ⚠️ Regular backups (setup recommended)

---

## Backup & Disaster Recovery

### Backup MongoDB
```bash
# Create backup
kubectl exec -it deployment/autowebiq-mongodb -n autowebiq -- mongodump --archive > backup.archive

# Restore backup
kubectl exec -i deployment/autowebiq-mongodb -n autowebiq -- mongorestore --archive < backup.archive
```

### Backup Entire Cluster
```bash
# Export all resources
kubectl get all -n autowebiq -o yaml > autowebiq-backup.yaml
```

---

## Support

If you encounter issues:

1. Check logs: `kubectl logs -f deployment/autowebiq-backend -n autowebiq`
2. Check pod status: `kubectl get pods -n autowebiq`
3. Check ingress: `kubectl describe ingress autowebiq-ingress -n autowebiq`
4. Check events: `kubectl get events -n autowebiq --sort-by='.lastTimestamp'`

---

## Next Steps

1. ✅ Deploy to GKE
2. ✅ Configure DNS
3. ✅ Verify SSL
4. ⚠️ Set up monitoring (Cloud Monitoring)
5. ⚠️ Set up alerting (Cloud Alerting)
6. ⚠️ Configure backups (automated)
7. ⚠️ Set up CI/CD (GitHub Actions)
8. ⚠️ Performance testing
9. ⚠️ Load testing
10. ⚠️ Security audit

---

🎉 **Your AutoWebIQ platform is now production-ready on GKE!**