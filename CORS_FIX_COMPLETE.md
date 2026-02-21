# CORS Fix Complete - February 21, 2026

## Problem Summary

The medbilldozer backend was failing to start on Google Cloud Run (all revisions after 00037 crashed), and when working, was missing the critical `access-control-allow-origin` CORS header.

## Root Causes

### Primary Issue: Missing Required Environment Variables
- **Problem**: Settings class required `FIREBASE_PROJECT_ID` and `GCS_PROJECT_ID` but they weren't set in Cloud Run
- **Impact**: Container failed to start with Pydantic validation error
- **Fix**: Added environment variables to Cloud Run service

### Secondary Issue: CORS Configuration
- **Problem**: `ALLOWED_ORIGINS` env var wasn't being read/parsed correctly
- **Impact**: Missing `access-control-allow-origin` header in API responses
- **Fix**: Modified config.py to properly parse comma-separated `ALLOWED_ORIGINS` env var

## Changes Made

### 1. Backend Code Changes (Committed)

#### [backend/app/config.py](backend/app/config.py)
- Changed `allowed_origins` field from hardcoded string to reading from `ALLOWED_ORIGINS` env var
- Updated `all_cors_origins` property to parse comma-separated origins
- Added priority system: ALLOWED_ORIGINS > environment defaults > FRONTEND_URL

#### [backend/app/main.py](backend/app/main.py)
- Added CORS configuration logging on startup (shows all configured origins)
- Added `/debug/cors` endpoint to verify CORS configuration
- Added build identifier to root endpoint for deployment verification

### 2. Cloud Run Environment Variables (Set via gcloud)

```bash
# Added to fix container startup
FIREBASE_PROJECT_ID=medbilldozer
GCS_PROJECT_ID=medbilldozer

# Already existed
ALLOWED_ORIGINS=https://medbilldozer.vercel.app,https://medbilldozer-git-v031-john-shultzs-projects.vercel.app,https://medbilldozer-git-v03-john-shultzs-projects.vercel.app,http://localhost:3000,http://localhost:5173
ENVIRONMENT=production
FRONTEND_URL=https://medbilldozer.vercel.app
```

## Verification

### Container Startup ✅
- Revision: `medbilldozer-api-00056-sx8`
- Status: Running and healthy
- Startup logs show: "🔧 Configuring CORS for 5 origins:"

### CORS Headers ✅
Tested with multiple origins:

```bash
# Test 1: Vercel preview deployment (v0.3.1 branch)
curl -X OPTIONS https://medbilldozer-api-360553024921.us-central1.run.app/api/auth/login \
  -H "Origin: https://medbilldozer-git-v031-john-shultzs-projects.vercel.app" \
  -H "Access-Control-Request-Method: POST"

Response:
✅ access-control-allow-origin: https://medbilldozer-git-v031-john-shultzs-projects.vercel.app
✅ access-control-allow-credentials: true
✅ access-control-allow-methods: DELETE, GET, POST, PUT, PATCH, OPTIONS
✅ access-control-allow-headers: Authorization, Content-Type, Accept, X-Request-ID
✅ access-control-max-age: 600

# Test 2: Main Vercel deployment
curl -X OPTIONS https://medbilldozer-api-360553024921.us-central1.run.app/api/auth/login \
  -H "Origin: https://medbilldozer.vercel.app" \
  -H "Access-Control-Request-Method: POST"

Response:
✅ access-control-allow-origin: https://medbilldozer.vercel.app
✅ (all other headers present)
```

### Debug Endpoint ✅
```bash
curl https://medbilldozer-api-360553024921.us-central1.run.app/debug/cors
```

Response shows correctly parsed origins:
```json
{
  "allowed_origins": [
    "https://medbilldozer.vercel.app",
    "https://medbilldozer-git-v031-john-shultzs-projects.vercel.app",
    "https://medbilldozer-git-v03-john-shultzs-projects.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173"
  ],
  "environment": "production",
  "frontend_url": "https://medbilldozer.vercel.app",
  "raw_allowed_origins_env_var": "https://medbilldozer.vercel.app,..."
}
```

## Commands for Future Reference

### Update Cloud Run Environment Variables
```bash
gcloud run services update medbilldozer-api \
  --region=us-central1 \
  --update-env-vars="KEY=value"
```

### Deploy Backend
```bash
cd backend
gcloud run deploy medbilldozer-api \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated
```

### Check Logs for CORS Configuration
```bash
gcloud run services logs read medbilldozer-api \
  --region=us-central1 \
  --limit=100 | grep -E "(🔧 Configuring CORS|✅)"
```

### Test CORS Preflight
```bash
curl -X OPTIONS <API_URL>/api/auth/login \
  -H "Origin: <FRONTEND_URL>" \
  -H "Access-Control-Request-Method: POST" \
  -D - -o /dev/null
```

## Next Steps

1. ✅ Container startup fixed
2. ✅ CORS headers working
3. 🔲 Test frontend end-to-end (user should test in browser)
4. 🔲 Consider removing `/debug/cors` endpoint (or restrict to dev/admin only)
5. 🔲 Add required env vars to `.env.example` and documentation

## Commits

- `a7ba3f55` - fix(cors): properly parse ALLOWED_ORIGINS env var to return access-control-allow-origin header
- `8b6943e6` - chore: force rebuild with build identifier

## Lessons Learned

1. **Always check required fields in Settings classes** - Missing env vars cause Pydantic validation to fail during module import
2. **Cloud Run env vars must be explicitly set** - They don't inherit from project metadata
3. **Test locally with Docker first** - Would have caught the missing env vars faster
4. **Use the `/debug/cors` pattern** - Very helpful for verifying CORS configuration in production
