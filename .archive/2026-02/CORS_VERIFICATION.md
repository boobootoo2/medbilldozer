# CORS Configuration Verification Guide

Use this guide to verify CORS is configured correctly in each environment.

## Quick Verification Script

### Check Backend Configuration

```bash
# From backend directory
cd backend

# Method 1: Quick check
python -c "from app.config import settings; print('Environment:', settings.environment); print('CORS Origins:', settings.all_cors_origins)"

# Method 2: Full check
python << 'EOF'
from app.config import settings

print("\n=== CORS Configuration ===")
print(f"Environment: {settings.environment}")
print(f"Frontend URL: {settings.frontend_url}")
print(f"Additional Origins: {settings.backend_cors_origins}")
print(f"\nAll Allowed Origins:")
for origin in settings.all_cors_origins:
    print(f"  ✓ {origin}")
EOF
```

## Environment-Specific Checks

### 🏠 Local Development

**Expected Configuration:**
- `ENVIRONMENT=local`
- Origins should include: `localhost:3000`, `localhost:5173`, `localhost:8000`, and `127.0.0.1` variants

**Test:**
```bash
# 1. Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8080

# 2. In another terminal, test CORS preflight
curl -X OPTIONS http://localhost:8080/api/auth/login \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization, Content-Type" \
  -i

# Expected response headers:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Credentials: true
# Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
# Access-Control-Max-Age: 600
```

**Frontend Test:**
```bash
# Start frontend
cd frontend
npm run dev

# Open browser to http://localhost:3000
# Open DevTools Console and run:
fetch('http://localhost:8080/health', {
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' }
}).then(r => r.json()).then(console.log)

# Should succeed without CORS errors
```

---

### 🧪 Staging Environment

**Expected Configuration:**
- `ENVIRONMENT=staging`
- `FRONTEND_URL=https://staging-frontend.vercel.app`
- Origins should include: `https://staging.medbilldozer.com` + `FRONTEND_URL`

**Test from Deployment:**
```bash
# SSH/connect to staging backend
python -c "from app.config import settings; print(settings.all_cors_origins)"

# Test via curl
curl -X OPTIONS https://staging-api.medbilldozer.com/api/auth/login \
  -H "Origin: https://staging-frontend.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization, Content-Type" \
  -i
```

**Frontend Test:**
```javascript
// In staging frontend browser console
fetch('https://staging-api.medbilldozer.com/health', {
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' }
}).then(r => r.json()).then(console.log)
```

---

### 🚀 Production Environment

**Expected Configuration:**
- `ENVIRONMENT=production`
- `FRONTEND_URL=https://medbilldozer.vercel.app`
- Origins should include: `https://medbilldozer.com`, `https://www.medbilldozer.com`, + `FRONTEND_URL`

**Test:**
```bash
# Test production CORS
curl -X OPTIONS https://api.medbilldozer.com/api/auth/login \
  -H "Origin: https://medbilldozer.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization, Content-Type" \
  -i

# Test with Vercel frontend
curl -X OPTIONS https://api.medbilldozer.com/api/auth/login \
  -H "Origin: https://medbilldozer.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization, Content-Type" \
  -i
```

**Frontend Test:**
```javascript
// In production frontend browser console
fetch('https://api.medbilldozer.com/health', {
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' }
}).then(r => r.json()).then(console.log)
```

---

## 🔍 Troubleshooting

### Issue: "Origin not allowed" error

**Check:**
1. Verify `ENVIRONMENT` variable is set correctly
2. Print actual origins: `python -c "from app.config import settings; print(settings.all_cors_origins)"`
3. Check frontend URL matches exactly (no trailing slashes, correct protocol)
4. Check browser DevTools Network tab for actual Origin header sent

**Fix:**
```bash
# Add the specific origin temporarily
export BACKEND_CORS_ORIGINS='["https://actual-frontend-url.com"]'

# Or set FRONTEND_URL
export FRONTEND_URL=https://actual-frontend-url.com

# Restart backend
```

---

### Issue: Still seeing old hardcoded origins

**Check:**
1. Ensure you're using the updated code (check `main.py` line 67 uses `settings.all_cors_origins`)
2. Restart backend server completely
3. Clear any cached environment variables

**Fix:**
```bash
# Force reload
pkill -f uvicorn
cd backend
python -m uvicorn app.main:app --reload
```

---

### Issue: CORS works locally but not in deployment

**Check:**
1. Environment variables are actually set in deployment platform
2. Case sensitivity: use uppercase `ENVIRONMENT`, not `environment`
3. JSON parsing: `BACKEND_CORS_ORIGINS` must be valid JSON array

**Fix:**
```bash
# Cloud Run
gcloud run services describe medbilldozer-api --format="value(spec.template.spec.containers[0].env)"

# Vercel (backend)
vercel env ls

# Check logs for startup environment
gcloud run logs read medbilldozer-api --limit=50 | grep -i environment
```

---

### Issue: Preflight requests timing out

**Check:**
1. Backend is responding to OPTIONS requests
2. `OPTIONS` is in `allow_methods` list
3. No firewall/load balancer blocking OPTIONS

**Test:**
```bash
# Direct OPTIONS test
curl -X OPTIONS https://your-backend.com/api/auth/login -v

# Should return 200 with CORS headers, not 405 Method Not Allowed
```

---

## 📋 Deployment Checklist

### Before Deploying Each Environment:

- [ ] Set `ENVIRONMENT` variable to correct value
- [ ] Set `FRONTEND_URL` to your frontend's actual URL
- [ ] Set `BACKEND_CORS_ORIGINS=[]` (or JSON array if needed)
- [ ] Restart/redeploy backend service
- [ ] Test with verification script above
- [ ] Test from actual frontend in browser
- [ ] Check browser DevTools for CORS errors
- [ ] Test authenticated requests work
- [ ] Test preflight OPTIONS requests

### Environment Variables Reference:

| Environment | ENVIRONMENT | FRONTEND_URL | Additional Origins |
|-------------|-------------|--------------|-------------------|
| Local | `local` | `http://localhost:3000` | Usually not needed |
| Staging | `staging` | `https://staging-frontend.vercel.app` | Preview URLs if needed |
| Production | `production` | `https://medbilldozer.vercel.app` | Usually not needed |

---

## 🆘 Quick Fixes

### Add a new allowed origin temporarily:
```bash
# Backend .env
BACKEND_CORS_ORIGINS=["https://new-origin.com"]
```

### Debug what origins are actually allowed:
```bash
cd backend
python -c "from app.config import settings; import json; print(json.dumps(settings.all_cors_origins, indent=2))"
```

### Test CORS from command line:
```bash
./scripts/test-cors.sh  # See below
```

---

## 📝 Test Script

Create `scripts/test-cors.sh`:

```bash
#!/bin/bash

# CORS Test Script
# Usage: ./scripts/test-cors.sh <backend-url> <origin>
# Example: ./scripts/test-cors.sh http://localhost:8080 http://localhost:3000

BACKEND_URL=${1:-http://localhost:8080}
ORIGIN=${2:-http://localhost:3000}

echo "Testing CORS for:"
echo "  Backend: $BACKEND_URL"
echo "  Origin: $ORIGIN"
echo ""

echo "=== Preflight Request (OPTIONS) ==="
curl -X OPTIONS "$BACKEND_URL/api/auth/login" \
  -H "Origin: $ORIGIN" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization, Content-Type" \
  -i -s | grep -i "access-control"

echo ""
echo "=== Actual Request (GET) ==="
curl -X GET "$BACKEND_URL/health" \
  -H "Origin: $ORIGIN" \
  -H "Content-Type: application/json" \
  -i -s | grep -i "access-control"

echo ""
echo "✓ Done"
```

Make it executable:
```bash
chmod +x scripts/test-cors.sh
```

Run it:
```bash
./scripts/test-cors.sh http://localhost:8080 http://localhost:3000
./scripts/test-cors.sh https://api.medbilldozer.com https://medbilldozer.com
```

---

## 📚 Additional Resources

- [CORS_CHANGES.md](CORS_CHANGES.md) - Complete documentation of changes
- [backend/.env.example](backend/.env.example) - Configuration template
- [MDN CORS Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
