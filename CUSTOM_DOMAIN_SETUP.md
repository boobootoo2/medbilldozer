# Custom Domain Setup for Vercel

This guide helps you set up a custom domain to eliminate the need for constantly adding new Vercel preview URLs to Firebase.

## Benefits

- ✅ One domain to configure (instead of dozens of preview URLs)
- ✅ No more auth errors on new deployments
- ✅ Professional domain instead of `*.vercel.app`
- ✅ Consistent CORS configuration

---

## Prerequisites

- Domain name (e.g., `medbilldozer.com`)
- Access to domain DNS settings
- Vercel account with project access

---

## Step 1: Add Custom Domain to Vercel

### Option A: Using Vercel Dashboard

1. Go to your Vercel project: https://vercel.com/john-shultzs-projects/medbilldozer
2. Click **Settings** → **Domains**
3. Add your custom domain:
   - **Production:** `app.medbilldozer.com` or `medbilldozer.com`
   - Click **Add**

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI if needed
npm i -g vercel

# Login
vercel login

# Add domain to project
vercel domains add app.medbilldozer.com --project=medbilldozer
```

---

## Step 2: Configure DNS Records

Add these DNS records to your domain provider (e.g., Namecheap, GoDaddy, Cloudflare):

### For Root Domain (`medbilldozer.com`)

```
Type: A
Name: @
Value: 76.76.21.21
```

### For Subdomain (`app.medbilldozer.com`)

```
Type: CNAME
Name: app
Value: cname.vercel-dns.com
```

**Verification:** After adding records, Vercel will automatically verify (may take a few minutes to hours for DNS propagation).

---

## Step 3: Configure Production Branch

In Vercel project settings:

1. **Settings** → **Git**
2. Set **Production Branch** to: `main`
3. This ensures `main` branch deploys to `app.medbilldozer.com`

---

## Step 4: Update Firebase Authorized Domains

Now you only need these domains in Firebase:

1. Go to: https://console.firebase.google.com/project/medbilldozer/authentication/settings
2. Under **Authorized domains**, keep only:
   - `app.medbilldozer.com` (your custom domain)
   - `localhost` (for local development)
   - `medbilldozer.firebaseapp.com` (Firebase default)
3. **Remove** all the Vercel preview URLs:
   - ❌ `medbilldozer-git-*-john-shultzs-projects.vercel.app`
   - ❌ `medbilldozer-*-john-shultzs-projects.vercel.app`

---

## Step 5: Update Backend CORS Configuration

Update your backend to use the custom domain:

**File:** `cloud-run-complete-env.yaml`

```yaml
ALLOWED_ORIGINS: "https://app.medbilldozer.com,http://localhost:3000,http://localhost:5173"
ENVIRONMENT: "production"
FRONTEND_URL: "https://app.medbilldozer.com"
FIREBASE_PROJECT_ID: "medbilldozer"
GCS_PROJECT_ID: "medbilldozer"
```

Then deploy:

```bash
gcloud run services update medbilldozer-api \
  --region=us-central1 \
  --env-vars-file=cloud-run-complete-env.yaml
```

---

## Step 6: Update Frontend Environment Variables (if needed)

If you have any hardcoded URLs in your frontend:

**File:** `frontend/.env.production`

```env
VITE_API_URL=https://medbilldozer-api-360553024921.us-central1.run.app
VITE_FRONTEND_URL=https://app.medbilldozer.com
```

---

## Step 7: Test the Setup

1. **Deploy to main branch:**
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```

2. **Wait for Vercel deployment** (automatic)

3. **Visit your custom domain:**
   - Open: https://app.medbilldozer.com
   - Try Google Sign-In
   - Upload a document
   - Should work without any auth/CORS errors!

---

## Preview Deployments

### Important Note About Previews

With this setup:
- ✅ **Production deployments** (main branch) → `app.medbilldozer.com` (with auth)
- ⚠️ **Preview deployments** (other branches) → `*.vercel.app` (NO auth by default)

### Options for Preview Deployments

**Option 1: Disable Auth on Previews** (Simplest)
- Preview deployments won't have Google Sign-In
- Good for testing UI/features that don't require auth
- Most common approach for most apps

**Option 2: Custom Preview Domain** (Advanced)
- Set up `preview.medbilldozer.com`
- Configure Vercel to use it for all preview deployments
- Add to Firebase authorized domains

**To configure preview domain:**

In `vercel.json`:
```json
{
  "github": {
    "autoAlias": true
  },
  "alias": [
    "preview.medbilldozer.com"
  ]
}
```

**Option 3: Continue Manual Approach**
- Keep adding preview URLs to Firebase when needed for testing auth
- Only do this when you specifically need to test auth on a preview

---

## Troubleshooting

### DNS Not Propagating

```bash
# Check DNS status
dig app.medbilldozer.com

# Expected output should show Vercel's IP or CNAME
```

Wait up to 48 hours for full DNS propagation (usually much faster).

### Still Getting Auth Errors

1. Verify domain is added to Firebase
2. Check browser console for the exact unauthorized domain
3. Ensure you're accessing via the custom domain (not `*.vercel.app`)

### CORS Errors

1. Verify Cloud Run ALLOWED_ORIGINS includes your custom domain
2. Check `/debug/cors` endpoint:
   ```bash
   curl https://medbilldozer-api-360553024921.us-central1.run.app/debug/cors
   ```

---

## Cost

- **Vercel Custom Domain:** Free on all plans
- **Domain Registration:** ~$10-15/year (from your domain provider)
- **DNS/SSL:** Free (Vercel provides automatic HTTPS)

---

## Migration Checklist

- [ ] Purchase domain (if you don't have one)
- [ ] Add custom domain to Vercel
- [ ] Configure DNS records
- [ ] Wait for DNS verification
- [ ] Update Firebase authorized domains
- [ ] Update backend CORS configuration
- [ ] Deploy backend with new CORS
- [ ] Merge to main and test
- [ ] Clean up old Vercel preview URLs from Firebase

---

## Benefits After Setup

✅ One-time DNS configuration
✅ No more adding preview URLs
✅ Professional domain
✅ Automatic SSL/HTTPS
✅ Better SEO
✅ Cleaner CORS configuration

---

**Questions?** Check [Vercel Custom Domains Docs](https://vercel.com/docs/concepts/projects/domains)
