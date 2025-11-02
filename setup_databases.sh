#!/bin/bash
# PostgreSQL and Redis Installation and Setup Script
# Makes services persistent and auto-starting

set -e

echo "🚀 AutoWebIQ Database Services Setup"
echo "===================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "❌ Please run as root (use sudo)"
   exit 1
fi

echo "📦 Step 1: Installing PostgreSQL and Redis..."
apt-get update -qq
apt-get install -y -qq postgresql postgresql-contrib redis-server

echo "✅ PostgreSQL and Redis installed"
echo ""

echo "🔧 Step 2: Configuring PostgreSQL..."

# Start PostgreSQL
service postgresql start || /usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/15/main start

# Wait for PostgreSQL to be ready
sleep 3

# Create database and user
sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname='autowebiq_db'" | grep -q 1 || \
sudo -u postgres psql <<EOF
CREATE USER autowebiq WITH PASSWORD 'autowebiq_secure_pass';
CREATE DATABASE autowebiq_db OWNER autowebiq;
GRANT ALL PRIVILEGES ON DATABASE autowebiq_db TO autowebiq;
ALTER USER autowebiq CREATEDB;
EOF

echo "✅ PostgreSQL database and user created"
echo ""

echo "🔧 Step 3: Configuring Redis..."

# Start Redis
redis-server /etc/redis/redis.conf --daemonize yes || service redis-server start

sleep 2

echo "✅ Redis started"
echo ""

echo "📋 Step 4: Creating database tables..."

cd /app/backend

# Create tables using SQLAlchemy
python3 << 'PYTHON_SCRIPT'
import asyncio
from database import Base, engine

async def create_tables():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"⚠️  Error creating tables: {e}")

asyncio.run(create_tables())
PYTHON_SCRIPT

echo ""

echo "🔍 Step 5: Verifying services..."

# Test PostgreSQL
if PGPASSWORD='autowebiq_secure_pass' psql -h localhost -U autowebiq -d autowebiq_db -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ PostgreSQL: Running and accessible"
else
    echo "❌ PostgreSQL: Not accessible"
fi

# Test Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Running and accessible"
else
    echo "❌ Redis: Not accessible"
fi

# Test MongoDB
if mongosh --quiet --eval "db.adminCommand('ping').ok" > /dev/null 2>&1; then
    echo "✅ MongoDB: Running and accessible"
else
    echo "⚠️  MongoDB: Check status"
fi

echo ""

echo "🔄 Step 6: Creating supervisor configs for persistence..."

# PostgreSQL Supervisor Config
cat > /etc/supervisor/conf.d/postgresql_autowebiq.conf << 'EOF'
[program:postgresql_autowebiq]
command=/usr/lib/postgresql/15/bin/postgres -D /var/lib/postgresql/15/main -c config_file=/etc/postgresql/15/main/postgresql.conf
user=postgres
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/postgresql.err.log
stdout_logfile=/var/log/supervisor/postgresql.out.log
priority=10
startsecs=10
stopwaitsecs=30
EOF

# Redis Supervisor Config
cat > /etc/supervisor/conf.d/redis_autowebiq.conf << 'EOF'
[program:redis_autowebiq]
command=/usr/bin/redis-server /etc/redis/redis.conf --supervised no
user=redis
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/redis.err.log
stdout_logfile=/var/log/supervisor/redis.out.log
priority=10
startsecs=5
stopwaitsecs=10
EOF

# Reload supervisor
supervisorctl reread
supervisorctl update

echo "✅ Supervisor configs created"
echo ""

echo "🔄 Step 7: Restarting backend services..."

supervisorctl restart backend celery_worker flower

sleep 5

echo "✅ Backend services restarted"
echo ""

echo "========================================="
echo "🎉 Setup Complete!"
echo "========================================="
echo ""
echo "Service Status:"
supervisorctl status | grep -E "(postgres|redis|backend|celery|mongodb)"
echo ""
echo "Next Steps:"
echo "1. Services are now managed by supervisor"
echo "2. They will auto-start on container restart"
echo "3. Test the health endpoint: curl https://autowebiq-iq.preview.emergentagent.com/api/health"
echo ""
