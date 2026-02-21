#!/bin/bash
# Full deployment script for medbilldozer with CORS verification

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SERVICE_NAME="medbilldozer-api"
REGION="us-central1"
FRONTEND_URL="https://medbilldozer.vercel.app"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         medbilldozer Full Deployment & Verification        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# -----------------------------------------------------------------------------
# STEP 1: Backend Deployment
# -----------------------------------------------------------------------------
echo -e "${YELLOW}📦 STEP 1: Deploying Backend to Cloud Run${NC}"
echo "────────────────────────────────────────────"

cd "$PROJECT_ROOT/backend"

# Update environment variables only (don't redeploy source)
echo "Updating CORS environment variables..."
gcloud run services update $SERVICE_NAME \
  --region=$REGION \
  --update-env-vars="ENVIRONMENT=production,FRONTEND_URL=$FRONTEND_URL,BACKEND_CORS_ORIGINS=[]" \
  --quiet

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region=$REGION \
  --format="value(status.url)")

echo -e "${GREEN}✅ Backend CORS configuration updated: $SERVICE_URL${NC}"
echo ""

# -----------------------------------------------------------------------------
# STEP 2: Backend Health Check
# -----------------------------------------------------------------------------
echo -e "${YELLOW}🏥 STEP 2: Backend Health Check${NC}"
echo "────────────────────────────────────────────"

# Wait for service to be ready
echo "Waiting for service to stabilize..."
sleep 3

HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health" 2>/dev/null || echo "000")

if [ "$HEALTH_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed (HTTP $HEALTH_STATUS)${NC}"
else
    echo -e "${RED}❌ Health check failed (HTTP $HEALTH_STATUS)${NC}"
    echo "   Debug: curl -v $SERVICE_URL/health"
    exit 1
fi
echo ""

# -----------------------------------------------------------------------------
# STEP 3: CORS Verification
# -----------------------------------------------------------------------------
echo -e "${YELLOW}🔒 STEP 3: CORS Configuration Verification${NC}"
echo "────────────────────────────────────────────"

echo "Testing preflight request from $FRONTEND_URL..."

CORS_RESPONSE=$(curl -s -i -X OPTIONS "$SERVICE_URL/api/auth/login" \
  -H "Origin: $FRONTEND_URL" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization" \
  2>/dev/null)

# Check for correct CORS headers
CORS_PASS=true
CORS_ISSUES=""

if echo "$CORS_RESPONSE" | grep -qi "access-control-allow-origin: $FRONTEND_URL"; then
    echo -e "  ${GREEN}✓${NC} access-control-allow-origin: $FRONTEND_URL"
else
    CORS_PASS=false
    CORS_ISSUES+="  - Missing or incorrect access-control-allow-origin\n"
fi

if echo "$CORS_RESPONSE" | grep -qi "access-control-allow-credentials: true"; then
    echo -e "  ${GREEN}✓${NC} access-control-allow-credentials: true"
else
    CORS_PASS=false
    CORS_ISSUES+="  - Missing access-control-allow-credentials\n"
fi

if echo "$CORS_RESPONSE" | grep -qi "access-control-allow-methods"; then
    echo -e "  ${GREEN}✓${NC} access-control-allow-methods present"
else
    CORS_PASS=false
    CORS_ISSUES+="  - Missing access-control-allow-methods\n"
fi

if echo "$CORS_RESPONSE" | grep -qi "access-control-max-age"; then
    echo -e "  ${GREEN}✓${NC} access-control-max-age present (preflight caching)"
else
    echo -e "  ${YELLOW}⚠${NC}  No preflight caching (max-age missing)"
fi

if [ "$CORS_PASS" = true ]; then
    echo -e "${GREEN}✅ CORS configured correctly${NC}"
else
    echo -e "${RED}❌ CORS issues detected:${NC}"
    echo -e "$CORS_ISSUES"
    echo ""
    echo "Full response headers:"
    echo "$CORS_RESPONSE" | head -20
fi
echo ""

# -----------------------------------------------------------------------------
# STEP 4: Test Actual API Request
# -----------------------------------------------------------------------------
echo -e "${YELLOW}🧪 STEP 4: Testing API Request with Origin Header${NC}"
echo "────────────────────────────────────────────"

API_RESPONSE=$(curl -s -i "$SERVICE_URL/health" \
  -H "Origin: $FRONTEND_URL" \
  -H "Accept: application/json" \
  2>/dev/null)

API_STATUS=$(echo "$API_RESPONSE" | grep -E "^HTTP" | tail -1 | awk '{print $2}')

if [ "$API_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ API request successful (HTTP $API_STATUS)${NC}"

    # Check CORS header in response
    if echo "$API_RESPONSE" | grep -qi "access-control-allow-origin"; then
        echo -e "  ${GREEN}✓${NC} CORS header present in response"
    else
        echo -e "  ${YELLOW}⚠${NC} CORS header not in GET response (may be OK - check OPTIONS)"
    fi
else
    echo -e "${RED}❌ API request failed (HTTP $API_STATUS)${NC}"
fi
echo ""

# -----------------------------------------------------------------------------
# STEP 5: Frontend Verification
# -----------------------------------------------------------------------------
echo -e "${YELLOW}🌐 STEP 5: Frontend Verification${NC}"
echo "────────────────────────────────────────────"

FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "000")

if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Frontend is accessible (HTTP $FRONTEND_STATUS)${NC}"
elif [ "$FRONTEND_STATUS" = "404" ]; then
    echo -e "${RED}❌ Frontend returned HTTP 404 - NOT FOUND${NC}"
    echo ""
    echo "   ${YELLOW}VERCEL CONFIGURATION REQUIRED:${NC}"
    echo "   1. Go to: https://vercel.com/dashboard"
    echo "   2. Select project: medbilldozer (or frontend)"
    echo "   3. Go to: Settings → General"
    echo "   4. Set 'Root Directory' to: ${BLUE}frontend${NC}"
    echo "   5. Click 'Save'"
    echo "   6. Trigger a new deployment"
    echo ""
else
    echo -e "${RED}❌ Frontend returned HTTP $FRONTEND_STATUS${NC}"
    echo "   Check Vercel deployment status"
fi

# Test SPA routing
SPA_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL/login" 2>/dev/null || echo "000")
if [ "$SPA_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ SPA routing works (/login returns 200)${NC}"
elif [ "$SPA_STATUS" = "404" ]; then
    echo -e "${RED}❌ SPA routing broken (/login returns 404)${NC}"
    echo "   ${YELLOW}→ Vercel rewrites not configured correctly${NC}"
else
    echo -e "${YELLOW}⚠${NC}  /login returned $SPA_STATUS"
fi
echo ""

# -----------------------------------------------------------------------------
# STEP 6: End-to-End CORS Test
# -----------------------------------------------------------------------------
echo -e "${YELLOW}🔗 STEP 6: End-to-End CORS Simulation${NC}"
echo "────────────────────────────────────────────"

echo "Simulating browser request from frontend to backend..."

E2E_RESPONSE=$(curl -s -i -X POST "$SERVICE_URL/api/auth/login" \
  -H "Origin: $FRONTEND_URL" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}' \
  2>/dev/null)

E2E_STATUS=$(echo "$E2E_RESPONSE" | grep -E "^HTTP" | tail -1 | awk '{print $2}')

# We expect 401 (unauthorized) or 422 (validation error), not CORS error
if [ "$E2E_STATUS" = "401" ] || [ "$E2E_STATUS" = "422" ] || [ "$E2E_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Request reached backend (HTTP $E2E_STATUS)${NC}"
    echo "   (401/422 is expected for invalid credentials)"

    if echo "$E2E_RESPONSE" | grep -qi "access-control-allow-origin: $FRONTEND_URL"; then
        echo -e "  ${GREEN}✓${NC} Response includes correct CORS header"
    fi
else
    echo -e "${RED}❌ Unexpected response (HTTP $E2E_STATUS)${NC}"
    echo "   This might indicate a CORS or routing issue"
fi
echo ""

# -----------------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------------
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     DEPLOYMENT SUMMARY                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  Backend URL:  $SERVICE_URL"
echo "  Frontend URL: $FRONTEND_URL"
echo "  Environment:  production"
echo ""
echo "  Verification Results:"
echo "  ─────────────────────"

if [ "$HEALTH_STATUS" = "200" ]; then
    echo -e "    Health Check:    ${GREEN}PASS${NC}"
else
    echo -e "    Health Check:    ${RED}FAIL${NC}"
fi

if [ "$CORS_PASS" = true ]; then
    echo -e "    CORS Config:     ${GREEN}PASS${NC}"
else
    echo -e "    CORS Config:     ${RED}FAIL${NC}"
fi

if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "    Frontend:        ${GREEN}PASS${NC}"
elif [ "$FRONTEND_STATUS" = "404" ]; then
    echo -e "    Frontend:        ${RED}FAIL (404 - See Vercel config steps above)${NC}"
else
    echo -e "    Frontend:        ${RED}FAIL (HTTP $FRONTEND_STATUS)${NC}"
fi

echo ""
echo "  Debug Commands:"
echo "  ───────────────"
echo "    View logs:     gcloud run logs read $SERVICE_NAME --limit=50"
echo "    Describe svc:  gcloud run services describe $SERVICE_NAME --region=$REGION"
echo "    Test CORS:     curl -v -X OPTIONS $SERVICE_URL/api/auth/login -H 'Origin: $FRONTEND_URL'"
echo "    Test frontend: curl -I $FRONTEND_URL"
echo ""

if [ "$FRONTEND_STATUS" = "404" ]; then
    echo -e "${YELLOW}⚠️  ACTION REQUIRED: Fix Vercel Configuration${NC}"
    echo ""
    echo "  The backend is working correctly, but Vercel is returning 404."
    echo "  Follow these steps to fix:"
    echo ""
    echo "  1. Go to Vercel Dashboard: https://vercel.com/dashboard"
    echo "  2. Select your project (medbilldozer or frontend)"
    echo "  3. Go to: Settings → General → Root Directory"
    echo "  4. Set to: 'frontend'"
    echo "  5. Save and redeploy"
    echo ""
    echo "  OR manually trigger redeployment from the main branch."
    echo ""
fi
