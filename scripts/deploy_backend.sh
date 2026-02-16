#!/bin/bash
# MedBillDozer Backend Deployment Script
# Usage: ./scripts/deploy_backend.sh

set -e  # Exit on error

echo "🚀 MedBillDozer Backend Deployment"
echo "=================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Please install it first."
    echo "   Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No GCP project configured."
    echo "   Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📦 Using GCP Project: $PROJECT_ID"
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env file not found"
    echo "   Copy backend/.env.example to backend/.env and fill in your credentials"
    exit 1
fi

echo "✅ Environment file found"
echo ""

# Enable required APIs
echo "🔧 Enabling required GCP APIs..."
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
echo "✅ APIs enabled"
echo ""

# Build Docker image
echo "🏗️  Building Docker image..."
cd backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/medbilldozer-api
echo "✅ Docker image built"
echo ""

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy medbilldozer-api \
  --image gcr.io/$PROJECT_ID/medbilldozer-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0

echo ""
echo "✅ Deployment complete!"
echo ""

# Get service URL
SERVICE_URL=$(gcloud run services describe medbilldozer-api \
  --region=us-central1 \
  --format='value(status.url)')

echo "🎉 Backend deployed successfully!"
echo ""
echo "Backend URL: $SERVICE_URL"
echo "API Docs: $SERVICE_URL/docs"
echo ""
echo "Test health endpoint:"
echo "  curl $SERVICE_URL/health"
echo ""
echo "Next steps:"
echo "1. Update frontend VITE_API_BASE_URL to: $SERVICE_URL"
echo "2. Update Firebase authorized domains"
echo "3. Update GCS CORS configuration"
echo ""
