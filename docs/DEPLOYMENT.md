# MedBillDozer Deployment Guide

## Overview

- **Frontend**: Vercel (React + Vite SPA)
- **Backend**: Google Cloud Run (FastAPI)
- **Database**: Supabase (PostgreSQL)
- **Storage**: Google Cloud Storage
- **Auth**: Firebase Authentication

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Google Cloud Project**: Create at [console.cloud.google.com](https://console.cloud.google.com)
3. **Supabase Project**: Already set up
4. **Firebase Project**: Already set up

## Frontend Deployment (Vercel)

### Option 1: Vercel Dashboard (Easiest)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Set root directory to `frontend`
4. Add environment variables:
   ```
   VITE_API_BASE_URL=https://your-backend-url.run.app
   VITE_FIREBASE_API_KEY=...
   VITE_FIREBASE_AUTH_DOMAIN=...
   VITE_FIREBASE_PROJECT_ID=...
   VITE_FIREBASE_STORAGE_BUCKET=...
   VITE_FIREBASE_MESSAGING_SENDER_ID=...
   VITE_FIREBASE_APP_ID=...
   VITE_FIREBASE_MEASUREMENT_ID=...
   ```
5. Click "Deploy"

### Option 2: Vercel CLI

```bash
cd frontend
npm i -g vercel
vercel login
vercel --prod
```

### GitHub Actions Setup

Add these secrets to your GitHub repository:
- `VERCEL_TOKEN` - Get from [vercel.com/account/tokens](https://vercel.com/account/tokens)
- `VERCEL_ORG_ID` - Find in Vercel project settings
- `VERCEL_PROJECT_ID` - Find in Vercel project settings
- `VITE_*` environment variables (same as above)

## Backend Deployment (Google Cloud Run)

### Prerequisites

1. Enable required APIs:
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable secretmanager.googleapis.com
   ```

2. Create secrets in Google Secret Manager:
   ```bash
   echo -n "your-firebase-private-key" | gcloud secrets create firebase-private-key --data-file=-
   echo -n "your-firebase-client-email" | gcloud secrets create firebase-client-email --data-file=-
   echo -n "your-supabase-key" | gcloud secrets create supabase-service-role-key --data-file=-
   echo -n "your-jwt-secret" | gcloud secrets create jwt-secret-key --data-file=-
   echo -n "your-openai-key" | gcloud secrets create openai-api-key --data-file=-
   echo -n "your-gemini-key" | gcloud secrets create gemini-api-key --data-file=-
   ```

### Manual Deployment

```bash
# Set your project ID
export PROJECT_ID=medbilldozer

# Build and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/medbilldozer-api backend/

# Deploy to Cloud Run
gcloud run deploy medbilldozer-api \
  --image gcr.io/$PROJECT_ID/medbilldozer-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars "DEBUG=false,ENVIRONMENT=production" \
  --set-secrets "FIREBASE_PRIVATE_KEY=firebase-private-key:latest,SUPABASE_SERVICE_ROLE_KEY=supabase-service-role-key:latest,JWT_SECRET_KEY=jwt-secret-key:latest"
```

### GitHub Actions Setup

Add these secrets to your GitHub repository:
- `GCP_PROJECT_ID` - Your GCP project ID
- `GCP_WORKLOAD_IDENTITY_PROVIDER` - Workload Identity Provider (see below)
- `GCP_SERVICE_ACCOUNT` - Service account email

#### Set up Workload Identity Federation

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Create Workload Identity Pool
gcloud iam workload-identity-pools create github-pool \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create Workload Identity Provider
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"

# Bind service account
gcloud iam service-accounts add-iam-policy-binding \
  github-actions@$PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_GITHUB_USERNAME/medbilldozer"
```

## Environment Variables

### Frontend (.env)
```bash
VITE_API_BASE_URL=https://your-backend-url.run.app
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=medbilldozer.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=medbilldozer
VITE_FIREBASE_STORAGE_BUCKET=medbilldozer.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
VITE_FIREBASE_MEASUREMENT_ID=...
```

### Backend (.env)
```bash
# Firebase
FIREBASE_PROJECT_ID=medbilldozer
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-...@medbilldozer.iam.gserviceaccount.com

# Supabase
SUPABASE_URL=https://zrhlpitzonhftigmdvgz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Google Cloud Storage
GCS_PROJECT_ID=medbilldozer
GCS_BUCKET_DOCUMENTS=medbilldozer.appspot.com
GCS_BUCKET_CLINICAL_IMAGES=medbilldozer.appspot.com

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI APIs (Optional)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# App Config
DEBUG=false
ENVIRONMENT=production
```

## Post-Deployment

1. **Update CORS**: Add your Vercel URL to backend CORS settings
2. **Update Firebase Auth**: Add Vercel URL to authorized domains
3. **Test**: Verify authentication, upload, and analysis flows
4. **Monitor**: Check Cloud Run logs and metrics

## Cost Estimates

### Vercel
- **Free tier**: 100GB bandwidth, unlimited requests
- **Pro**: $20/month if exceeded

### Google Cloud Run
- **First 2M requests/month**: Free
- **After free tier**: ~$0.00002400/request
- **Estimated**: $10-50/month for moderate usage

### Supabase
- **Free tier**: 500MB database, 1GB file storage
- **Pro**: $25/month for more resources

## Troubleshooting

### Frontend shows "Network Error"
- Check `VITE_API_BASE_URL` points to correct Cloud Run URL
- Verify backend CORS allows frontend domain

### Backend "Secret not found"
- Ensure all secrets exist in Secret Manager
- Verify service account has `secretmanager.secretAccessor` role

### "Authentication failed"
- Check Firebase credentials are correct
- Verify Supabase connection string and key

## CI/CD Flow

1. **Push to `main` branch** → Auto-deploy to production
2. **Push to `v0.3` branch** → Auto-deploy to staging
3. **Pull Request** → Deploy preview (Vercel only)

## Monitoring

- **Frontend**: Vercel Analytics Dashboard
- **Backend**: Google Cloud Run Metrics & Logs
- **Database**: Supabase Dashboard

## Rollback

```bash
# Rollback backend to previous revision
gcloud run services update-traffic medbilldozer-api \
  --to-revisions=medbilldozer-api-00001-xyz=100 \
  --region us-central1

# Rollback frontend
vercel rollback
```
