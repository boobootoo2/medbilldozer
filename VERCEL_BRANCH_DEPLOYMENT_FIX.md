# Vercel Branch Deployment Fix

## Problem
When deploying from a new Git branch (e.g., `develop`), you get:
1. ❌ CORS error: "No 'Access-Control-Allow-Origin' header"
2. ❌ Firebase error: "auth/unauthorized-domain"

## Root Cause
Each Vercel branch gets a unique preview URL that needs to be authorized in:
- Backend CORS configuration (Cloud Run)
- Firebase authorized domains

---

## ✅ Solution: 2 Steps Required

### Step 1: Add to Cloud Run ALLOWED_ORIGINS

**Option A: Cloud Console (Easiest)**
1. Go to: https://console.cloud.google.com/run/detail/us-central1/medbilldozer-api/variables
2. Click "Edit & Deploy New Revision"
3. Find `ALLOWED_ORIGINS` environment variable
4. Add your new Vercel URL to the comma-separated list
5. Click "Deploy"

**Option B: Command Line**
```bash
# Create YAML file
cat > cors-update.yaml <<EOF
ALLOWED_ORIGINS: "https://medbilldozer.vercel.app,https://medbilldozer-git-v031-john-shultzs-projects.vercel.app,https://medbilldozer-git-v03-john-shultzs-projects.vercel.app,https://medbilldozer-git-develop-john-shultzs-projects.vercel.app,http://localhost:3000,http://localhost:5173"
EOF

# Update Cloud Run
gcloud run services update medbilldozer-api \
  --region=us-central1 \
  --env-vars-file=cors-update.yaml
```

---

### Step 2: Add to Firebase Authorized Domains

**Firebase Console:**
1. Go to: https://console.firebase.google.com/project/medbilldozer/authentication/settings
2. Scroll to "Authorized domains"
3. Click "Add domain"
4. Enter: `medbilldozer-git-develop-john-shultzs-projects.vercel.app`
5. Click "Add"

---

## 📋 Vercel URL Pattern

Vercel preview deployments follow this pattern:
```
https://medbilldozer-git-{BRANCH_NAME}-john-shultzs-projects.vercel.app
```

**Examples:**
- `develop` → `https://medbilldozer-git-develop-john-shultzs-projects.vercel.app`
- `v0.3.1` → `https://medbilldozer-git-v031-john-shultzs-projects.vercel.app`
- `feature-auth` → `https://medbilldozer-git-feature-auth-john-shultzs-projects.vercel.app`

**Note:** Branch names with dots/periods are sanitized (`.` becomes empty)

---

## 🔄 Automated Solution (Future)

To avoid manual updates for each branch, consider:

### Option 1: Wildcard CORS (Not Recommended for Production)
```python
# In config.py (only for dev/staging)
if environment == "staging":
    origins.append("https://*.vercel.app")  # FastAPI supports wildcards
```

### Option 2: Pattern-Based Validation
```python
# In config.py
import re

def is_valid_vercel_preview(origin: str) -> bool:
    """Check if origin matches Vercel preview pattern."""
    pattern = r"https://medbilldozer-git-[\w-]+-john-shultzs-projects\.vercel\.app"
    return bool(re.match(pattern, origin))

# In all_cors_origins property
if environment == "staging":
    # Allow all Vercel previews in staging
    # Would need custom CORS middleware to validate dynamically
```

### Option 3: GitHub Actions to Sync
Create a GitHub Action that automatically updates Cloud Run and Firebase when new branches are deployed.

---

## 🧪 Testing After Fix

1. **Test CORS:**
   ```bash
   curl -X OPTIONS https://medbilldozer-api-360553024921.us-central1.run.app/api/auth/login \
     -H "Origin: https://medbilldozer-git-develop-john-shultzs-projects.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -i | grep "access-control-allow-origin"
   ```

   Expected: `access-control-allow-origin: https://medbilldozer-git-develop-john-shultzs-projects.vercel.app`

2. **Test Frontend:**
   - Go to your Vercel preview URL
   - Try logging in with Google
   - Should work without errors

---

## 📝 Current Authorized URLs

### Backend CORS (Cloud Run)
```
https://medbilldozer.vercel.app
https://medbilldozer-git-v031-john-shultzs-projects.vercel.app
https://medbilldozer-git-v03-john-shultzs-projects.vercel.app
https://medbilldozer-git-develop-john-shultzs-projects.vercel.app
http://localhost:3000
http://localhost:5173
```

### Firebase Authorized Domains
**Need to Add:**
- `medbilldozer-git-develop-john-shultzs-projects.vercel.app`
- `medbilldozer-git-v031-john-shultzs-projects.vercel.app` (if not already)
- `medbilldozer-git-v03-john-shultzs-projects.vercel.app` (if not already)

---

## 🚀 Quick Checklist for New Branches

When deploying a new branch:
- [ ] Note the Vercel preview URL
- [ ] Add to Cloud Run `ALLOWED_ORIGINS`
- [ ] Add to Firebase Authorized Domains
- [ ] Test login functionality
- [ ] Check browser console for CORS/Firebase errors

---

## ⚠️ Common Mistakes

1. **Forgetting the `https://` prefix** - URLs must include protocol
2. **Using HTTP instead of HTTPS** - Vercel uses HTTPS
3. **Forgetting Firebase** - Both CORS and Firebase must be updated
4. **Typos in branch name** - Double-check the exact Vercel URL

---

## 📚 Related Documentation

- [Vercel Preview Deployments](https://vercel.com/docs/deployments/preview-deployments)
- [Firebase Authorized Domains](https://firebase.google.com/docs/auth/web/redirect-best-practices#verify-domain)
- [CORS Configuration](./CORS_FIX_COMPLETE.md)
