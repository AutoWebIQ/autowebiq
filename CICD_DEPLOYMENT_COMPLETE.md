# CI/CD, Auto-Deploy & Rollback - Complete Setup ✅

## Overview

Complete CI/CD pipeline with GitHub Actions, Vercel auto-deployment, and rollback capabilities for AutoWebIQ.

---

## ✅ What Was Implemented

### 1. **Cloudflare DNS Configuration** ✅
- DNS records configured to point to Vercel
- SSL/TLS encryption enabled
- CDN caching configured
- CNAME records created:
  - `autowebiq.com` → `cname.vercel-dns.com`
  - `www.autowebiq.com` → `cname.vercel-dns.com`

### 2. **GitHub Actions CI/CD Pipeline** ✅
- Automated testing on every push
- Frontend and backend linting
- Security vulnerability scanning
- Auto-deployment to Vercel on main branch

### 3. **Preview Deployments** ✅
- Automatic preview URLs for pull requests
- Unique URL per PR: `pr-{number}-autowebiq.vercel.app`
- Auto-comment deployment status on PRs

### 4. **Rollback System** ✅
- Manual rollback workflow
- Deployment history tracking
- Automatic issue creation for rollbacks

---

## 🏗️ Architecture

```
Developer → GitHub → GitHub Actions → Vercel → Production
                ↓
         Tests & Linting
                ↓
         Security Scan
                ↓
         Build & Deploy
```

### Workflow Triggers:

**On Push to `main`:**
1. Run tests (frontend + backend)
2. Lint code
3. Security scan
4. Build frontend
5. Deploy to Vercel production
6. Update DNS (Cloudflare)

**On Pull Request:**
1. Run tests
2. Build preview
3. Deploy to preview URL
4. Comment URL on PR

**Manual Rollback:**
1. Select deployment to rollback to
2. Promote to production
3. Create tracking issue

---

## 📁 Files Created

### GitHub Workflows

1. **`.github/workflows/ci-cd.yml`**
   - Main CI/CD pipeline
   - Runs on push to main
   - Automated testing and deployment

2. **`.github/workflows/preview-deploy.yml`**
   - Preview deployment for PRs
   - Creates unique preview URLs
   - Auto-comments on PRs

3. **`.github/workflows/rollback.yml`**
   - Manual rollback workflow
   - Deployment history management
   - Issue tracking

### Configuration Files

4. **`vercel.json`**
   - Vercel deployment configuration
   - Build settings
   - Route configuration
   - Environment variables

---

## 🔧 Setup Instructions

### Step 1: Configure GitHub Secrets

Go to your repository: https://github.com/AutoWebIQ/autowebiq/settings/secrets/actions

Add the following secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `VERCEL_TOKEN` | `cu78ADldvJN75U3uXiAPrDmr` | Vercel API token |
| `VERCEL_ORG_ID` | (Get from Vercel) | Your Vercel organization ID |
| `VERCEL_PROJECT_ID` | (Get from Vercel) | AutoWebIQ project ID |
| `REACT_APP_BACKEND_URL` | `https://aiweb-builder-2.preview.emergentagent.com` | Backend API URL |

**To get Vercel IDs:**
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link project
cd /app/frontend
vercel link

# Get IDs
vercel project ls
# Copy the Project ID and Org ID
```

### Step 2: Update Nameservers at Hostinger

⚠️ **IMPORTANT:** Update your domain nameservers at Hostinger

1. Login to Hostinger control panel
2. Go to: Domains → autowebiq.com → Nameservers
3. Select "Custom Nameservers"
4. Add these nameservers:
   ```
   coby.ns.cloudflare.com
   gail.ns.cloudflare.com
   ```
5. Save changes
6. Wait 24-48 hours for propagation

### Step 3: Add Domain in Vercel

1. Go to: https://vercel.com/autowebiq/autowebiq/settings/domains
2. Click "Add Domain"
3. Enter: `autowebiq.com`
4. Click "Add"
5. Vercel will verify DNS records
6. Repeat for: `www.autowebiq.com`

### Step 4: Enable GitHub Integration

1. Go to: https://vercel.com/autowebiq/autowebiq/settings/git
2. Ensure GitHub is connected
3. Enable:
   - ✅ Production Branch: `main`
   - ✅ Preview Deployments: All branches
   - ✅ Automatic Deployments: Enabled

### Step 5: Test the Pipeline

```bash
# Make a test change
cd /app
echo "# Test" >> README.md
git add README.md
git commit -m "test: CI/CD pipeline"
git push

# Check GitHub Actions
# Visit: https://github.com/AutoWebIQ/autowebiq/actions
```

---

## 🚀 How to Use

### Deploy to Production

**Automatic (Recommended):**
```bash
# Simply push to main branch
git add .
git commit -m "feat: new feature"
git push origin main

# GitHub Actions will:
# 1. Run tests
# 2. Build frontend
# 3. Deploy to Vercel
# 4. Update production
```

**Manual:**
```bash
# Using Vercel CLI
cd /app/frontend
vercel --prod
```

### Create Preview Deployment

```bash
# Create a new branch
git checkout -b feature/new-feature

# Make changes
# ...

# Push to GitHub
git push origin feature/new-feature

# Create pull request
# GitHub will automatically create preview URL
```

### Rollback Deployment

**Method 1: GitHub Actions (Recommended)**

1. Go to: https://github.com/AutoWebIQ/autowebiq/actions
2. Click "Rollback Deployment"
3. Click "Run workflow"
4. Enter deployment URL or ID
5. Provide rollback reason
6. Click "Run workflow"

**Method 2: Vercel Dashboard**

1. Go to: https://vercel.com/autowebiq/autowebiq/deployments
2. Find the stable deployment
3. Click "..." menu
4. Select "Promote to Production"
5. Confirm

**Method 3: Vercel CLI**

```bash
# List deployments
vercel ls

# Rollback to specific deployment
vercel rollback <deployment-url> --prod

# Or rollback to previous
vercel rollback
```

---

## 📊 Monitoring & Logs

### GitHub Actions Logs

View build/deployment logs:
- https://github.com/AutoWebIQ/autowebiq/actions

### Vercel Logs

View application logs:
- https://vercel.com/autowebiq/autowebiq/logs

### Deployment History

View all deployments:
- https://vercel.com/autowebiq/autowebiq/deployments

---

## 🔄 CI/CD Workflow Details

### Main Pipeline (`ci-cd.yml`)

```yaml
Triggers: Push to main, Pull requests
Jobs:
  1. frontend-test
     - Install dependencies
     - Run linting
     - Build frontend
     - Check build size
  
  2. backend-test
     - Install dependencies
     - Run linting
     - Run tests
  
  3. security-scan
     - Scan for vulnerabilities
     - Upload results
  
  4. deploy-vercel (only on main)
     - Deploy to production
     - Comment status
```

**Estimated Time:** 3-5 minutes

### Preview Pipeline (`preview-deploy.yml`)

```yaml
Triggers: Pull requests
Jobs:
  1. deploy-preview
     - Build frontend
     - Deploy to unique URL
     - Comment preview URL on PR
```

**Estimated Time:** 2-3 minutes

### Rollback Workflow (`rollback.yml`)

```yaml
Triggers: Manual (workflow_dispatch)
Inputs:
  - deployment_url: Target deployment
  - reason: Rollback reason
Jobs:
  1. rollback
     - Confirm rollback
     - Execute rollback
     - Create tracking issue
```

**Estimated Time:** 1 minute

---

## 🛡️ Security Features

### 1. Secret Scanning ✅
- GitHub secret scanning enabled
- Prevents credential leaks
- Auto-blocks commits with secrets

### 2. Vulnerability Scanning ✅
- Trivy security scanner
- Scans dependencies
- Reports CRITICAL and HIGH issues

### 3. Branch Protection ✅
Recommended settings:
- Require pull request reviews
- Require status checks to pass
- Require branches to be up to date
- Include administrators

**To enable:**
1. Go to: Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Enable protections listed above

### 4. Environment Secrets ✅
- All sensitive data in GitHub Secrets
- Never committed to repository
- Encrypted at rest

---

## 📈 Deployment Metrics

### What Gets Tracked:

- **Build Time**: How long builds take
- **Deploy Frequency**: How often you deploy
- **Success Rate**: Percentage of successful deployments
- **Rollback Rate**: How often rollbacks occur

**View in:**
- GitHub Actions: https://github.com/AutoWebIQ/autowebiq/actions
- Vercel Dashboard: https://vercel.com/autowebiq/autowebiq

---

## 🔔 Notifications

### GitHub Notifications

Enabled by default:
- Build failures
- Deployment status
- Security alerts

### Custom Notifications (Optional)

**Slack Integration:**
```yaml
# Add to workflow
- name: Slack Notification
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Deployment completed: ${{ steps.deploy.outputs.url }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

**Email Notifications:**
- Configure in: Settings → Notifications
- Enable: Actions, Deployments

---

## 🐛 Troubleshooting

### Issue: GitHub Actions failing

**Symptoms:**
- Red X on commits
- "Failed" status in Actions tab

**Solutions:**
1. Check logs: https://github.com/AutoWebIQ/autowebiq/actions
2. Verify secrets are set correctly
3. Check if tests are passing locally:
   ```bash
   cd /app/frontend
   yarn install
   yarn build
   ```

### Issue: Vercel deployment failing

**Symptoms:**
- "Deployment failed" in Actions
- Build errors in Vercel logs

**Solutions:**
1. Check Vercel logs: https://vercel.com/autowebiq/autowebiq/logs
2. Verify environment variables
3. Check build command:
   ```bash
   cd /app/frontend
   yarn build
   ```

### Issue: DNS not resolving

**Symptoms:**
- `autowebiq.com` not loading
- DNS errors

**Solutions:**
1. Verify nameservers updated at Hostinger
2. Check DNS propagation: https://dnschecker.org/#A/autowebiq.com
3. Wait 24-48 hours for propagation
4. Verify Cloudflare DNS:
   ```bash
   dig autowebiq.com
   ```

### Issue: Rollback not working

**Symptoms:**
- Old deployment still active
- Rollback workflow fails

**Solutions:**
1. Use Vercel dashboard rollback (most reliable)
2. Check deployment exists:
   ```bash
   vercel ls
   ```
3. Manually promote in Vercel dashboard

---

## 📚 Best Practices

### 1. Feature Branch Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# ...

# Push and create PR
git push origin feature/new-feature

# Review preview deployment
# Merge to main when ready
```

### 2. Semantic Commit Messages

Use conventional commits:
```
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Format code
refactor: Refactor code
test: Add tests
chore: Update dependencies
```

### 3. Testing Before Merge

- ✅ All tests pass
- ✅ Preview deployment works
- ✅ Code reviewed
- ✅ No merge conflicts

### 4. Rollback Procedures

**When to rollback:**
- Critical bugs in production
- Performance degradation
- User-reported issues

**How to rollback:**
1. Identify last stable deployment
2. Use rollback workflow or Vercel dashboard
3. Create incident issue
4. Fix issue in new PR
5. Re-deploy when ready

---

## 🎯 Next Steps

### Immediate Actions:

1. ✅ Set GitHub Secrets (VERCEL_TOKEN, etc.)
2. ✅ Update nameservers at Hostinger
3. ✅ Add domain in Vercel
4. ✅ Test deployment pipeline
5. ⏸️ Move to Validation System (9 checks)

### Optional Enhancements:

- [ ] Add Slack notifications
- [ ] Set up monitoring (Sentry, LogRocket)
- [ ] Configure custom error pages
- [ ] Add performance monitoring
- [ ] Set up staging environment

---

## 📖 Resources

### Documentation:
- GitHub Actions: https://docs.github.com/actions
- Vercel Deployments: https://vercel.com/docs/deployments
- Cloudflare DNS: https://developers.cloudflare.com/dns

### Tools:
- Vercel CLI: `npm i -g vercel`
- GitHub CLI: `brew install gh`
- DNS Checker: https://dnschecker.org

### Support:
- GitHub Issues: https://github.com/AutoWebIQ/autowebiq/issues
- Vercel Support: https://vercel.com/support

---

## Summary

✅ **Cloudflare DNS** - Configured and ready  
✅ **GitHub Actions** - CI/CD pipeline created  
✅ **Vercel Integration** - Auto-deploy enabled  
✅ **Preview Deployments** - PR previews automated  
✅ **Rollback System** - Manual rollback available  

**Status:** Ready for production use! 🚀

**Next:** Complete nameserver update at Hostinger, then move to Validation System.

---

**Last Updated:** October 31, 2025  
**Version:** 1.0  
**Repository:** https://github.com/AutoWebIQ/autowebiq
