#!/bin/bash
# Manual deployment script for MedBillDozer backend to Cloud Run

set -e  # Exit on error

PROJECT_ID="medbilldozer"
SERVICE_NAME="medbilldozer-api"
REGION="us-central1"

echo "🚀 Deploying MedBillDozer backend to Google Cloud Run"
echo "=================================================="
echo ""

# Step 1: Set project
echo "📋 Step 1: Setting GCP project..."
gcloud config set project $PROJECT_ID

# Step 2: Build Docker image
echo ""
echo "🐳 Step 2: Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  -f backend/Dockerfile .

# Step 3: Push to GCR
echo ""
echo "⬆️  Step 3: Pushing image to Google Container Registry..."
gcloud auth configure-docker
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Step 4: Deploy to Cloud Run
echo ""
echo "☁️  Step 4: Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --min-instances 0 \
  --timeout 300 \
  --set-env-vars "DEBUG=false,ENVIRONMENT=production,FIREBASE_PROJECT_ID=medbilldozer,SUPABASE_URL=https://zrhlpitzonhftigmdvgz.supabase.co,GCS_PROJECT_ID=medbilldozer,GCS_BUCKET_DOCUMENTS=medbilldozer.appspot.com,GCS_BUCKET_CLINICAL_IMAGES=medbilldozer.appspot.com" \
  --set-secrets "FIREBASE_PRIVATE_KEY=firebase-private-key:latest,FIREBASE_CLIENT_EMAIL=firebase-client-email:latest,SUPABASE_SERVICE_ROLE_KEY=supabase-service-role-key:latest,JWT_SECRET_KEY=jwt-secret-key:latest,OPENAI_API_KEY=openai-api-key:latest,GEMINI_API_KEY=gemini-api-key:latest"

# Step 5: Get the deployed URL
echo ""
echo "🔗 Step 5: Getting Cloud Run URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo ""
echo "=============================================="
echo "✅ Deployment complete!"
echo ""
echo "🔗 Backend URL: $SERVICE_URL"
echo ""
echo "Next steps:"
echo "1. Test the backend: curl $SERVICE_URL/health"
echo "2. Update Vercel environment variables with this URL"
echo "3. Add to GitHub secrets: VITE_API_BASE_URL=$SERVICE_URL"
echo "=============================================="
