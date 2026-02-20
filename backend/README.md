# MedBillDozer FastAPI Backend

Production-ready FastAPI backend for MedBillDozer medical billing analysis.

## Architecture

```
FastAPI Backend (Cloud Run)
    ↓
Existing Core Modules (Reused)
    - orchestrator_agent.py
    - medgemma_ensemble_provider.py
    - clinical_validator.py
    - coverage_matrix.py
    ↓
Google Cloud Storage + Supabase
```

## Features

- **OAuth 2.0 Authentication**: Firebase Auth with Google/GitHub providers
- **Direct File Uploads**: GCS signed URLs for scalable uploads
- **MedGemma Analysis**: Reuses existing analysis engine (75% of codebase)
- **Cross-Document Analysis**: Coverage matrix for duplicate payment detection
- **Clinical Validation**: Vision API integration for medical imaging

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Set up Infrastructure

**Supabase:**
```bash
# Run schema migration
psql $SUPABASE_URL -f ../sql/schema_production_api.sql
```

**Google Cloud:**
```bash
# Create GCS buckets
gsutil mb gs://medbilldozer-documents
gsutil mb gs://medbilldozer-clinical

# Enable CORS for direct uploads (IMPORTANT!)
../scripts/setup_gcs_cors.sh
```

> **Note**: CORS configuration is critical for file uploads. Without it, uploads will fail with browser security errors. See [Troubleshooting Guide](../docs/TROUBLESHOOTING.md#-cors-errors-with-file-uploads) if you encounter CORS issues.

**Firebase:**
- Create Firebase project at https://console.firebase.google.com
- Enable Google Authentication
- Download service account key JSON
- Extract credentials to .env file

### 4. Run Locally

```bash
uvicorn app.main:app --reload --port 8080
```

API will be available at: http://localhost:8080
API docs: http://localhost:8080/docs

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login with Firebase ID token
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout

### Profile
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update profile

### Documents
- `POST /api/documents/upload-url` - Get signed upload URL
- `POST /api/documents/confirm` - Confirm upload
- `GET /api/documents` - List user documents
- `GET /api/documents/{id}` - Get document with download URL
- `DELETE /api/documents/{id}` - Delete document

### Analysis
- `POST /api/analyze` - Trigger analysis (background task)
- `GET /api/analyze/{id}` - Get analysis results (polling)
- `GET /api/analyze` - List user analyses

## Deployment to Cloud Run

### 1. Build Docker Image

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/medbilldozer-api
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy medbilldozer-api \
  --image gcr.io/PROJECT_ID/medbilldozer-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "SUPABASE_URL=$SUPABASE_URL,FIREBASE_PROJECT_ID=$FIREBASE_PROJECT_ID" \
  --set-secrets "OPENAI_API_KEY=openai-key:latest,SUPABASE_SERVICE_ROLE_KEY=supabase-key:latest" \
  --max-instances 10 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300
```

### 3. Set up Secrets (recommended)

```bash
# Store secrets in Google Secret Manager
echo -n "$OPENAI_API_KEY" | gcloud secrets create openai-key --data-file=-
echo -n "$SUPABASE_SERVICE_ROLE_KEY" | gcloud secrets create supabase-key --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding openai-key \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Architecture Details

### File Upload Flow

```
1. Client calls POST /api/documents/upload-url
2. Backend generates GCS signed URL (15min expiry)
3. Client uploads file directly to GCS using PUT
4. Client calls POST /api/documents/confirm
5. Backend saves metadata to Supabase
```

### Analysis Flow

```
1. Client calls POST /api/analyze
2. Backend queues background task
3. Background task:
   a. Downloads documents from GCS
   b. Runs OrchestratorAgent (reused code)
   c. Builds coverage matrix
   d. Saves results to Supabase
4. Client polls GET /api/analyze/{id} for completion
```

### Authentication Flow

```
1. User logs in with Google (Firebase Auth)
2. Client sends Firebase ID token to POST /api/auth/login
3. Backend verifies token with Firebase Admin SDK
4. Backend creates/updates user in Supabase
5. Backend returns JWT access token
6. Client includes token in Authorization header
```

## Reused Existing Modules

The following modules are reused **AS-IS** (no modifications needed):

- `src/medbilldozer/core/orchestrator_agent.py` - Analysis workflow
- `src/medbilldozer/providers/medgemma_ensemble_provider.py` - MedGemma
- `src/medbilldozer/core/clinical_validator.py` - Vision API
- `src/medbilldozer/core/coverage_matrix.py` - Cross-document analysis
- `src/medbilldozer/extractors/` - Fact extraction
- `src/medbilldozer/prompts/` - Domain prompts

**Total Reused LOC: ~15,000** (75% of existing codebase)

## Environment Variables

See `.env.example` for full list of required environment variables.

Critical variables:
- `FIREBASE_PROJECT_ID` - Firebase Auth
- `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` - Database
- `GCS_PROJECT_ID` + bucket names - File storage
- `OPENAI_API_KEY` - OpenAI provider
- `JWT_SECRET_KEY` - Token signing

## Testing

```bash
# Run tests
pytest tests/

# Test with curl
curl http://localhost:8080/health
```

## Monitoring

- **Logs**: Google Cloud Logging
- **Metrics**: Cloud Monitoring
- **Errors**: Sentry (TODO)
- **Performance**: Cloud Trace (TODO)

## CI/CD

GitHub Actions workflow in `.github/workflows/deploy-backend.yml` (TODO)

## License

Proprietary - MedBillDozer
