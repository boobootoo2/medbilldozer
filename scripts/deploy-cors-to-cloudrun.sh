#!/bin/bash
# Quick script to update CORS configuration in Cloud Run

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Updating CORS Configuration in Cloud Run${NC}"
echo "=========================================="
echo ""

# Configuration - UPDATE THESE VALUES
SERVICE_NAME="medbilldozer-api"
REGION="us-central1"  # Change to your region
FRONTEND_URL="https://medbilldozer.vercel.app"

# Ask for confirmation
echo "This will update the following environment variables:"
echo "  ENVIRONMENT=production"
echo "  FRONTEND_URL=$FRONTEND_URL"
echo "  BACKEND_CORS_ORIGINS=[]"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Update Cloud Run
echo ""
echo -e "${YELLOW}⏳ Updating Cloud Run service...${NC}"

gcloud run services update $SERVICE_NAME \
  --region=$REGION \
  --update-env-vars ENVIRONMENT=production,FRONTEND_URL=$FRONTEND_URL,BACKEND_CORS_ORIGINS=[] \
  --quiet

echo -e "${GREEN}✅ Environment variables updated${NC}"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --format="value(status.url)")

echo ""
echo "Service URL: $SERVICE_URL"

# Test health endpoint
echo ""
echo -e "${YELLOW}🧪 Testing health endpoint...${NC}"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" $SERVICE_URL/health)

if [ "$HEALTH_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed (HTTP $HEALTH_STATUS)${NC}"
else
    echo -e "${RED}⚠️  Health check returned HTTP $HEALTH_STATUS${NC}"
fi

# Test CORS
echo ""
echo -e "${YELLOW}🧪 Testing CORS configuration...${NC}"
CORS_TEST=$(curl -X OPTIONS $SERVICE_URL/api/auth/login \
  -H "Origin: $FRONTEND_URL" \
  -H "Access-Control-Request-Method: POST" \
  -s -i)

if echo "$CORS_TEST" | grep -q "access-control-allow-origin: $FRONTEND_URL"; then
    echo -e "${GREEN}✅ CORS configured correctly${NC}"
    echo "   Origin allowed: $FRONTEND_URL"
else
    echo -e "${RED}⚠️  CORS test failed - check logs${NC}"
    echo ""
    echo "Debug with:"
    echo "  gcloud run logs read $SERVICE_NAME --limit=50"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Test your frontend at: $FRONTEND_URL"
echo "  2. Check logs with: gcloud run logs read $SERVICE_NAME --limit=50"
echo "  3. View service: https://console.cloud.google.com/run"
echo ""
