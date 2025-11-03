# PostgreSQL and Redis Installation Complete ✅

## Installation Summary

Successfully installed and configured PostgreSQL 15 and Redis 7.0 for AutoWebIQ.

---

## What Was Installed

### 1. PostgreSQL 15 ✅
- **Version**: PostgreSQL 15.14 (Debian)
- **Location**: `/usr/lib/postgresql/15/bin/postgres`
- **Data Directory**: `/var/lib/postgresql/15/main`
- **Config File**: `/etc/postgresql/15/main/postgresql.conf`
- **Port**: 5432 (localhost)

### 2. Redis 7.0 ✅
- **Version**: Redis 7.0.15
- **Location**: `/usr/bin/redis-server`
- **Config File**: `/etc/redis/redis.conf`
- **Port**: 6379 (localhost)

---

## Database Configuration

### PostgreSQL Database

**Database Details:**
- **Database Name**: `autowebiq_db`
- **User**: `autowebiq`
- **Password**: `autowebiq_secure_pass`
- **Connection String**: `postgresql+asyncpg://autowebiq:autowebiq_secure_pass@localhost/autowebiq_db`

**Tables Created:**
- `users` - User accounts
- `projects` - User projects
- `project_messages` - Chat history
- `credit_transactions` - Credit operations
- `user_sessions` - Session management

### Redis Configuration

**Connection:**
- **Host**: localhost
- **Port**: 6379
- **Database**: 0
- **Connection String**: `redis://localhost:6379/0`

**Used For:**
- Celery message broker
- Task result backend
- Caching (templates, components, user data)
- Session storage

---

## Service Management

### Starting Services

**Automatic Startup Script:**
```bash
/app/start_services.sh
```

This script:
- Starts PostgreSQL if not running
- Starts Redis if not running
- Verifies all services are healthy
- Shows status of MongoDB, PostgreSQL, and Redis

**Manual Commands:**
```bash
# PostgreSQL
service postgresql start
service postgresql stop
service postgresql restart
service postgresql status

# Redis
service redis-server start
service redis-server stop
service redis-server restart
service redis-server status
```

### Checking Service Health

**Quick Health Check:**
```bash
# PostgreSQL
PGPASSWORD='autowebiq_secure_pass' psql -h localhost -U autowebiq -d autowebiq_db -c "SELECT version();"

# Redis
redis-cli ping
# Should return: PONG

# MongoDB
mongosh --eval "db.adminCommand('ping')"
```

**API Health Check:**
```bash
curl -s "https://multiagent-web.preview.emergentagent.com/api/health" | python -m json.tool
```

Expected output:
```json
{
    "status": "healthy",
    "service": "autowebiq-backend",
    "timestamp": "2025-10-31T19:24:44.198238+00:00",
    "databases": {
        "mongodb": "connected",
        "postgresql": "connected"
    },
    "services": {
        "redis": "connected",
        "celery": "1 workers active"
    }
}
```

---

## Supervisor Configuration

PostgreSQL and Redis run as system services (not managed by supervisor).

**Supervisor-Managed Services:**
- `backend` - FastAPI application
- `celery_worker` - Celery task worker
- `flower` - Celery monitoring UI
- `frontend` - React application
- `mongodb` - MongoDB database

**View Status:**
```bash
supervisorctl status
```

**Restart Services:**
```bash
# Restart backend after code changes
supervisorctl restart backend

# Restart Celery after task changes
supervisorctl restart celery_worker

# Restart all services
supervisorctl restart all
```

---

## Database Operations

### PostgreSQL

**Connect to Database:**
```bash
PGPASSWORD='autowebiq_secure_pass' psql -h localhost -U autowebiq -d autowebiq_db
```

**Common Commands:**
```sql
-- List all tables
\dt

-- View table structure
\d users
\d projects

-- Count records
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM projects;

-- View recent projects
SELECT id, name, user_id, status, created_at 
FROM projects 
ORDER BY created_at DESC 
LIMIT 10;

-- Exit
\q
```

**Backup Database:**
```bash
pg_dump -h localhost -U autowebiq autowebiq_db > /app/backup_$(date +%Y%m%d).sql
```

**Restore Database:**
```bash
PGPASSWORD='autowebiq_secure_pass' psql -h localhost -U autowebiq -d autowebiq_db < /app/backup.sql
```

### Redis

**Connect to Redis CLI:**
```bash
redis-cli
```

**Common Commands:**
```bash
# Check status
ping

# List all keys
keys *

# Get cache stats
info stats

# View memory usage
info memory

# Get specific key
get user:123:data

# Set value
set test_key "test_value"

# Delete key
del test_key

# Clear all data (use with caution!)
flushall

# Exit
exit
```

**Monitor Redis Activity:**
```bash
redis-cli monitor
```

---

## Environment Variables

### Backend `.env` Configuration

```env
# PostgreSQL Configuration
DATABASE_URL="postgresql+asyncpg://autowebiq:autowebiq_secure_pass@localhost/autowebiq_db"

# Redis Configuration
REDIS_URL="redis://localhost:6379/0"

# Celery Configuration
CELERY_BROKER_URL="redis://localhost:6379/0"
CELERY_RESULT_BACKEND="redis://localhost:6379/0"
```

✅ All environment variables are already configured in `/app/backend/.env`

---

## Troubleshooting

### Issue: PostgreSQL Not Starting

**Symptoms:**
- "Connection refused" errors
- Backend health shows PostgreSQL as "error"

**Solution:**
```bash
# Check logs
tail -f /var/log/postgresql/postgresql-15-main.log

# Check port usage
netstat -tlnp | grep 5432

# Restart service
service postgresql restart

# Check status
service postgresql status
```

### Issue: Redis Not Starting

**Symptoms:**
- "Connection refused" on port 6379
- Celery workers failing

**Solution:**
```bash
# Check logs
tail -f /var/log/redis/redis-server.log

# Check port usage
netstat -tlnp | grep 6379

# Restart service
sudo -u redis /usr/bin/redis-server /etc/redis/redis.conf --daemonize yes

# Test connection
redis-cli ping
```

### Issue: Celery Not Connecting to Redis

**Symptoms:**
- Celery worker crashes on startup
- "Error connecting to Redis" in logs

**Solution:**
```bash
# Verify Redis is running
redis-cli ping

# Check Redis is listening on correct port
redis-cli -h localhost -p 6379 ping

# Restart Celery worker
supervisorctl restart celery_worker

# Check Celery logs
tail -f /var/log/supervisor/celery_worker.err.log
```

### Issue: Database Connection Pool Exhausted

**Symptoms:**
- "Too many connections" errors
- Slow API responses

**Solution:**
```bash
# Check active connections
PGPASSWORD='autowebiq_secure_pass' psql -h localhost -U autowebiq -d autowebiq_db -c "SELECT count(*) FROM pg_stat_activity;"

# View connection details
PGPASSWORD='autowebiq_secure_pass' psql -h localhost -U autowebiq -d autowebiq_db -c "SELECT datname, usename, application_name, client_addr, state FROM pg_stat_activity;"

# Restart backend to reset connection pool
supervisorctl restart backend
```

### Issue: Redis Memory Full

**Symptoms:**
- Redis commands failing
- "OOM command not allowed" errors

**Solution:**
```bash
# Check memory usage
redis-cli info memory

# View maxmemory setting
redis-cli config get maxmemory

# Clear expired keys
redis-cli --scan --pattern "cache:*" | xargs redis-cli del

# Or flush all (use with caution!)
redis-cli flushall
```

---

## Performance Tuning

### PostgreSQL Optimization

**Connection Pooling (Already Configured in Code):**
- Pool size: 20 connections
- Max overflow: 10 connections
- Pool timeout: 30 seconds

**Recommended PostgreSQL Settings:**
```bash
# Edit config
sudo nano /etc/postgresql/15/main/postgresql.conf

# Increase shared buffers (25% of RAM recommended)
shared_buffers = 256MB

# Increase work memory
work_mem = 16MB

# Restart to apply
service postgresql restart
```

### Redis Optimization

**Memory Management:**
```bash
# Set max memory (1GB example)
redis-cli config set maxmemory 1gb

# Set eviction policy (LRU - Least Recently Used)
redis-cli config set maxmemory-policy allkeys-lru

# Save config
redis-cli config rewrite
```

**Persistence:**
```bash
# View current settings
redis-cli config get save
redis-cli config get appendonly

# Enable AOF (Append Only File) for better durability
redis-cli config set appendonly yes
```

---

## Monitoring

### PostgreSQL Monitoring

**Active Queries:**
```sql
SELECT pid, now() - query_start as duration, state, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;
```

**Database Size:**
```sql
SELECT pg_size_pretty(pg_database_size('autowebiq_db'));
```

**Table Sizes:**
```sql
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

### Redis Monitoring

**Real-time Stats:**
```bash
redis-cli --stat
```

**Key Statistics:**
```bash
redis-cli info stats | grep -E "total_connections_received|total_commands_processed|expired_keys"
```

**Memory Usage:**
```bash
redis-cli info memory | grep -E "used_memory_human|maxmemory_human"
```

### Celery Monitoring

**Flower Dashboard:**
- URL: http://localhost:5555/flower
- Shows active workers, tasks, and queues
- Real-time monitoring

**CLI Status:**
```bash
cd /app/backend
celery -A celery_app status
```

---

## Backup Strategy

### Automated Backup Script

```bash
#!/bin/bash
# Create in /app/backup_databases.sh

BACKUP_DIR="/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
echo "Backing up PostgreSQL..."
PGPASSWORD='autowebiq_secure_pass' pg_dump -h localhost -U autowebiq autowebiq_db > "$BACKUP_DIR/postgres_$DATE.sql"

# Backup MongoDB
echo "Backing up MongoDB..."
mongodump --db autowebiq_db --out "$BACKUP_DIR/mongodb_$DATE"

# Backup Redis (optional - mainly caching)
echo "Backing up Redis..."
redis-cli save
cp /var/lib/redis/dump.rdb "$BACKUP_DIR/redis_$DATE.rdb"

echo "Backups completed!"
```

**Make executable and run:**
```bash
chmod +x /app/backup_databases.sh
/app/backup_databases.sh
```

---

## Security Considerations

### PostgreSQL Security

1. **Password Strength**: Default password is `autowebiq_secure_pass`
   - Change for production deployment
   - Use strong passwords (20+ characters, mixed case, numbers, symbols)

2. **Connection Restrictions**: Currently listening on localhost only (good)
   - Don't expose port 5432 externally
   - Use SSL/TLS for remote connections

3. **User Permissions**: `autowebiq` user has full permissions on `autowebiq_db`
   - Don't use superuser for application
   - Principle of least privilege

### Redis Security

1. **Authentication**: Currently no password (localhost only)
   - Add password for production: `requirepass your_strong_password`
   - Update connection string in `.env`

2. **Command Restrictions**: Consider disabling dangerous commands
   ```bash
   # In /etc/redis/redis.conf
   rename-command FLUSHALL ""
   rename-command FLUSHDB ""
   rename-command CONFIG ""
   ```

3. **Network Binding**: Currently bound to 127.0.0.1 (good)
   - Don't expose port 6379 externally

---

## Migration from MongoDB to PostgreSQL

### Current Architecture

- **MongoDB**: Templates, components, legacy user data
- **PostgreSQL**: New user accounts, projects, credit transactions (V2 API)
- **Hybrid Approach**: Both databases active

### Migration Script Available

```bash
# Run migration from MongoDB to PostgreSQL
cd /app/backend
python migrate_data.py
```

This migrates:
- User accounts
- Projects
- Credit transactions

---

## Quick Reference

### Connection Strings

```bash
# PostgreSQL
postgresql+asyncpg://autowebiq:autowebiq_secure_pass@localhost/autowebiq_db

# Redis
redis://localhost:6379/0

# MongoDB
mongodb://localhost:27017
```

### Default Ports

- PostgreSQL: 5432
- Redis: 6379
- MongoDB: 27017
- Backend API: 8001
- Frontend: 3000
- Flower: 5555

### Log Files

```bash
# PostgreSQL
/var/log/postgresql/postgresql-15-main.log

# Redis
/var/log/redis/redis-server.log

# Backend
/var/log/supervisor/backend.err.log
/var/log/supervisor/backend.out.log

# Celery
/var/log/supervisor/celery_worker.err.log
/var/log/supervisor/celery_worker.out.log
```

---

## Summary

✅ **PostgreSQL 15** installed and configured  
✅ **Redis 7.0** installed and configured  
✅ **Database** created with all tables  
✅ **Services** running and healthy  
✅ **Startup script** created for automatic startup  
✅ **Backup procedures** documented  
✅ **Monitoring** tools configured  

**All systems operational!** 🚀

The backend now has full access to:
- PostgreSQL for relational data (users, projects, transactions)
- Redis for caching and Celery task queue
- MongoDB for templates and components

Your V2 API endpoints are now fully functional!
