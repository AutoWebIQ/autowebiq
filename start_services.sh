#!/bin/bash
# AutoWebIQ Services Startup Script
# Ensures PostgreSQL and Redis are running

echo "🚀 Starting AutoWebIQ Services..."

# Start PostgreSQL
if ! service postgresql status > /dev/null 2>&1; then
    echo "📊 Starting PostgreSQL..."
    service postgresql start
    sleep 2
else
    echo "✅ PostgreSQL already running"
fi

# Start Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚡ Starting Redis..."
    sudo -u redis /usr/bin/redis-server /etc/redis/redis.conf --daemonize yes
    sleep 2
else
    echo "✅ Redis already running"
fi

# Wait for services
sleep 3

# Check health
echo ""
echo "🏥 Checking service health..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Running"
else
    echo "❌ Redis: Not running"
fi

if PGPASSWORD='autowebiq_secure_pass' psql -h localhost -U autowebiq -d autowebiq_db -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ PostgreSQL: Running"
else
    echo "❌ PostgreSQL: Not running"
fi

if pgrep -f "mongod" > /dev/null 2>&1; then
    echo "✅ MongoDB: Running"
else
    echo "❌ MongoDB: Not running"
fi

echo ""
echo "✨ All services started!"
