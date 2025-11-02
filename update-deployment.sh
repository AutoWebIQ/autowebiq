#!/bin/bash

# Update deployment with latest Docker images

set -e

echo "🔄 Updating AutoWebIQ deployment..."

# Configuration
DOCKER_REPO="aashikzm098"
NAMESPACE="autowebiq"

# Load env
source backend/.env

# Build new images
echo "Building new images..."
VERSION=$(date +%Y%m%d-%H%M%S)

docker build -t $DOCKER_REPO/autowebiq-backend:$VERSION -t $DOCKER_REPO/autowebiq-backend:latest ./backend
docker build -t $DOCKER_REPO/autowebiq-frontend:$VERSION -t $DOCKER_REPO/autowebiq-frontend:latest ./frontend

# Push images
echo "Pushing images..."
echo "$DOCKER_HUB_TOKEN" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin

docker push $DOCKER_REPO/autowebiq-backend:$VERSION
docker push $DOCKER_REPO/autowebiq-backend:latest
docker push $DOCKER_REPO/autowebiq-frontend:$VERSION
docker push $DOCKER_REPO/autowebiq-frontend:latest

# Rolling update
echo "Performing rolling update..."
kubectl rollout restart deployment/autowebiq-backend -n $NAMESPACE
kubectl rollout restart deployment/autowebiq-frontend -n $NAMESPACE

# Wait for rollout
echo "Waiting for rollout to complete..."
kubectl rollout status deployment/autowebiq-backend -n $NAMESPACE
kubectl rollout status deployment/autowebiq-frontend -n $NAMESPACE

echo "✅ Update complete!"
echo ""
echo "Check status:"
echo "kubectl get pods -n $NAMESPACE"