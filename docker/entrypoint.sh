#!/bin/bash
set -e

echo "🚀 Starting AutoWebIQ Workspace Container..."

# Create log directory
mkdir -p /workspace/logs

# Start supervisor (manages nginx, frontend, backend)
exec /usr/bin/supervisord -c /etc/supervisord.conf
