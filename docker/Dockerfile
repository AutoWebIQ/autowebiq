# AutoWebIQ Workspace Container
# This container runs user-generated websites with isolated environments

FROM node:18-alpine

# Install Python, pip, and other essentials
RUN apk add --no-cache \
    python3 \
    py3-pip \
    nginx \
    supervisor \
    bash \
    curl

# Create workspace directory
WORKDIR /workspace

# Create directories for frontend and backend
RUN mkdir -p /workspace/frontend /workspace/backend /workspace/logs

# Install common frontend dependencies
RUN cd /workspace/frontend && \
    npm init -y && \
    npm install --save \
    react@18 react-dom@18 \
    express@4

# Install common backend dependencies
RUN pip3 install --break-system-packages \
    fastapi \
    uvicorn[standard] \
    pydantic \
    python-multipart

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisord.conf

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
# 3000 - Frontend (React/HTML)
# 8001 - Backend (FastAPI)
# 80 - Nginx proxy
EXPOSE 3000 8001 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/health || exit 1

# Start supervisor
ENTRYPOINT ["/entrypoint.sh"]
