# Quick CORS Fix for Vercel Preview Deployments

## Problem

Frontend at `https://medbilldozer-git-v031-john-shultzs-projects.vercel.app` is blocked by CORS because it's not in the backend's allowed origins list.

## Quick Fix Options

### Option 1: Update via Google Cloud Console (FASTEST - 2 minutes)

1. Go to: https://console.cloud.google.com/run/detail/us-central1/medbilldozer-api/variables-and-secrets

2. Click **Edit & Deploy New Revision**

3. In the **Variables & Secrets** tab, find `ALLOWED_ORIGINS`

4. Update the value to:
   ```
   https://medbilldozer.vercel.app,https://medbilldozer-git-v031-john-shultzs-projects.vercel.app,https://medbilldozer-git-v03-john-shultzs-projects.vercel.app,http://localhost:3000,http://localhost:5173
   ```

5. Click **Deploy** (wait 1-2 minutes)

6. Refresh your frontend and try logging in again

### Option 2: Deploy from Source (5-10 minutes)

The code has been updated to include Vercel preview URLs. Deploy the latest version:

```bash
cd /Users/jgs/Documents/GitHub/medbilldozer/backend

gcloud run deploy medbilldozer-api \
  --source . \
  --region=us-central1 \
  --allow-unauthenticated
```

### Option 3: Use Main Production URL (Workaround)

Instead of using the v0.3.1 preview deployment, use the main production deployment which should have CORS configured:

- Open: `https://medbilldozer.vercel.app/` (instead of the preview URL)

---

## After Fix - Test

```bash
# Test CORS from your preview deployment
curl -X OPTIONS https://medbilldozer-api-4iuj3mhruq-uc.a.run.app/api/auth/login \
  -H "Origin: https://medbilldozer-git-v031-john-shultzs-projects.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -i

# Should see:
# access-control-allow-origin: https://medbilldozer-git-v031-john-shultzs-projects.vercel.app
```

---

## Why This Happened

- Vercel creates unique URLs for each branch deployment
- v0.3.1 branch: `https://medbilldozer-git-v031-john-shultzs-projects.vercel.app`
- v0.3 branch: `https://medbilldozer-git-v03-john-shultzs-projects.vercel.app`
- main branch: `https://medbilldozer.vercel.app`

The backend needs to explicitly allow each of these URLs in its CORS configuration.

---

## Permanent Solution

The code has been updated to automatically include these preview URLs in production. The next deployment will pick up this change.

**Updated file**: `backend/app/config.py` (lines 96-106)

```python
elif env == "production":
    origins.extend([
        "https://medbilldozer.com",
        "https://www.medbilldozer.com",
        "https://medbilldozer.vercel.app",
        "https://medbilldozer-git-v03-john-shultzs-projects.vercel.app",
        "https://medbilldozer-git-v031-john-shultzs-projects.vercel.app",
    ])
```

---

**RECOMMENDED**: Use **Option 1** (Google Cloud Console) for immediate fix, takes 2 minutes.
