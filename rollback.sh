#!/bin/bash

# Rollback to previous deployment

set -e

NAMESPACE="autowebiq"

echo "🔙 Rolling back AutoWebIQ deployment..."

kubectl rollout undo deployment/autowebiq-backend -n $NAMESPACE
kubectl rollout undo deployment/autowebiq-frontend -n $NAMESPACE

echo "Waiting for rollback..."
kubectl rollout status deployment/autowebiq-backend -n $NAMESPACE
kubectl rollout status deployment/autowebiq-frontend -n $NAMESPACE

echo "✅ Rollback complete!"
kubectl get pods -n $NAMESPACE