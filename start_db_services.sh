#!/bin/bash
# Startup script for PostgreSQL and Redis
# Call this from supervisor or container entrypoint

echo "🚀 Starting Database Services..."

# Start PostgreSQL
if ! pgrep -f "postgres -D" > /dev/null; then
    echo "📊 Starting PostgreSQL..."
    sudo -u postgres /usr/lib/postgresql/15/bin/postgres -D /var/lib/postgresql/15/main -c config_file=/etc/postgresql/15/main/postgresql.conf > /dev/null 2>&1 &
    sleep 3
    echo "✅ PostgreSQL started"
else
    echo "✅ PostgreSQL already running"
fi

# Start Redis  
if ! pgrep -f "redis-server" > /dev/null; then
    echo "⚡ Starting Redis..."
    redis-server /etc/redis/redis.conf --daemonize yes
    sleep 2
    echo "✅ Redis started"
else
    echo "✅ Redis already running"
fi

# Verify services
echo ""
echo "🔍 Verifying services..."

if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Running"
else
    echo "❌ Redis: Not responding"
fi

if PGPASSWORD='autowebiq_secure_pass' psql -h localhost -U autowebiq -d autowebiq_db -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ PostgreSQL: Running"
else
    echo "❌ PostgreSQL: Not responding"
fi

echo ""
echo "✨ Database services ready!"
