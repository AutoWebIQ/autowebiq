# AutoWebIQ: Preview vs Production Environment Differences

## Overview
This document explains the key differences between the preview environment (Emergent platform) and production deployment on autowebiq.com.

## Environment Configuration

### Preview Environment (Emergent)
- **Domain**: `multiagent-web.preview.emergentagent.com`
- **Backend URL**: Uses Emergent's preview infrastructure
- **Services**: Managed by Emergent's Kubernetes cluster
- **SSL**: Automatically provided by Emergent
- **Nginx**: Managed by Emergent

### Production Environment (autowebiq.com)
- **Domain**: `autowebiq.com`
- **Backend URL**: `https://autowebiq.com/api`
- **Services**: Self-hosted on your server
- **SSL**: Requires manual setup (Let's Encrypt)
- **Nginx**: Self-managed reverse proxy

## Key Differences That Could Affect Functionality

### 1. URL Configuration

**Preview:**
```
Backend: https://multiagent-web.preview.emergentagent.com/api
Frontend: https://multiagent-web.preview.emergentagent.com
```

**Production:**
```
Backend: https://autowebiq.com/api
Frontend: https://autowebiq.com
```

**Fixed:** ✅ Frontend .env updated to use `https://autowebiq.com`

### 2. OAuth Callback URLs

**Services That Need Callback URL Updates:**

#### GitHub OAuth
- **Preview**: `https://api.autowebiq.com/auth/github/callback`
- **Production**: `https://autowebiq.com/api/auth/github/callback`
- **Fixed**: ✅ Updated in backend .env

#### Firebase Authentication
- **Authorized Domains**: Must include `autowebiq.com`
- **Configuration**: Firebase console settings
- **Status**: ⚠️ Needs verification in Firebase Console

**Action Required:**
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project: `autowebiq`
3. Authentication → Settings → Authorized domains
4. Add: `autowebiq.com` (if not already present)

#### Google OAuth (if used)
- **Authorized redirect URIs**: Must include your production domain
- **Configuration**: Google Cloud Console
- **Status**: ⚠️ Needs verification

### 3. CORS Configuration

**Backend CORS Origins:**
```python
# Currently configured:
CORS_ORIGINS=https://autowebiq.com,https://www.autowebiq.com
```

**Status**: ✅ Correctly configured for production

### 4. Trusted Host Middleware

**Preview**: Not restricted (development mode)

**Production**: Enforces allowed hosts
```python
allowed_hosts = [
    'autowebiq.com',
    'www.autowebiq.com',
    'api.autowebiq.com',  # Note: This subdomain doesn't exist
    '*.autowebiq.com'
]
```

**Status**: ✅ Configured but `api.autowebiq.com` is not in use

### 5. External Service Integrations

#### Razorpay
- **API Keys**: Using live keys (`rzp_live_...`)
- **Webhook URL**: May need update if using webhooks
- **Status**: ✅ Live keys configured

#### Cloudinary
- **Configuration**: Independent of domain
- **Status**: ✅ No changes needed

#### MongoDB
- **Preview**: May use Emergent's MongoDB or external
- **Production**: Using local MongoDB (`mongodb://localhost:27017`)
- **Status**: ✅ Configured for local MongoDB

### 6. SSL/HTTPS

**Preview**: Automatically provided by Emergent

**Production**: Currently HTTP only
- **Current**: `http://autowebiq.com`
- **Required**: Setup Let's Encrypt for `https://autowebiq.com`
- **Status**: ⚠️ **CRITICAL - Needs SSL certificate**

**Action Required:**
```bash
# Install certbot
apt-get update
apt-get install certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d autowebiq.com -d www.autowebiq.com

# Auto-renewal is configured by certbot
```

After SSL setup, update:
- Frontend .env: `REACT_APP_BACKEND_URL=https://autowebiq.com`
- Backend .env: `BACKEND_URL=https://autowebiq.com`

### 7. WebSocket Connections

**Preview**: WSS (secure WebSocket) available

**Production**: Currently WS only (no SSL)
- **Current**: `ws://autowebiq.com`
- **After SSL**: `wss://autowebiq.com`

**Services Using WebSockets:**
- Terminal component
- Live build updates
- Code editor collaboration

**Status**: ⚠️ Will work after SSL setup

### 8. Service Discovery

**Preview**: Kubernetes service discovery

**Production**: Direct connection via localhost
- Backend → MongoDB: `localhost:27017`
- Nginx → Backend: `localhost:8001`
- Nginx → Frontend: `localhost:3000`

**Status**: ✅ Correctly configured

### 9. Environment Variables Summary

**Environment-Specific Variables:**

| Variable | Preview | Production |
|----------|---------|------------|
| ENVIRONMENT | preview | production |
| BACKEND_URL | preview.emergentagent.com | https://autowebiq.com |
| FRONTEND_URL | preview.emergentagent.com | https://autowebiq.com |
| GITHUB_CALLBACK_URL | api.autowebiq.com/... | autowebiq.com/api/... |

**Status**: ✅ All updated for production

## Testing Checklist

### Basic Functionality ✅
- [x] Landing page loads
- [x] Backend health check works
- [x] API endpoints accessible

### Authentication
- [x] Email/password login
- [x] Email/password registration
- [ ] Google OAuth (needs domain authorization)
- [ ] GitHub OAuth (callback URL updated, needs testing)
- [ ] Firebase Auth (needs domain authorization)

### External Services
- [x] MongoDB connection
- [x] Cloudinary image upload
- [ ] Razorpay payments (needs testing with live keys)
- [ ] GitHub integration (needs testing)

### Security
- [x] CORS configured
- [x] Trusted hosts configured
- [ ] SSL/HTTPS (needs setup)
- [ ] Security headers (configured)

## Known Limitations (Current)

1. **HTTP Only**: No SSL certificate installed
2. **OAuth Providers**: May need callback URL updates in provider consoles
3. **WebSocket**: Using WS instead of WSS (until SSL)
4. **Firebase Domains**: Need to authorize production domain

## Action Items

### High Priority
1. ✅ Configure nginx reverse proxy
2. ✅ Update backend URL in frontend
3. ✅ Fix GitHub callback URL
4. ⚠️ **Install SSL certificate** (certbot)
5. ⚠️ Update Firebase authorized domains

### Medium Priority
6. Test all OAuth providers on production
7. Test Razorpay payment flow with live keys
8. Configure monitoring/logging for production

### Low Priority
9. Setup automatic SSL renewal verification
10. Configure CDN if needed
11. Setup production backups

## Troubleshooting

### Issue: "Network Error" on login
**Cause**: Frontend trying to connect to wrong backend URL
**Solution**: ✅ Fixed - updated to https://autowebiq.com

### Issue: OAuth callback fails
**Cause**: Callback URL not matching provider configuration
**Solution**: ✅ Updated GitHub URL, needs verification in GitHub settings

### Issue: "Connection refused" 
**Cause**: Service not running or nginx not configured
**Solution**: ✅ Fixed - nginx reverse proxy configured

### Issue: SSL/HTTPS required errors
**Cause**: No SSL certificate installed
**Solution**: ⚠️ Pending - needs certbot installation

## Conclusion

**Current Status**: 
- ✅ Core infrastructure configured
- ✅ Backend and frontend working
- ✅ Basic authentication functional
- ⚠️ SSL needed for production-ready deployment
- ⚠️ OAuth providers need verification

**Next Critical Step**: Install SSL certificate using Let's Encrypt
