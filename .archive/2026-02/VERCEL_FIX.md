# Fix Vercel 404 Errors - Step-by-Step Guide

## Problem

`https://medbilldozer.vercel.app/` and `https://medbilldozer.vercel.app/login` are returning **404 NOT_FOUND** errors.

## Root Cause

The Vercel project is deployed from a **monorepo** with the frontend in the `frontend/` subdirectory, but Vercel's project settings don't correctly specify the root directory. This causes Vercel to fail to find the `index.html` file and the `vercel.json` configuration.

## Solution: Configure Vercel Project Root Directory

### Option 1: Via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Navigate to: https://vercel.com/dashboard
   - Sign in with your account

2. **Select Your Project**
   - Find and click on your project: `medbilldozer` or `frontend`
   - Project ID: `prj_9fLqqU5RZFdfCbXcOm0zP2ePOjjt`

3. **Update Root Directory Setting**
   - Click on **Settings** (top navigation)
   - Go to **General** section
   - Find **Root Directory** setting
   - Change from: ` ` (empty or `.`)
   - Change to: `frontend`
   - Click **Save**

4. **Trigger Redeployment**
   - Go to **Deployments** tab
   - Click **Redeploy** on the latest deployment
   - OR push a new commit to trigger automatic deployment

5. **Verify**
   - Wait for deployment to complete (1-2 minutes)
   - Visit: https://medbilldozer.vercel.app/
   - Should see the app (not 404)
   - Visit: https://medbilldozer.vercel.app/login
   - Should work (React Router handles routing)

---

### Option 2: Via Vercel CLI

If you prefer using the command line:

```bash
# Install Vercel CLI (if not installed)
npm install -g vercel

# Login
vercel login

# Link to project
cd /Users/jgs/Documents/GitHub/medbilldozer/frontend
vercel link

# Deploy
vercel --prod
```

The CLI will automatically detect the `vercel.json` in the frontend directory.

---

### Option 3: Update GitHub Actions Workflow

If neither option above works, modify `.github/workflows/deploy-frontend.yml`:

```yaml
- name: Deploy to Vercel
  uses: amondnet/vercel-action@v25
  with:
    vercel-token: ${{ secrets.VERCEL_TOKEN }}
    vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
    vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
    working-directory: ./
    vercel-args: ${{ github.ref == 'refs/heads/main' && '--prod --cwd frontend' || '--cwd frontend' }}
```

Change `working-directory` from `frontend` to `./` and add `--cwd frontend` to `vercel-args`.

---

## Verification Steps

After applying the fix:

### 1. Test Root Path

```bash
curl -I https://medbilldozer.vercel.app/
```

**Expected**: `HTTP/2 200` (not 404)

### 2. Test Login Route

```bash
curl -I https://medbilldozer.vercel.app/login
```

**Expected**: `HTTP/2 200` (React Router should serve index.html)

### 3. Test Assets

```bash
curl -I https://medbilldozer.vercel.app/assets/index-Buj5yZ0P.js
```

**Expected**: `HTTP/2 200` with cache headers

### 4. Browser Test

1. Open https://medbilldozer.vercel.app/ in your browser
2. Should see the **Invite Code Gate** page (not 404)
3. Open DevTools (F12) → Network tab
4. Verify:
   - `index.html` loads (200)
   - JS/CSS assets load (200)
   - No 404 errors in console

### 5. End-to-End Test

1. Enter invite code: `MEDBILL2024`
2. Click **Continue with Google**
3. Complete authentication
4. Should reach the main dashboard (not 404)

---

## Common Issues

### Issue: Still Getting 404 After Fixing Root Directory

**Possible causes**:
1. Vercel cache not cleared
2. DNS/CDN propagation delay
3. Old deployment still active

**Solutions**:
```bash
# Force clear cache in browser (Cmd+Shift+R or Ctrl+Shift+R)
# Wait 5-10 minutes for CDN propagation
# Trigger a new deployment from Vercel dashboard
```

### Issue: Assets Load But App Shows Blank Page

**Possible causes**:
1. JavaScript errors
2. Firebase auth domain misconfigured
3. API URL incorrect

**Solutions**:
1. Open browser DevTools console
2. Check for errors
3. Verify `VITE_API_BASE_URL` in `frontend/vercel.json` matches backend URL
4. Verify Firebase auth domain includes `medbilldozer.vercel.app`

### Issue: CORS Errors in Console

**Check backend CORS**:
```bash
curl -X OPTIONS https://medbilldozer-api-4iuj3mhruq-uc.a.run.app/api/auth/login \
  -H "Origin: https://medbilldozer.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -i
```

Should include:
- `access-control-allow-origin: https://medbilldozer.vercel.app`
- `access-control-allow-credentials: true`

If not, run:
```bash
cd /Users/jgs/Documents/GitHub/medbilldozer
./scripts/deploy-and-verify.sh
```

---

## Current Configuration

### ✅ Backend (Cloud Run)
- URL: `https://medbilldozer-api-4iuj3mhruq-uc.a.run.app`
- CORS: Properly configured
- Environment: `production`
- Frontend URL: `https://medbilldozer.vercel.app`

### ⚠️ Frontend (Vercel)
- URL: `https://medbilldozer.vercel.app`
- Status: 404 (needs root directory fix)
- Configuration file: `frontend/vercel.json` ✅
- GitHub Actions: Configured ✅

---

## Next Steps

1. **Fix Vercel root directory** (see Option 1 above)
2. **Redeploy** and wait for completion
3. **Test** using verification steps
4. **Run full verification**:
   ```bash
   cd /Users/jgs/Documents/GitHub/medbilldozer
   ./scripts/deploy-and-verify.sh
   ```

---

## Support

If issues persist:
1. Check Vercel deployment logs: https://vercel.com/dashboard → Your Project → Deployments
2. Check Cloud Run logs: `gcloud run logs read medbilldozer-api --limit=50`
3. Review: [CORS_CHANGES.md](CORS_CHANGES.md) for backend CORS configuration
4. Review: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for deployment steps

---

**Last Updated**: 2026-02-21
**Status**: Backend ✅ Working | Frontend ⚠️ Needs Vercel root directory fix
