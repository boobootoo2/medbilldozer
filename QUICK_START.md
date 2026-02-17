# 🚀 MedBillDozer Quick Start Guide

Get MedBillDozer deployed to production in ~75 minutes.

---

## ⚡ Prerequisites (5 min)

Ensure you have accounts and tools ready:

```bash
# Check installations
gcloud --version    # Install: https://cloud.google.com/sdk/docs/install
node --version      # Should be v18+
python --version    # Should be 3.11+
```

**Create accounts (if needed):**
- [ ] Google Cloud: https://console.cloud.google.com
- [ ] Supabase: https://supabase.com
- [ ] Vercel: https://vercel.com

---

## 🔥 Phase 1: Firebase Setup (15 min)

### 1.1 Create Project & Enable Auth

```bash
# Go to: https://console.firebase.google.com
# 1. Click "Add project" → Name: medbilldozer
# 2. Navigate to Authentication → Get started
# 3. Enable Google provider (toggle on, add support email, save)
# 4. Enable GitHub provider (see guide for OAuth setup)
```

### 1.2 Get Credentials

**Backend credentials:**
```bash
# In Firebase Console:
# Settings (gear icon) → Service accounts → Generate new private key
# Save as: ~/Downloads/firebase-credentials.json
```

**Frontend credentials:**
```bash
# In Firebase Console:
# Project Settings → General → Your apps → Add web app
# Copy the firebaseConfig object
```

---

## 💾 Phase 2: Supabase Setup (10 min)

```bash
# Go to: https://supabase.com
# 1. New project → Name: medbilldozer
# 2. Generate strong database password (save it!)
# 3. Wait 2 minutes for project creation
# 4. Go to Project Settings → API
# 5. Copy: Project URL and service_role key
```

**Run database schema:**
```bash
# In Supabase dashboard:
# 1. Click SQL Editor
# 2. New query
# 3. Copy contents of sql/schema_production_api.sql
# 4. Paste and click "Run"
# 5. Verify tables created in Table Editor
```

---

## ☁️ Phase 3: Google Cloud Setup (10 min)

### 3.1 Set Project

```bash
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID
```

### 3.2 Run Infrastructure Setup Script

```bash
./scripts/setup_infrastructure.sh
```

This creates:
- GCS buckets for documents
- CORS configuration
- Required API enablements

---

## 🔧 Phase 4: Configure Backend (5 min)

### 4.1 Create Environment File

```bash
cd backend
cp .env.example .env
```

### 4.2 Fill in Credentials

Open `backend/.env` and fill in values from:
- Firebase (project_id, private_key, client_email)
- Supabase (url, service_role_key)
- GCP (project_id, bucket names)
- AI providers (openai_api_key, etc.)

```bash
# Generate JWT secret
JWT_SECRET_KEY=$(openssl rand -hex 32)
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY" >> .env
```

### 4.3 Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8080

# In another terminal, test:
curl http://localhost:8080/health
```

Expected output: `{"status":"healthy",...}`

---

## 🚀 Phase 5: Deploy Backend (15 min)

### 5.1 Deploy to Cloud Run

```bash
./scripts/deploy_backend.sh
```

This will:
1. Build Docker image
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Output your backend URL

### 5.2 Save Backend URL

```bash
# Copy the URL from output, looks like:
# https://medbilldozer-api-xxxxx-uc.a.run.app

export BACKEND_URL="https://medbilldozer-api-xxxxx-uc.a.run.app"
```

### 5.3 Test Deployed Backend

```bash
curl $BACKEND_URL/health
open $BACKEND_URL/docs  # Opens API documentation
```

---

## 🎨 Phase 6: Deploy Frontend (10 min)

### 6.1 Configure Frontend

```bash
cd frontend
cp .env.example .env.local
```

Edit `.env.local`:
```bash
VITE_API_BASE_URL=https://medbilldozer-api-xxxxx-uc.a.run.app

# Firebase config from Firebase Console
VITE_FIREBASE_API_KEY=AIza...
VITE_FIREBASE_AUTH_DOMAIN=medbilldozer.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=medbilldozer
# ... (rest of Firebase config)
```

### 6.2 Test Locally

```bash
npm install
npm run dev
```

Open http://localhost:5173 and test login.

### 6.3 Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

When prompted:
- Project name: `medbilldozer-frontend`
- Link to existing? No
- Override settings? No

### 6.4 Set Environment Variables in Vercel

```bash
# Go to: https://vercel.com/dashboard
# Select project → Settings → Environment Variables
# Add all VITE_* variables from .env.local
# Then redeploy: vercel --prod
```

---

## 🔄 Phase 7: Update CORS (5 min)

### 7.1 Update Backend CORS

```bash
# Get your Vercel URL
export FRONTEND_URL="https://medbilldozer-frontend.vercel.app"

# Redeploy backend with updated CORS
gcloud run deploy medbilldozer-api \
  --image gcr.io/$PROJECT_ID/medbilldozer-api \
  --region us-central1 \
  --update-env-vars "ALLOWED_ORIGINS=http://localhost:5173,$FRONTEND_URL"
```

### 7.2 Update Firebase Authorized Domains

```bash
# Go to: https://console.firebase.google.com
# Authentication → Settings → Authorized domains
# Click "Add domain" → Enter your Vercel URL
# Save
```

### 7.3 Update GCS CORS

```bash
cat > cors.json <<EOF
[
  {
    "origin": ["http://localhost:5173", "$FRONTEND_URL"],
    "method": ["GET", "PUT", "POST"],
    "responseHeader": ["Content-Type", "Authorization"],
    "maxAgeSeconds": 3600
  }
]
EOF

gsutil cors set cors.json gs://medbilldozer-documents
```

---

## ✅ Phase 8: Test End-to-End (10 min)

### 8.1 Open Your App

```bash
open $FRONTEND_URL
```

### 8.2 Complete Test Checklist

- [ ] **Login**: Click "Continue with Google" and authenticate
- [ ] **Upload**: Drag and drop a PDF file (or use sample from `benchmarks/inputs/`)
- [ ] **Select**: Click on uploaded document to select it
- [ ] **Analyze**: Click "Analyze" button
- [ ] **Wait**: Analysis takes 30-60 seconds
- [ ] **Results**: Verify issues and savings are displayed
- [ ] **Mobile**: Test on your phone
- [ ] **Logout**: Click user menu → Logout

---

## 🎉 Success!

Your MedBillDozer application is now live!

**URLs:**
- Frontend: https://medbilldozer-frontend.vercel.app
- Backend: https://medbilldozer-api-xxxxx-uc.a.run.app
- API Docs: https://medbilldozer-api-xxxxx-uc.a.run.app/docs

---

## 📊 Quick Commands Reference

### View Backend Logs
```bash
gcloud run services logs tail medbilldozer-api --region=us-central1
```

### Redeploy Backend
```bash
cd backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/medbilldozer-api
gcloud run deploy medbilldozer-api --image gcr.io/$PROJECT_ID/medbilldozer-api --region=us-central1
```

### Redeploy Frontend
```bash
cd frontend
vercel --prod
```

### Test API Health
```bash
curl $BACKEND_URL/health
```

---

## 🆘 Troubleshooting

### Backend not starting
```bash
# Check logs
gcloud run services logs read medbilldozer-api --region=us-central1 --limit=50

# Verify environment variables
gcloud run services describe medbilldozer-api --region=us-central1 --format=json | jq '.spec.template.spec.containers[0].env'
```

### CORS errors in browser
```bash
# Verify CORS configuration
gsutil cors get gs://medbilldozer-documents

# Update if needed
gsutil cors set cors.json gs://medbilldozer-documents
```

### Firebase auth not working
- Check Firebase authorized domains include your Vercel URL
- Verify frontend `.env.local` has correct Firebase config
- Clear browser cache and cookies

### Upload fails
- Check GCS CORS includes your frontend URL
- Verify buckets exist: `gsutil ls`
- Check browser console for detailed errors

---

## 📚 Full Documentation

For detailed guides, see:
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) - Complete step-by-step
- [Backend README](backend/README.md) - Backend API reference
- [Frontend README](frontend/README.md) - Frontend development guide
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Architecture overview

---

## 💰 Cost Estimate

**Free tier covers:**
- Firebase: 50K MAU
- Supabase: 500 MB database
- Cloud Run: 2M requests/month
- Vercel: Unlimited for personal

**After free tier:** ~$0.20/month for Cloud Storage

---

## 🔒 Security Checklist

- [ ] All secrets stored in Google Secret Manager
- [ ] `.env` files in `.gitignore`
- [ ] CORS configured with specific origins
- [ ] JWT secret is random (32+ bytes)
- [ ] Supabase RLS policies enabled
- [ ] Firebase service account JSON not in git

---

## 🎯 Next Steps

1. **Custom Domain** (optional)
   - Vercel: Project Settings → Domains
   - Add DNS records as instructed

2. **Monitoring**
   - Set up Google Cloud Monitoring alerts
   - Enable Supabase logging
   - Configure error tracking (Sentry)

3. **CI/CD**
   - Set up GitHub Actions
   - Automate deployments
   - Add tests

4. **Features**
   - Add more document types
   - Implement clinical image validation UI
   - Add email notifications
   - Build mobile app

---

**Need help?** Check [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed troubleshooting.

🚀 Happy analyzing medical bills!
