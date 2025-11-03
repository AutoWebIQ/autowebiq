# AutoWebIQ Production Deployment Guide
## Domain: autowebiq.com

---

## 🚀 Pre-Deployment Checklist

### 1. Environment Variables
- ✅ Copy `/app/.env.production` to `/app/backend/.env`
- ✅ Copy `/app/frontend/.env.production` to `/app/frontend/.env`
- ✅ Update `REACT_APP_BACKEND_URL` in frontend .env
- ✅ Update `CORS_ORIGINS` in backend .env

### 2. Database Configuration
- ✅ MongoDB Production: `mongodb+srv://autowebiq:Saifiboy@1@cluster0.uqhm5rw.mongodb.net/`
- ✅ Database name: `autowebiq_production`
- ✅ Create indexes for performance
- ✅ Backup current data

### 3. Domain Configuration
- ✅ Point `autowebiq.com` → Your server IP
- ✅ Point `www.autowebiq.com` → Your server IP
- ✅ Point `api.autowebiq.com` → Your server IP (backend)
- ✅ Configure SSL certificates (Let's Encrypt)

### 4. Cloudflare Setup
- ✅ Add autowebiq.com to Cloudflare
- ✅ Enable SSL/TLS (Full or Full Strict)
- ✅ Enable HTTP/2 and HTTP/3
- ✅ Enable Auto Minify (JS, CSS, HTML)
- ✅ Enable Brotli compression
- ✅ Configure DNS:
  - `A` record: `@` → Server IP
  - `A` record: `www` → Server IP
  - `A` record: `api` → Server IP
  - `CNAME` record: `*.preview` → `preview.autowebiq.com`

### 5. Security Hardening
- ✅ Change JWT_SECRET to production value
- ✅ Enable HTTPS only
- ✅ Configure secure cookies
- ✅ Set strict CORS origins
- ✅ Enable rate limiting
- ✅ Configure firewall rules

---

## 📦 Deployment Steps

### Option A: Docker Deployment (Recommended)

```bash
# 1. Build images
cd /app
docker-compose -f docker-compose.prod.yml build

# 2. Start services
docker-compose -f docker-compose.prod.yml up -d

# 3. Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Option B: Kubernetes/GKE Deployment

```bash
# 1. Configure kubectl
gcloud container clusters get-credentials autowebiq-cluster --region asia-south1

# 2. Update secrets
kubectl create secret generic autowebiq-secrets --from-env-file=/app/.env.production

# 3. Deploy
kubectl apply -f /app/k8s/production/

# 4. Check status
kubectl get pods -n autowebiq-production
kubectl get services -n autowebiq-production
```

### Option C: Manual Deployment

```bash
# Backend
cd /app/backend
source venv/bin/activate
pip install -r requirements.txt
cp /app/.env.production .env
gunicorn server:app -w 4 -b 0.0.0.0:8001 --daemon

# Frontend
cd /app/frontend
yarn install
cp /app/frontend/.env.production .env
yarn build
# Serve build/ folder with Nginx or similar
```

---

## 🔧 Nginx Configuration

### Main Site (autowebiq.com)
```nginx
server {
    listen 80;
    server_name autowebiq.com www.autowebiq.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name autowebiq.com www.autowebiq.com;

    ssl_certificate /etc/letsencrypt/live/autowebiq.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/autowebiq.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    root /app/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### API (api.autowebiq.com)
```nginx
server {
    listen 80;
    server_name api.autowebiq.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.autowebiq.com;

    ssl_certificate /etc/letsencrypt/live/autowebiq.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/autowebiq.com/privkey.pem;

    # Backend API
    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## 🗄️ Database Migration

```bash
# 1. Backup current database
mongodump --uri="mongodb://localhost:27017/autowebiq_db" --out=/backup/autowebiq_backup

# 2. Restore to production
mongorestore --uri="mongodb+srv://autowebiq:PASSWORD@cluster0.uqhm5rw.mongodb.net/autowebiq_production" /backup/autowebiq_backup/autowebiq_db

# 3. Create indexes
mongo mongodb+srv://... <<EOF
use autowebiq_production
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "id": 1 }, { unique: true })
db.projects.createIndex({ "user_id": 1 })
db.projects.createIndex({ "id": 1 }, { unique: true })
db.credit_transactions.createIndex({ "user_id": 1 })
EOF
```

---

## 📊 Monitoring & Logging

### 1. Application Logs
```bash
# Backend logs
tail -f /var/log/autowebiq/backend.log

# Frontend access logs
tail -f /var/log/nginx/autowebiq_access.log

# Error logs
tail -f /var/log/nginx/autowebiq_error.log
```

### 2. Health Checks
- Backend: `https://api.autowebiq.com/api/health`
- Frontend: `https://autowebiq.com`

### 3. Monitoring Setup
- Configure PostHog analytics
- Setup error tracking (Sentry)
- Configure uptime monitoring
- Setup performance monitoring

---

## 🔄 Post-Deployment

### 1. Verify Services
```bash
# Check backend
curl https://api.autowebiq.com/api/health

# Check frontend
curl -I https://autowebiq.com

# Test authentication
curl -X POST https://api.autowebiq.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"Demo123456"}'
```

### 2. Test Critical Features
- ✅ Landing page loads
- ✅ User registration works
- ✅ User login works
- ✅ Project creation works
- ✅ Website generation works
- ✅ Deployment works
- ✅ Subscription payment works
- ✅ Agent status displays

### 3. Performance Testing
```bash
# Load testing
ab -n 1000 -c 10 https://autowebiq.com/

# API testing
ab -n 100 -c 5 https://api.autowebiq.com/api/health
```

### 4. SSL Verification
```bash
# Check SSL
ssl-checker https://autowebiq.com
ssl-checker https://api.autowebiq.com
```

---

## 🚨 Troubleshooting

### Issue: Backend not starting
```bash
# Check logs
tail -100 /var/log/supervisor/backend.err.log

# Check MongoDB connection
mongo mongodb+srv://... --eval "db.adminCommand('ping')"

# Restart backend
sudo supervisorctl restart backend
```

### Issue: Frontend 404 errors
```bash
# Check Nginx config
nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Check frontend build
ls -la /app/frontend/build/
```

### Issue: CORS errors
- Update `CORS_ORIGINS` in backend .env
- Include: `https://autowebiq.com,https://www.autowebiq.com`
- Restart backend

### Issue: SSL certificate errors
```bash
# Renew Let's Encrypt
sudo certbot renew

# Check expiry
sudo certbot certificates
```

---

## 📈 Performance Optimization

### 1. Frontend
- ✅ Enable Gzip/Brotli compression
- ✅ Minify JS/CSS
- ✅ Optimize images
- ✅ Enable browser caching
- ✅ Use CDN (Cloudflare)

### 2. Backend
- ✅ Enable Redis caching
- ✅ Optimize database queries
- ✅ Use connection pooling
- ✅ Enable API rate limiting

### 3. Database
- ✅ Create appropriate indexes
- ✅ Enable query caching
- ✅ Regular backups
- ✅ Monitor slow queries

---

## 🔐 Security Checklist

- ✅ All secrets in environment variables
- ✅ HTTPS everywhere
- ✅ Secure cookies enabled
- ✅ CORS properly configured
- ✅ Rate limiting enabled
- ✅ JWT tokens secure
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CSRF protection
- ✅ Security headers set
- ✅ Regular security updates

---

## 📞 Support

If you encounter issues:
1. Check logs first
2. Verify environment variables
3. Test database connection
4. Check Nginx configuration
5. Verify SSL certificates

---

**Status:** Ready for Production ✅  
**Last Updated:** February 11, 2025
