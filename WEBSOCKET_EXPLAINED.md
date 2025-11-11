# 🔌 WebSocket Explained - Real-Time Communication in AutoWebIQ

## 📖 What is WebSocket?

### Simple Explanation:

**WebSocket** = A **permanent phone line** ☎️ between your browser and server

**Regular HTTP** = Sending **letters** 📬 (one question → one answer → done)

### Real-World Analogy:

**🏗️ Building a House (Website Generation):**

**Without WebSocket (HTTP only):**
- You: "Hey, are you done yet?" 📬
- Builder: "No, 10% done" 📬
- *5 seconds later*
- You: "Are you done yet?" 📬  
- Builder: "No, 20% done" 📬
- *5 seconds later*
- You: "Are you done yet?" 📬
- Builder: "No, 30% done" 📬

**With WebSocket:**
- You: "Call me when you make progress" ☎️ *(connection stays open)*
- Builder: "10% done!" ☎️ *(instant update)*
- Builder: "20% done!" ☎️ *(instant update)*
- Builder: "50% done!" ☎️ *(instant update)*
- Builder: "✅ Done!" ☎️ *(instant update)*

---

## 🎯 Why AutoWebIQ Uses WebSocket

### During Website Generation:
1. **AI Agents work** (Planner, Frontend, Image, Testing)
2. **Each agent sends updates** in real-time
3. **You see progress live:**
   - "🧠 Planner Agent: Analyzing requirements... 10%"
   - "🎨 Frontend Agent: Generating HTML... 40%"
   - "🖼️ Image Agent: Processing images... 60%"
   - "✅ Build Complete!"

### Without WebSocket:
- You'd see: "Building..." 🔄 *(spinning forever)*
- No progress updates
- No idea what's happening
- Poor user experience

---

## ❌ Common WebSocket Issues & Solutions

### Issue 1: "WebSocket trying to connect but disconnecting"

**What You're Seeing:**
```
WebSocket: Connecting to ws://...
WebSocket: Connected
WebSocket: Closed 1006
WebSocket: Will attempt to reconnect in 3s...
```

**What This Means:**
- Connection **starts** successfully ✅
- But **immediately closes** with error code 1006 ❌
- Frontend tries to reconnect every 3 seconds 🔄

**Common Causes:**

#### 1. **Backend Not Running** 🔴
```bash
# Check if backend is running
sudo supervisorctl status backend

# Should show: RUNNING
# If not: sudo supervisorctl restart backend
```

#### 2. **Wrong URL Configuration** 🔴
```javascript
// frontend/.env should have:
REACT_APP_BACKEND_URL=https://aiweb-builder-2.preview.emergentagent.com

// WebSocket automatically converts:
// https → wss (secure websocket)
// http → ws (regular websocket)
```

#### 3. **Nginx/Proxy Timeout** 🔴
WebSocket connections can timeout if the proxy doesn't support long-lived connections.

**Solution:**
```nginx
# Nginx config needs:
proxy_read_timeout 3600;
proxy_send_timeout 3600;
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

#### 4. **Backend Error** 🔴
```bash
# Check backend logs
tail -f /var/log/supervisor/backend.err.log

# Look for WebSocket errors
```

#### 5. **Missing PostgreSQL Data** 🔴 **(MOST LIKELY RIGHT NOW)**

After our MongoDB → PostgreSQL migration, the backend might be trying to query MongoDB for user/project data during WebSocket authentication!

**Check this:**
```python
# In routes_v2.py line 95-101
if token:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
    except:
        pass  # Silently fails!
```

If JWT decode fails or database query fails, WebSocket still connects but might not work properly.

---

## 🔧 How to Fix WebSocket Disconnections

### Step 1: Check Backend Status
```bash
sudo supervisorctl status backend
# Should show: RUNNING

# If not running:
sudo supervisorctl restart backend

# Check logs:
tail -f /var/log/supervisor/backend.err.log
```

### Step 2: Verify Backend Health
```bash
curl http://localhost:8001/api/health
# Should return: {"status":"healthy",...}
```

### Step 3: Test WebSocket Endpoint
```bash
# Check if WebSocket endpoint exists
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: test" \
  http://localhost:8001/api/v2/ws/build/test-project-id?token=test

# Should return 101 Switching Protocols (not 404)
```

### Step 4: Check Frontend Logs
```javascript
// Open browser console (F12)
// Look for WebSocket messages:
WebSocket: Connecting to ws://...
WebSocket: Connected  ✅
// OR
WebSocket: Error     ❌
WebSocket: Closed 1006 ❌
```

### Step 5: Check Token
```javascript
// In browser console:
console.log(localStorage.getItem('token'));

// Should show a JWT token
// If null or undefined, login again
```

---

## 📊 WebSocket Connection Lifecycle

```
1. Frontend: "Let me connect to ws://server/build/123?token=xyz"
   ↓
2. Server: "OK, upgrading to WebSocket (101 Switching Protocols)"
   ↓
3. Frontend: onopen() → "Connected!"  
   ↓
4. Server: Sends → {"type":"connection","status":"connected"}
   ↓
5. Frontend: Receives → Shows "WebSocket Connected" ✅
   ↓
6. [Connection stays open for real-time updates]
   ↓
7. Frontend: Sends ping every 30s → "ping"
   Server: Responds → {"type":"pong"}
   ↓
8. Build starts → Server sends:
   - {"type":"agent_message","agent":"planner","progress":10}
   - {"type":"agent_message","agent":"frontend","progress":40}
   - {"type":"build_complete","result":{...}}
   ↓
9. Frontend: onclose() → "Disconnected"
```

---

## 🐛 Debugging WebSocket Issues

### Enable Detailed Logging:

**Frontend (Browser Console):**
```javascript
// Add to Workspace.js
console.log('WebSocket Status:', connectionStatus);
console.log('Last Message:', lastMessage);
```

**Backend (server.py):**
```python
# Already has logging:
print(f"✅ WebSocket connected: project={project_id}")
print(f"🔌 WebSocket disconnected: project={project_id}")
print(f"WebSocket error: {e}")
```

### Check Connection in Browser:
1. Open **DevTools (F12)**
2. Go to **Network** tab
3. Filter by **WS** (WebSocket)
4. Click on the WebSocket connection
5. See:
   - Status: 101 (good) or other (bad)
   - Messages tab (see all sent/received messages)
   - Timing tab (see when it connected/disconnected)

---

## ✅ Expected Behavior (Working WebSocket)

**Browser Console Output:**
```
WebSocket: Connecting to wss://webgen-platform-4.preview.emergentagent.com/api/v2/ws/build/abc123?token=...
WebSocket: Connected
WebSocket: Message received {type: 'connection', status: 'connected'}
WebSocket: Message received {type: 'agent_message', agent: 'planner', progress: 10}
WebSocket: Message received {type: 'agent_message', agent: 'frontend', progress: 40}
WebSocket: Message received {type: 'build_complete', result: {...}}
```

**UI Shows:**
```
🟢 WebSocket: Connected

Chat Messages:
🧠 Planner Agent: Analyzing requirements... 10%
🎨 Frontend Agent: Generating HTML... 40%
🖼️ Image Agent: Processing images... 60%
✅ Build Complete! Your website is ready.
```

---

## ❌ Current Issue (After MongoDB Migration)

**Problem:** WebSocket connects but disconnects immediately

**Why:** Backend routes might still have MongoDB code that fails silently

**Evidence:**
```bash
# Check routes_v2.py line 82-131
# WebSocket endpoint exists ✅
# But authentication/database queries might fail ❌
```

**Solution:**
1. Verify all database queries in routes_v2.py use PostgreSQL
2. Check JWT token is valid
3. Ensure user exists in PostgreSQL database
4. Test with demo@test.com account

---

## 🔍 Quick Diagnostic Checklist

- [ ] Backend is running (`supervisorctl status backend`)
- [ ] Backend health check passes (`curl localhost:8001/api/health`)
- [ ] Frontend env has correct URL (`.env` file)
- [ ] JWT token exists (`localStorage.getItem('token')`)
- [ ] User is logged in (check /api/auth/me)
- [ ] Project ID is valid (check /api/projects)
- [ ] No errors in backend logs (`tail -f backend.err.log`)
- [ ] No errors in browser console (F12)
- [ ] WebSocket URL is correct (ws:// or wss://)
- [ ] Proxy supports WebSocket (Upgrade header)

---

## 🎯 Summary

**WebSocket = Real-time phone line ☎️**
- Keeps connection open
- Instant updates both ways
- Used for live build progress

**Why Disconnecting:**
- Most likely: Backend database queries failing after MongoDB removal
- Check: Backend logs, JWT token, user authentication
- Fix: Ensure all routes use PostgreSQL correctly

**How to Fix:**
1. Check backend logs
2. Verify authentication works
3. Test with valid project/user
4. Ensure PostgreSQL migration is complete

---

**Next Steps:**
1. Run backend testing to verify all endpoints work
2. Check WebSocket connection with valid credentials
3. Monitor backend logs for errors
4. Test with demo account (demo@test.com)

