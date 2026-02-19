#!/bin/bash
# MedBillDozer Infrastructure Setup Script
# Creates GCS buckets and configures CORS

set -e

echo "🏗️  MedBillDozer Infrastructure Setup"
echo "===================================="
echo ""

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: No GCP project configured."
    echo "   Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📦 Using GCP Project: $PROJECT_ID"
echo ""

# Create GCS buckets
echo "🪣 Creating GCS buckets..."
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://medbilldozer-documents 2>/dev/null || echo "   Bucket medbilldozer-documents already exists"
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://medbilldozer-clinical 2>/dev/null || echo "   Bucket medbilldozer-clinical already exists"
echo "✅ Buckets created"
echo ""

# Prompt for frontend URL
echo "📝 Enter your frontend URL (or press Enter for localhost):"
read -p "   Frontend URL [http://localhost:5173]: " FRONTEND_URL
FRONTEND_URL=${FRONTEND_URL:-http://localhost:5173}
echo ""

# Create CORS configuration
echo "🔧 Configuring CORS for direct uploads..."
cat > /tmp/cors.json <<EOF
[
  {
    "origin": ["http://localhost:5173", "$FRONTEND_URL"],
    "method": ["GET", "PUT", "POST"],
    "responseHeader": ["Content-Type", "Authorization"],
    "maxAgeSeconds": 3600
  }
]
EOF

# Apply CORS
gsutil cors set /tmp/cors.json gs://medbilldozer-documents
echo "✅ CORS configured"
echo ""

# Verify CORS
echo "📋 Current CORS configuration:"
gsutil cors get gs://medbilldozer-documents
echo ""

echo "✅ Infrastructure setup complete!"
echo ""
echo "Created buckets:"
echo "  - gs://medbilldozer-documents"
echo "  - gs://medbilldozer-clinical"
echo ""
echo "CORS configured for:"
echo "  - http://localhost:5173"
echo "  - $FRONTEND_URL"
echo ""
echo "Next steps:"
echo "1. Set up Firebase Authentication"
echo "2. Set up Supabase database"
echo "3. Configure backend/.env file"
echo "4. Run: ./scripts/deploy_backend.sh"
echo ""
