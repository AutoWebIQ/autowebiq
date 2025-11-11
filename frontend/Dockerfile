# Production Dockerfile for AutoWebIQ Frontend
# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Build arguments for environment variables
ARG REACT_APP_BACKEND_URL=https://autowebiq.com
ARG REACT_APP_API_URL=https://autowebiq.com/api
ARG REACT_APP_ENVIRONMENT=production

# Set environment variables
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_ENVIRONMENT=$REACT_APP_ENVIRONMENT

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build for production
RUN yarn build

# Stage 2: Production with Nginx
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]