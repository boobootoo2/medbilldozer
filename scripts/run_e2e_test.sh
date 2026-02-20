#!/bin/bash
# Run E2E tests for upload → analyze workflow

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🧪 MedBillDozer E2E Test Runner"
echo "======================================"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "❌ Backend is not running on http://localhost:8080"
    echo ""
    echo "Start the backend first:"
    echo "  cd backend && python -m uvicorn app.main:app --port 8080 --reload"
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Check for token
if [ -z "$E2E_FIREBASE_TOKEN" ]; then
    echo "📋 Firebase Token Required"
    echo "======================================"
    echo ""
    echo "To get your token:"
    echo "  1. Open http://localhost:5173 in browser"
    echo "  2. Login with your account"
    echo "  3. Open Developer Tools (F12)"
    echo "  4. Go to Application > Local Storage > http://localhost:5173"
    echo "  5. Copy the value of 'access_token'"
    echo ""
    echo "Then run:"
    echo "  export E2E_FIREBASE_TOKEN='<your_token>'"
    echo "  $0"
    echo ""
    echo "Or pass it directly:"
    echo "  python tests/e2e/test_upload_analyze_workflow.py <your_token>"
    exit 1
fi

# Run the test
echo "🚀 Running E2E tests..."
echo ""

cd "$PROJECT_ROOT"
python tests/e2e/test_upload_analyze_workflow.py "$E2E_FIREBASE_TOKEN"
