# MedBillDozer Deployment Guide

Complete step-by-step guide to deploy MedBillDozer to production.

---

## Prerequisites

Before starting, ensure you have:
- [ ] Google Cloud account with billing enabled
- [ ] Supabase account (free tier works)
- [ ] `gcloud` CLI installed and configured
- [ ] `npm` and `node` installed (v18+)
- [ ] `python` 3.11+ installed

---

## Phase 1: Firebase Setup (15 minutes)

### Step 1: Create Firebase Project

1. **Go to Firebase Console**: https://console.firebase.google.com
2. Click **"Add project"**
3. Enter project name: `medbilldozer` (or your preferred name)
4. Disable Google Analytics (optional)
5. Click **"Create project"**

### Step 2: Enable Authentication

1. In Firebase Console, navigate to **"Build" → "Authentication"**
2. Click **"Get started"**
3. Click **"Sign-in method"** tab
4. Enable **Google** provider:
   - Toggle "Google" to enabled
   - Enter support email
   - Click "Save"
5. Enable **GitHub** provider:
   - Toggle "GitHub" to enabled
   - Go to GitHub → Settings → Developer settings → OAuth Apps
   - Create new OAuth App:
     - Homepage URL: `https://medbilldozer-frontend.vercel.app`
     - Authorization callback URL: Copy from Firebase console
   - Copy Client ID and Client Secret to Firebase
   - Click "Save"

### Step 3: Configure Authorized Domains

1. In Authentication settings, click **"Settings"** tab
2. Scroll to **"Authorized domains"**
3. Add your domains:
   - `localhost` (already added)
   - `your-frontend.vercel.app` (add when deployed)
   - `your-custom-domain.com` (if applicable)

### Step 4: Get Firebase Credentials

#### For Backend (Python):

1. Go to **Project Settings** (gear icon) → **"Service accounts"**
2. Click **"Generate new private key"**
3. Download the JSON file (e.g., `medbilldozer-firebase-adminsdk.json`)
4. **Keep this file secure - DO NOT commit to git!**

Extract values for `.env`:
```json
{
  "project_id": "medbilldozer",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@medbilldozer.iam.gserviceaccount.com"
}
```

#### For Frontend (JavaScript):

1. Go to **Project Settings** → **"General"**
2. Scroll to **"Your apps"** section
3. Click **Web icon** (</>) to add a web app
4. Enter app nickname: `medbilldozer-frontend`
5. Click **"Register app"**
6. Copy the Firebase config:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "medbilldozer.firebaseapp.com",
  projectId: "medbilldozer",
  storageBucket: "medbilldozer.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdefghijklmnop"
};
```

---

## Phase 2: Supabase Setup (10 minutes)

### Step 1: Create Supabase Project

1. **Go to Supabase**: https://supabase.com
2. Click **"Start your project"** → **"New project"**
3. Fill in details:
   - Name: `medbilldozer`
   - Database Password: (generate strong password and save it!)
   - Region: Choose closest to your users
   - Pricing: Free tier
4. Click **"Create new project"** (takes ~2 minutes)

### Step 2: Get Supabase Credentials

1. Go to **Project Settings** (gear icon) → **"API"**
2. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: `eyJhbGciOi...` (for client-side, optional)
   - **service_role key**: `eyJhbGciOi...` (for backend - keep secure!)

### Step 3: Run Database Schema

1. In Supabase dashboard, click **"SQL Editor"**
2. Click **"New query"**
3. Copy contents of `/Users/jgs/Documents/GitHub/medbilldozer/sql/schema_production_api.sql`
4. Paste into SQL editor
5. Click **"Run"**
6. Verify tables created: Go to **"Table Editor"** and see:
   - `user_profiles`
   - `documents`
   - `analyses`
   - `issues`

---

## Phase 3: Google Cloud Storage Setup (10 minutes)

### Step 1: Create GCS Buckets

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"

# Create buckets
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://medbilldozer-documents
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 gs://medbilldozer-clinical

# Verify buckets created
gsutil ls
```

### Step 2: Configure CORS for Direct Uploads

```bash
# Create CORS configuration file
cat > cors.json <<EOF
[
  {
    "origin": ["http://localhost:5173", "https://your-frontend.vercel.app"],
    "method": ["GET", "PUT", "POST"],
    "responseHeader": ["Content-Type", "Authorization"],
    "maxAgeSeconds": 3600
  }
]
EOF

# Apply CORS to documents bucket
gsutil cors set cors.json gs://medbilldozer-documents

# Verify CORS applied
gsutil cors get gs://medbilldozer-documents
```

### Step 3: Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Container Registry API
gcloud services enable containerregistry.googleapis.com

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Enable Storage API
gcloud services enable storage.googleapis.com
```

---

## Phase 4: Backend Configuration (5 minutes)

### Step 1: Create Environment File

```bash
cd backend
cp .env.example .env
```

### Step 2: Edit `.env` with Your Credentials

```bash
# Open in your editor
nano .env
# or
code .env
```

Fill in all values:

```bash
# API Configuration
APP_NAME=MedBillDozer API
APP_VERSION=1.0.0
DEBUG=false

# CORS (update with your frontend URL)
ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app

# Firebase Authentication
FIREBASE_PROJECT_ID=medbilldozer
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@medbilldozer.iam.gserviceaccount.com

# Google Cloud Storage
GCS_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_DOCUMENTS=medbilldozer-documents
GCS_BUCKET_CLINICAL_IMAGES=medbilldozer-clinical

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...

# AI Providers
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
HF_API_TOKEN=hf_...

# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Important Notes:**
- For `FIREBASE_PRIVATE_KEY`, keep the `\n` characters (newlines)
- Generate `JWT_SECRET_KEY` with: `openssl rand -hex 32`
- Never commit `.env` to git!

### Step 3: Test Backend Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8080
```

Open http://localhost:8080/docs to see API documentation.

Test health endpoint:
```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "api_version": "1.0.0",
  "environment": "development"
}
```

---

## Phase 5: Deploy Backend to Cloud Run (15 minutes)

### Step 1: Create Secrets in Google Secret Manager

```bash
# Set project
gcloud config set project $PROJECT_ID

# Create secrets
echo -n "$OPENAI_API_KEY" | gcloud secrets create openai-key --data-file=-
echo -n "$SUPABASE_SERVICE_ROLE_KEY" | gcloud secrets create supabase-key --data-file=-
echo -n "$FIREBASE_PRIVATE_KEY" | gcloud secrets create firebase-key --data-file=-
echo -n "$(openssl rand -hex 32)" | gcloud secrets create jwt-secret --data-file=-

# Verify secrets created
gcloud secrets list
```

### Step 2: Build and Push Docker Image

```bash
cd backend

# Build image
gcloud builds submit --tag gcr.io/$PROJECT_ID/medbilldozer-api

# Verify image built
gcloud container images list
```

### Step 3: Deploy to Cloud Run

```bash
gcloud run deploy medbilldozer-api \
  --image gcr.io/$PROJECT_ID/medbilldozer-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars "FIREBASE_PROJECT_ID=medbilldozer,GCS_PROJECT_ID=$PROJECT_ID,GCS_BUCKET_DOCUMENTS=medbilldozer-documents,SUPABASE_URL=https://xxxxx.supabase.co,ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app,JWT_ALGORITHM=HS256" \
  --set-secrets "OPENAI_API_KEY=openai-key:latest,SUPABASE_SERVICE_ROLE_KEY=supabase-key:latest,FIREBASE_PRIVATE_KEY=firebase-key:latest,JWT_SECRET_KEY=jwt-secret:latest"
```

**Note:** Update `SUPABASE_URL` and `ALLOWED_ORIGINS` with your actual values.

### Step 4: Grant Permissions

```bash
# Get Cloud Run service account
SERVICE_ACCOUNT=$(gcloud run services describe medbilldozer-api \
  --region=us-central1 \
  --format='value(spec.template.spec.serviceAccountName)')

# Grant Storage permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/storage.objectAdmin"

# Grant Secret Manager permissions
gcloud secrets add-iam-policy-binding openai-key \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding supabase-key \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding firebase-key \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding jwt-secret \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 5: Get Backend URL

```bash
gcloud run services describe medbilldozer-api \
  --region=us-central1 \
  --format='value(status.url)'
```

Output: `https://medbilldozer-api-xxxxx-uc.a.run.app`

**Save this URL** - you'll need it for the frontend configuration.

### Step 6: Test Deployed Backend

```bash
# Test health endpoint
curl https://medbilldozer-api-xxxxx-uc.a.run.app/health

# Test API docs
open https://medbilldozer-api-xxxxx-uc.a.run.app/docs
```

---

## Phase 6: Frontend Deployment (10 minutes)

### Step 1: Configure Frontend Environment

```bash
cd frontend
cp .env.example .env.local
```

Edit `.env.local`:

```bash
# Backend API URL (from Cloud Run deployment)
VITE_API_BASE_URL=https://medbilldozer-api-xxxxx-uc.a.run.app

# Firebase Configuration (from Firebase Console)
VITE_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
VITE_FIREBASE_AUTH_DOMAIN=medbilldozer.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=medbilldozer
VITE_FIREBASE_STORAGE_BUCKET=medbilldozer.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:abcdefghijklmnop
```

### Step 2: Test Frontend Locally

```bash
# Install dependencies
npm install

# Run dev server
npm run dev
```

Open http://localhost:5173 and test:
1. Click "Continue with Google"
2. Login with your Google account
3. Upload a test PDF
4. Verify it appears in document list

### Step 3: Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

Follow prompts:
- Link to existing project? **No**
- Project name: `medbilldozer-frontend`
- Directory: `./`
- Override settings? **No**

**Set environment variables in Vercel dashboard:**

1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add all variables from `.env.local`:
   - `VITE_API_BASE_URL`
   - `VITE_FIREBASE_API_KEY`
   - `VITE_FIREBASE_AUTH_DOMAIN`
   - `VITE_FIREBASE_PROJECT_ID`
   - `VITE_FIREBASE_STORAGE_BUCKET`
   - `VITE_FIREBASE_MESSAGING_SENDER_ID`
   - `VITE_FIREBASE_APP_ID`

5. Redeploy: `vercel --prod`

### Step 4: Update CORS and Firebase Authorized Domains

**Update Backend CORS:**
```bash
# Get your Vercel URL
VERCEL_URL="https://medbilldozer-frontend.vercel.app"

# Redeploy backend with updated CORS
gcloud run deploy medbilldozer-api \
  --image gcr.io/$PROJECT_ID/medbilldozer-api \
  --region us-central1 \
  --update-env-vars "ALLOWED_ORIGINS=http://localhost:5173,$VERCEL_URL"
```

**Update Firebase Authorized Domains:**
1. Go to Firebase Console → Authentication → Settings
2. Add your Vercel URL to authorized domains

**Update GCS CORS:**
```bash
# Update cors.json
cat > cors.json <<EOF
[
  {
    "origin": ["http://localhost:5173", "$VERCEL_URL"],
    "method": ["GET", "PUT", "POST"],
    "responseHeader": ["Content-Type", "Authorization"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set cors.json gs://medbilldozer-documents
```

---

## Phase 7: End-to-End Testing (10 minutes)

### Test Checklist

1. **Authentication:**
   - [ ] Open `https://your-frontend.vercel.app`
   - [ ] Click "Continue with Google"
   - [ ] Login with Google account
   - [ ] Verify redirected to dashboard
   - [ ] Check user menu shows your name

2. **Document Upload:**
   - [ ] Click or drag a PDF file (medical bill)
   - [ ] Verify progress indicator shows
   - [ ] Verify "Upload successful" message
   - [ ] Verify document appears in list

3. **Document Analysis:**
   - [ ] Select uploaded document (checkbox)
   - [ ] Click "Analyze" button
   - [ ] Verify redirected to analysis page
   - [ ] Verify "Analyzing your documents" message
   - [ ] Wait 30-60 seconds for completion
   - [ ] Verify results display:
     - [ ] Total savings amount
     - [ ] Issues count
     - [ ] Issue cards with details

4. **Mobile Test:**
   - [ ] Open on mobile device
   - [ ] Test login flow
   - [ ] Test document upload
   - [ ] Verify responsive layout

5. **Logout:**
   - [ ] Click user menu
   - [ ] Click "Logout"
   - [ ] Verify redirected to login page

---

## Troubleshooting

### Backend Issues

**Issue: "Invalid Firebase token"**
```bash
# Verify Firebase credentials
cat backend/.env | grep FIREBASE

# Test Firebase Admin SDK
python -c "import firebase_admin; print('OK')"
```

**Issue: "Permission denied (GCS)"**
```bash
# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:$SERVICE_ACCOUNT"
```

**Issue: "CORS error"**
```bash
# Verify CORS configuration
gsutil cors get gs://medbilldozer-documents

# Update CORS
gsutil cors set cors.json gs://medbilldozer-documents
```

### Frontend Issues

**Issue: "Network Error" when calling API**
- Check `VITE_API_BASE_URL` is correct
- Verify backend CORS includes frontend URL
- Check browser console for error details

**Issue: "Firebase auth not working"**
- Verify Firebase config in `.env.local`
- Check Firebase authorized domains
- Clear browser cache and cookies

**Issue: "Upload fails"**
- Check GCS CORS configuration
- Verify bucket exists: `gsutil ls`
- Check browser console for errors

---

## Monitoring & Logs

### Backend Logs (Cloud Run)

```bash
# View recent logs
gcloud run services logs read medbilldozer-api \
  --region=us-central1 \
  --limit=50

# Stream logs in real-time
gcloud run services logs tail medbilldozer-api \
  --region=us-central1
```

### Frontend Logs (Vercel)

1. Go to Vercel dashboard
2. Select your project
3. Click on deployment
4. View "Build Logs" or "Function Logs"

### Database Logs (Supabase)

1. Go to Supabase dashboard
2. Click "Logs" in sidebar
3. View "Postgres Logs" or "API Logs"

---

## Updating Deployment

### Update Backend

```bash
cd backend

# Make your code changes

# Rebuild and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/medbilldozer-api
gcloud run deploy medbilldozer-api \
  --image gcr.io/$PROJECT_ID/medbilldozer-api \
  --region=us-central1
```

### Update Frontend

```bash
cd frontend

# Make your code changes

# Redeploy
vercel --prod
```

---

## Security Checklist

- [ ] All API keys stored in Secret Manager (not in code)
- [ ] `.env` files added to `.gitignore`
- [ ] HTTPS enabled (automatic with Cloud Run/Vercel)
- [ ] CORS configured with specific origins (not `*`)
- [ ] JWT secret is random and secure
- [ ] Firebase service account JSON not committed to git
- [ ] Supabase Row Level Security policies enabled
- [ ] Cloud Run requires authentication for sensitive endpoints

---

## Cost Estimates

### Free Tier Limits

- **Firebase Auth**: 50,000 MAU free
- **Supabase**: 500 MB database, 1 GB file storage, 2 GB bandwidth/month
- **Cloud Run**: 2 million requests/month, 360,000 GB-seconds compute
- **Cloud Storage**: 5 GB free, then $0.020 per GB/month
- **Vercel**: Unlimited bandwidth for personal projects

### Estimated Monthly Costs (after free tier)

| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run (Backend) | 100K requests/month | $0 (within free tier) |
| Cloud Storage | 10 GB storage | $0.20 |
| Vercel (Frontend) | Unlimited | $0 (free tier) |
| Supabase | Free tier | $0 |
| **Total** | | **~$0.20/month** |

---

## Success! 🎉

Your MedBillDozer application is now deployed to production!

- **Frontend**: https://your-frontend.vercel.app
- **Backend**: https://medbilldozer-api-xxxxx-uc.a.run.app
- **API Docs**: https://medbilldozer-api-xxxxx-uc.a.run.app/docs

Next steps:
- Set up custom domain (optional)
- Configure monitoring and alerts
- Set up CI/CD pipeline
- Add more features!
