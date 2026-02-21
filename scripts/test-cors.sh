#!/bin/bash

# CORS Test Script
# Usage: ./scripts/test-cors.sh <backend-url> <origin>
# Example: ./scripts/test-cors.sh http://localhost:8080 http://localhost:3000

set -e

BACKEND_URL=${1:-http://localhost:8080}
ORIGIN=${2:-http://localhost:3000}

echo "🔍 Testing CORS Configuration"
echo "================================"
echo "  Backend: $BACKEND_URL"
echo "  Origin:  $ORIGIN"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Preflight Request (OPTIONS)
echo "📋 Test 1: Preflight Request (OPTIONS)"
echo "---------------------------------------"
RESPONSE=$(curl -X OPTIONS "$BACKEND_URL/api/auth/login" \
  -H "Origin: $ORIGIN" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization, Content-Type" \
  -i -s)

if echo "$RESPONSE" | grep -q "Access-Control-Allow-Origin: $ORIGIN"; then
    echo -e "${GREEN}✓${NC} Access-Control-Allow-Origin: $ORIGIN"
else
    echo -e "${RED}✗${NC} Missing or incorrect Access-Control-Allow-Origin"
    echo "$RESPONSE" | grep -i "access-control-allow-origin" || echo "  (header not found)"
fi

if echo "$RESPONSE" | grep -q "Access-Control-Allow-Credentials: true"; then
    echo -e "${GREEN}✓${NC} Access-Control-Allow-Credentials: true"
else
    echo -e "${RED}✗${NC} Missing Access-Control-Allow-Credentials"
fi

if echo "$RESPONSE" | grep -q "Access-Control-Max-Age"; then
    MAX_AGE=$(echo "$RESPONSE" | grep -i "Access-Control-Max-Age" | cut -d: -f2 | tr -d ' \r')
    echo -e "${GREEN}✓${NC} Access-Control-Max-Age: $MAX_AGE seconds"
else
    echo -e "${YELLOW}⚠${NC}  No Access-Control-Max-Age (preflight caching disabled)"
fi

# Test 2: Actual GET Request
echo ""
echo "📋 Test 2: Actual Request (GET /health)"
echo "---------------------------------------"
RESPONSE=$(curl -X GET "$BACKEND_URL/health" \
  -H "Origin: $ORIGIN" \
  -H "Content-Type: application/json" \
  -i -s)

if echo "$RESPONSE" | grep -q "Access-Control-Allow-Origin: $ORIGIN"; then
    echo -e "${GREEN}✓${NC} Access-Control-Allow-Origin: $ORIGIN"
else
    echo -e "${RED}✗${NC} Missing or incorrect Access-Control-Allow-Origin"
fi

if echo "$RESPONSE" | grep -q "Access-Control-Allow-Credentials: true"; then
    echo -e "${GREEN}✓${NC} Access-Control-Allow-Credentials: true"
else
    echo -e "${RED}✗${NC} Missing Access-Control-Allow-Credentials"
fi

if echo "$RESPONSE" | grep -q "X-Correlation-ID"; then
    echo -e "${GREEN}✓${NC} X-Correlation-ID header exposed"
else
    echo -e "${YELLOW}⚠${NC}  X-Correlation-ID header not found"
fi

# Test 3: Check HTTP status
HTTP_STATUS=$(echo "$RESPONSE" | grep -i "HTTP" | head -1 | awk '{print $2}')
if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓${NC} HTTP Status: $HTTP_STATUS"
else
    echo -e "${RED}✗${NC} HTTP Status: $HTTP_STATUS (expected 200)"
fi

echo ""
echo "================================"
echo -e "${GREEN}✓ CORS Test Complete${NC}"
echo ""
echo "💡 To test with different origins:"
echo "   ./scripts/test-cors.sh $BACKEND_URL https://different-origin.com"
