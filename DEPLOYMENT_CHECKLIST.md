# CORS Deployment Checklist

Follow this checklist to update your hosting environments with the new CORS configuration.

## 📋 Pre-Deployment Verification

- [ ] Test CORS locally and confirm it works
- [ ] Commit all CORS changes to your repository
- [ ] Have your frontend URLs ready (production and staging)

---

## 🚀 Cloud Run (Backend API)

### Check Current Configuration

```bash
# View current environment variables
gcloud run services describe medbilldozer-api \
  --region=YOUR_REGION \
  --format="value(spec.template.spec.containers[0].env)"
```

### Update Environment Variables

**Method 1: Using gcloud CLI (Recommended)**

```bash
# Set your Cloud Run region
export REGION="us-central1"  # Change to your region

# Update environment variables
gcloud run services update medbilldozer-api \
  --region=$REGION \
  --update-env-vars ENVIRONMENT=production \
  --update-env-vars FRONTEND_URL=https://medbilldozer.vercel.app \
  --update-env-vars BACKEND_CORS_ORIGINS=[]
```

**Method 2: Using Google Cloud Console**

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click on your service: `medbilldozer-api`
3. Click **"Edit & Deploy New Revision"**
4. Go to **"Variables & Secrets"** tab
5. Add/update these environment variables:
   - `ENVIRONMENT` = `production`
   - `FRONTEND_URL` = `https://medbilldozer.vercel.app`
   - `BACKEND_CORS_ORIGINS` = `[]`
6. Click **"Deploy"**

### Verify Deployment

```bash
# Check the service is healthy
curl https://YOUR-SERVICE-URL.run.app/health

# Test CORS
curl -X OPTIONS https://YOUR-SERVICE-URL.run.app/api/auth/login \
  -H "Origin: https://medbilldozer.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -i
```

**Checklist:**
- [ ] `ENVIRONMENT` is set to `production`
- [ ] `FRONTEND_URL` is set to your Vercel URL
- [ ] `BACKEND_CORS_ORIGINS` is set to `[]`
- [ ] Service deployed successfully
- [ ] Health check returns 200
- [ ] CORS preflight test succeeds

---

## 🔵 Vercel (Frontend)

### Check Current Configuration

```bash
# List current environment variables
vercel env ls
```

### Update if Needed

Your frontend likely just needs the API URL. Verify it's set:

**Method 1: Using Vercel CLI**

```bash
# Check if VITE_API_BASE_URL is set
vercel env ls

# If not set or incorrect, add it:
vercel env add VITE_API_BASE_URL production
# When prompted, enter: https://YOUR-SERVICE-URL.run.app
```

**Method 2: Using Vercel Dashboard**

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project: `medbilldozer`
3. Go to **Settings** → **Environment Variables**
4. Verify/add:
   - Variable: `VITE_API_BASE_URL`
   - Value: `https://YOUR-SERVICE-URL.run.app`
   - Environment: `Production`

**Checklist:**
- [ ] `VITE_API_BASE_URL` is set to your Cloud Run URL
- [ ] Variable is available in Production environment
- [ ] Redeploy frontend if variable was added/changed

---

## 🧪 Staging Environment (If Applicable)

### Cloud Run Staging Backend

```bash
# Update staging service
gcloud run services update medbilldozer-api-staging \
  --region=$REGION \
  --update-env-vars ENVIRONMENT=staging \
  --update-env-vars FRONTEND_URL=https://medbilldozer-git-staging.vercel.app \
  --update-env-vars BACKEND_CORS_ORIGINS=[]
```

### Vercel Staging Frontend

Vercel preview deployments automatically get environment variables marked for "Preview". No changes needed unless you have a dedicated staging deployment.

**Checklist:**
- [ ] Staging backend has `ENVIRONMENT=staging`
- [ ] Staging `FRONTEND_URL` matches your staging/preview URL
- [ ] Preview deployments work correctly

---

## 🔍 Post-Deployment Testing

### 1. Test Production Backend CORS

```bash
# Replace with your actual URLs
BACKEND_URL="https://YOUR-SERVICE.run.app"
FRONTEND_URL="https://medbilldozer.vercel.app"

# Test preflight
curl -X OPTIONS $BACKEND_URL/api/auth/login \
  -H "Origin: $FRONTEND_URL" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization, Content-Type" \
  -i

# Should see:
# access-control-allow-origin: https://medbilldozer.vercel.app
# access-control-allow-credentials: true
```

### 2. Test from Frontend

1. Open your production frontend: `https://medbilldozer.vercel.app`
2. Open browser DevTools (F12) → Console tab
3. Run this test:

```javascript
fetch('https://YOUR-BACKEND.run.app/health', {
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' }
})
  .then(r => r.json())
  .then(data => console.log('✅ CORS working:', data))
  .catch(err => console.error('❌ CORS error:', err))
```

4. Check **Network** tab for the request:
   - Should see OPTIONS request (preflight) with 200 status
   - Should see actual request with correct CORS headers
   - No CORS errors in console

### 3. Test Authentication Flow

1. Try logging in through your frontend
2. Make an authenticated API request
3. Verify no CORS errors occur

**Checklist:**
- [ ] Preflight requests return 200 with correct headers
- [ ] Actual requests include CORS headers
- [ ] No CORS errors in browser console
- [ ] Authentication works end-to-end
- [ ] `X-Correlation-ID` header is visible in responses

---

## 🚨 Troubleshooting

### Issue: CORS still failing after deployment

**Check:**
```bash
# 1. Verify environment variables are actually set
gcloud run services describe medbilldozer-api --format="value(spec.template.spec.containers[0].env)"

# 2. Check recent logs
gcloud run logs read medbilldozer-api --limit=50

# 3. Look for startup errors
gcloud run logs read medbilldozer-api --limit=50 | grep -i "error\|cors\|environment"
```

**Common fixes:**
- Ensure `BACKEND_CORS_ORIGINS=[]` not `BACKEND_CORS_ORIGINS=""` (empty array vs empty string)
- Restart the service after changing variables
- Clear browser cache / try in incognito mode
- Verify frontend URL is EXACTLY correct (no trailing slash, correct protocol)

---

### Issue: "Origin not allowed" error

**Debug:**
```bash
# SSH into your backend or add debug logging
# In backend/app/main.py, temporarily add:
@app.on_event("startup")
async def startup_debug():
    logger.info(f"CORS Origins: {settings.all_cors_origins}")
```

Then check logs:
```bash
gcloud run logs read medbilldozer-api --limit=10
```

---

### Issue: Environment variable not taking effect

**Verify:**
1. Variable is set in Cloud Run console
2. Service was redeployed after setting variable
3. Variable name is correct (uppercase: `ENVIRONMENT` not `environment`)
4. No typos in JSON array: `[]` not `[ ]` or `[  ]`

---

## 📝 Deployment Commands Reference

### Quick Deploy Script

Save as `scripts/deploy-backend-cors.sh`:

```bash
#!/bin/bash
set -e

# Configuration
PROJECT_ID="medbilldozer"
SERVICE_NAME="medbilldozer-api"
REGION="us-central1"  # Change to your region
FRONTEND_URL="https://medbilldozer.vercel.app"

echo "🚀 Deploying CORS configuration to Cloud Run..."

# Update environment variables
gcloud run services update $SERVICE_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --update-env-vars ENVIRONMENT=production \
  --update-env-vars FRONTEND_URL=$FRONTEND_URL \
  --update-env-vars BACKEND_CORS_ORIGINS=[]

echo "✅ Environment variables updated"

# Wait for deployment
echo "⏳ Waiting for service to be ready..."
gcloud run services describe $SERVICE_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --format="value(status.url)"

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --project=$PROJECT_ID \
  --region=$REGION \
  --format="value(status.url)")

echo ""
echo "✅ Deployment complete!"
echo "   Service URL: $SERVICE_URL"
echo ""
echo "🧪 Testing CORS..."

# Test CORS
curl -X OPTIONS $SERVICE_URL/api/auth/login \
  -H "Origin: $FRONTEND_URL" \
  -H "Access-Control-Request-Method: POST" \
  -s -o /dev/null -w "   HTTP Status: %{http_code}\n"

echo ""
echo "🎉 Done! Test your frontend at $FRONTEND_URL"
```

Make it executable:
```bash
chmod +x scripts/deploy-backend-cors.sh
./scripts/deploy-backend-cors.sh
```

---

## ✅ Final Checklist

### Backend (Cloud Run)
- [ ] `ENVIRONMENT=production` set in Cloud Run
- [ ] `FRONTEND_URL` set to your Vercel deployment URL
- [ ] `BACKEND_CORS_ORIGINS=[]` set
- [ ] Service redeployed and healthy
- [ ] CORS preflight test succeeds
- [ ] Backend logs show correct environment

### Frontend (Vercel)
- [ ] `VITE_API_BASE_URL` points to Cloud Run URL
- [ ] Frontend can reach backend /health endpoint
- [ ] No CORS errors in browser console
- [ ] Authentication flow works

### Testing
- [ ] Preflight (OPTIONS) requests return 200
- [ ] Actual requests include CORS headers
- [ ] `access-control-allow-origin` matches frontend URL
- [ ] `access-control-allow-credentials: true` present
- [ ] Login/authenticated requests work

---

## 🔄 Rollback Plan (If Something Goes Wrong)

### Quick Rollback

```bash
# Rollback to previous revision
gcloud run services update-traffic medbilldozer-api \
  --to-revisions PREVIOUS_REVISION=100

# Or set back to old ALLOWED_ORIGINS temporarily
gcloud run services update medbilldozer-api \
  --update-env-vars ALLOWED_ORIGINS="http://localhost:3000,https://medbilldozer.vercel.app"
```

The old `ALLOWED_ORIGINS` variable is still in the code as a fallback (marked deprecated), so if something breaks, you can temporarily use it while debugging.

---

## 📞 Need Help?

If you run into issues:
1. Check [CORS_VERIFICATION.md](CORS_VERIFICATION.md) for testing steps
2. Review [CORS_CHANGES.md](CORS_CHANGES.md) for configuration details
3. Check Cloud Run logs: `gcloud run logs read medbilldozer-api --limit=100`
4. Test locally first with production-like settings

---

**Last Updated:** 2026-02-19
**Related Docs:** [CORS_CHANGES.md](CORS_CHANGES.md), [CORS_VERIFICATION.md](CORS_VERIFICATION.md)
