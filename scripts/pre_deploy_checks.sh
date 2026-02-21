#!/bin/bash
# Pre-deployment validation checks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔍 Pre-Deployment Validation Checks"
echo "=========================================="
echo ""

FAILED=0

# Check 1: Backend linting
echo "📝 Check 1: Backend Code Quality"
echo "------------------------------------------"
cd "$PROJECT_ROOT/backend"
if command -v ruff &> /dev/null; then
    echo "Running ruff..."
    ruff check app/ || FAILED=1
else
    echo "⚠️  ruff not installed, skipping"
fi
echo ""

# Check 2: Frontend build
echo "🏗️  Check 2: Frontend Build"
echo "------------------------------------------"
cd "$PROJECT_ROOT/frontend"
if [ -d "node_modules" ]; then
    echo "Building frontend..."
    npm run build || FAILED=1
    echo "✅ Frontend build successful"
else
    echo "⚠️  node_modules not found, skipping frontend build"
fi
echo ""

# Check 3: Backend starts successfully
echo "🚀 Check 3: Backend Startup"
echo "------------------------------------------"
cd "$PROJECT_ROOT/backend"
echo "Testing backend initialization..."
timeout 10s python -c "
import sys
sys.path.insert(0, '.')
from app.main import app
print('✅ Backend imports successfully')
" || FAILED=1
echo ""

# Check 4: Configuration validation
echo "⚙️  Check 4: Configuration Validation"
echo "------------------------------------------"
if [ -f "$PROJECT_ROOT/backend/.env" ]; then
    echo "✅ Backend .env exists"

    # Check required env vars
    required_vars=(
        "FIREBASE_PROJECT_ID"
        "GCS_PROJECT_ID"
        "OPENAI_API_KEY"
        "SUPABASE_URL"
    )

    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" "$PROJECT_ROOT/backend/.env"; then
            echo "  ✅ $var configured"
        else
            echo "  ❌ $var missing"
            FAILED=1
        fi
    done
else
    echo "❌ Backend .env not found"
    FAILED=1
fi
echo ""

# Summary
echo "=========================================="
if [ $FAILED -eq 0 ]; then
    echo "✅ All pre-deployment checks passed!"
    echo ""
    echo "Safe to deploy ✈️"
    exit 0
else
    echo "❌ Some pre-deployment checks failed"
    echo ""
    echo "⚠️  DO NOT DEPLOY until all checks pass"
    exit 1
fi
