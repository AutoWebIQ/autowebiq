# 🔒 SSL Setup Guide for AutoWebIQ

## Why SSL Failed?

Let's Encrypt tried to verify you own `autowebiq.com` but it couldn't reach your server.

**The Problem:**
- Your server IP: `35.184.53.215`
- DNS is pointing to: `34.57.15.54` (different server!)

## What You Need to Do

### Step 1: Fix Your DNS Settings

Go to where you bought your domain (like GoDaddy, Namecheap, Cloudflare, etc.) and:

1. **Find DNS settings** for `autowebiq.com`
2. **Update A record** to point to: `35.184.53.215`
3. **Update www A record** to also point to: `35.184.53.215`

**Example DNS settings:**
```
Type    Name    Value              TTL
A       @       35.184.53.215      3600
A       www     35.184.53.215      3600
```

**Wait 5-10 minutes** for DNS to update worldwide.

### Step 2: Verify DNS is Correct

From your computer, run:
```bash
nslookup autowebiq.com
```

You should see: `35.184.53.215`

Or visit this website: https://dnschecker.org/#A/autowebiq.com
- It should show `35.184.53.215` globally

### Step 3: Run SSL Command Again

Once DNS is correct, SSH back to your server and run:

```bash
certbot --nginx -d autowebiq.com -d www.autowebiq.com --non-interactive --agree-tos --email admin@autowebiq.com --redirect
```

### Step 4: Update Environment Files

After SSL is installed successfully:

```bash
# 1. Stop services
sudo supervisorctl stop all

# 2. Update frontend .env
nano /app/frontend/.env
# Change: REACT_APP_BACKEND_URL=https://autowebiq.com (add https)

# 3. Rebuild frontend
cd /app/frontend
rm -rf build
yarn build

# 4. Restart all services
sudo supervisorctl start all
```

### Step 5: Test Your Site

Visit: `https://autowebiq.com` (with HTTPS)

You should see:
- 🔒 Lock icon in browser
- No security warnings
- Login should work perfectly!

## Current Status

✅ Nginx configured
✅ Certbot installed  
✅ SSL verification directory created
⚠️ **DNS needs to point to: 35.184.53.215**

## Need Help?

If you're not sure how to update DNS:
1. Tell me your domain registrar (where you bought the domain)
2. I can give you specific instructions

Common registrars:
- GoDaddy
- Namecheap
- Cloudflare
- Google Domains
- HostGator

## Alternative: Use Cloudflare (Easier!)

If your domain is with Cloudflare:
1. Go to Cloudflare dashboard
2. Select autowebiq.com
3. DNS → Edit A records
4. Point @ and www to: `35.184.53.215`
5. Turn on "Proxy status" (orange cloud) for free SSL
6. Done! Cloudflare handles SSL for you.

## Quick Check Command

To see if DNS is fixed, run this on your server:
```bash
curl -I http://autowebiq.com/.well-known/acme-challenge/test
```

Should return 404 (not found) - that's GOOD
Should NOT return HTML - that means it's still going to React app
