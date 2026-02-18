# MedBillDozer Architecture Documentation

**Version:** 0.3
**Last Updated:** February 17, 2026
**Status:** Production Prototype

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Security Model](#security-model)
6. [Database Schema](#database-schema)
7. [API Endpoints](#api-endpoints)
8. [Deployment Architecture](#deployment-architecture)
9. [Technology Stack](#technology-stack)

---

## 1. System Overview

MedBillDozer is a full-stack medical billing analysis platform that combines AI-powered document analysis with multimodal capabilities to detect billing errors, overcharges, and insurance coverage issues.

### Key Capabilities
- **Document Upload**: Direct-to-cloud upload with signed URLs
- **Multimodal Analysis**: Text (bills, EOBs) + Images (X-rays, prescriptions)
- **AI-Powered Detection**: MedGemma ensemble + OpenAI/Gemini fallback
- **Cross-Document Validation**: Coverage matrix for inconsistency detection
- **Real-time Results**: Async processing with polling-based updates

### Architecture Pattern
**Three-Tier Architecture:**
- **Presentation Tier**: React SPA with TypeScript
- **Application Tier**: FastAPI REST API with async processing
- **Data Tier**: Supabase (PostgreSQL) + Google Cloud Storage

---

## 2. Architecture Diagram

![Data Flow Diagram](./docs/data_flow_diagram.html)

```
┌──────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                              │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  React App (Vite + TypeScript)                                 │  │
│  │  - HomePage (Upload & Selection)                               │  │
│  │  - AnalysisDashboard (Results Polling)                         │  │
│  │  - Zustand Auth Store (JWT + Refresh Tokens)                   │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓ HTTP/HTTPS
                          Bearer Token (JWT)
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND (Python 3.11)                    │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Authentication Middleware                                     │  │
│  │  - JWT Verification (HS256)                                    │  │
│  │  - User Lookup from Supabase                                   │  │
│  └────────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  API Routes                                                    │  │
│  │  /api/auth      → AuthService (Firebase verification)         │  │
│  │  /api/documents → StorageService (GCS signed URLs)            │  │
│  │  /api/analyze   → AnalysisService (Async processing)          │  │
│  │  /api/profile   → DatabaseService (User CRUD)                 │  │
│  │  /api/issues    → DatabaseService (Issue tracking)            │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓                ↓
    ┌─────────┐     ┌──────────────────┐   ┌────────────┐   ┌────────────┐
    │ Firebase│     │   Google Cloud   │   │  Supabase  │   │   AI LLM   │
    │  Auth   │     │    Storage       │   │ PostgreSQL │   │  Providers │
    │ Admin   │     │  (GCS Buckets)   │   │  (PostREST)│   │ MedGemma/  │
    │  SDK    │     │                  │   │    RLS     │   │ GPT/Gemini │
    └─────────┘     └──────────────────┘   └────────────┘   └────────────┘
         ↓                    ↓                    ↓                ↓
    Verify ID          Sign Upload/         Store User/      Analyze
    Tokens             Download URLs        Documents/       Documents
    Return JWT                              Analyses/        Return
                                           Issues           Issues
```

---

## 3. Component Details

### 3.1 Frontend (React + TypeScript)

**Location:** `/frontend/`

**Framework Stack:**
- React 18.2 with TypeScript
- Vite (build tool)
- React Router DOM (routing)
- Zustand (state management)
- Axios (HTTP client)
- Tailwind CSS (styling)

**Key Components:**

| Component | Purpose | State Management |
|-----------|---------|------------------|
| `App.tsx` | Root component with router | Auth store via Zustand |
| `HomePage.tsx` | Document upload & selection | Local state + document service |
| `AnalysisDashboard.tsx` | Results display with polling | Local state + polling interval |
| `ProtectedRoute.tsx` | Auth guard for private routes | Auth store check |
| `DocumentUpload.tsx` | Drag-drop file upload | React Dropzone |

**Services:**

```typescript
// documents.service.ts
- getUploadUrl(filename, contentType, documentType?)
- uploadToGCS(uploadUrl, file)
- confirmUpload(documentId, filename, gcsPath, sizeBytes)
- getDocuments(userId)
- deleteDocument(documentId)

// analysis.service.ts
- triggerAnalysis(documentIds, provider?)
- getAnalysis(analysisId)
- pollAnalysis(analysisId, interval=2000)

// auth.service.ts
- login(firebaseIdToken)
- refreshAccessToken()
- logout()
```

**Authentication Flow:**
1. User signs in with Firebase (Google/GitHub OAuth)
2. Frontend receives Firebase ID token
3. POST `/api/auth/login` with ID token
4. Receive JWT access token (1hr) + refresh token (7d)
5. Store access token in memory, refresh token in httpOnly cookie
6. Axios interceptor adds `Authorization: Bearer {token}`
7. On 401, auto-refresh token and retry request

---

### 3.2 Backend (FastAPI)

**Location:** `/backend/app/`

**Framework:** FastAPI + Uvicorn + Pydantic

**Main Application** (`main.py`):
```python
app = FastAPI(title="MedBillDozer API", version="0.3.0")

# Middleware
app.add_middleware(CORSMiddleware,
                   allow_origins=config.allowed_origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(issues.router, prefix="/api/issues", tags=["issues"])

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.3.0"}
```

**Dependency Injection** (`dependencies.py`):

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    db_service: DatabaseService = Depends(get_db_service)
) -> dict:
    """
    1. Extract Bearer token from Authorization header
    2. Verify JWT signature
    3. Extract user_id from payload
    4. Lookup user in Supabase
    5. Return user dict
    """
    token = credentials.credentials
    payload = auth_service.verify_access_token(token)
    user_id = payload.get("user_id")
    user = await db_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user
```

---

### 3.3 Services Layer

#### 3.3.1 AuthService (`services/auth_service.py`)

**Responsibilities:**
- Verify Firebase ID tokens via Firebase Admin SDK
- Generate JWT access tokens (HS256, 1hr expiry)
- Generate JWT refresh tokens (HS256, 7d expiry)
- Validate JWT signatures

**Methods:**
```python
class AuthService:
    async def verify_firebase_token(self, id_token: str) -> dict
    def create_access_token(self, user_id: str, firebase_uid: str, email: str) -> str
    def create_refresh_token(self, user_id: str) -> str
    def verify_access_token(self, token: str) -> dict
    def verify_refresh_token(self, token: str) -> dict
```

**JWT Payload:**
```json
// Access Token
{
  "user_id": "uuid",
  "firebase_uid": "firebase_uid_string",
  "email": "user@example.com",
  "exp": 1234567890,
  "iat": 1234567890
}

// Refresh Token
{
  "sub": "user_id_uuid",
  "type": "refresh",
  "exp": 1234567890,
  "iat": 1234567890
}
```

---

#### 3.3.2 StorageService (`services/storage_service.py`)

**Responsibilities:**
- Generate signed upload URLs for client-side uploads
- Generate signed download URLs for client-side downloads
- Server-side file operations (download, delete, check existence)

**GCS Buckets:**
- `medbilldozer-documents`: Medical bills, EOBs, receipts
- `medbilldozer-clinical`: X-rays, clinical images

**Methods:**
```python
class StorageService:
    def generate_signed_upload_url(
        self,
        bucket_name: str,
        blob_path: str,
        content_type: str,
        expiration_minutes: int = 15
    ) -> str

    def generate_signed_download_url(
        self,
        bucket_name: str,
        blob_path: str,
        expiration_minutes: int = 10
    ) -> str

    async def download_text(self, bucket_name: str, blob_path: str) -> str
    async def file_exists(self, bucket_name: str, blob_path: str) -> bool
    async def delete_file(self, bucket_name: str, blob_path: str) -> bool
```

**Path Structure:** `{user_id}/{document_id}/{filename}`

---

#### 3.3.3 DatabaseService (`services/db_service.py`)

**Responsibilities:**
- User CRUD operations
- Document metadata management
- Analysis tracking
- Issue management

**Client:** Supabase Python client (PostgREST API)

**Methods:**
```python
class DatabaseService:
    # Users
    async def create_or_update_user(firebase_uid, email, display_name?, avatar_url?)
    async def get_user_by_id(user_id)
    async def get_user_by_firebase_uid(firebase_uid)
    async def update_last_login(user_id)

    # Documents
    async def create_document(user_id, filename, gcs_path, content_type, size_bytes, document_type?)
    async def get_documents(user_id, limit?, offset?)
    async def get_document_by_id(document_id)
    async def update_document_status(document_id, status, error_message?)
    async def delete_document(document_id)

    # Analyses
    async def create_analysis(user_id, document_ids, provider)
    async def get_analysis(analysis_id)
    async def update_analysis_status(analysis_id, status, started_at?, completed_at?, error_message?)
    async def update_analysis_results(analysis_id, results, coverage_matrix, total_savings, issues_count)

    # Issues
    async def create_issue(analysis_id, issue_data)
    async def get_issues_by_analysis(analysis_id)
    async def update_issue_status(issue_id, status, notes?)
```

---

#### 3.3.4 AnalysisService (`services/analysis_service.py`)

**Responsibilities:**
- Orchestrate document analysis workflow
- Detect document types (text vs image)
- Route to appropriate analysis service
- Calculate total savings and issue counts

**Workflow:**
```python
async def run_analysis(self, analysis_id, document_ids, user_id, provider="medgemma-ensemble"):
    # 1. Update status to "processing"
    await db_service.update_analysis_status(analysis_id, "processing", started_at=now())

    # 2. Fetch document metadata
    documents = await db_service.get_documents_by_ids(document_ids)

    # 3. Check for images
    has_images = any(doc.content_type.startswith("image/") for doc in documents)

    # 4. Route to appropriate service
    if has_images:
        results = await multimodal_service.run_multimodal_analysis(documents, provider)
    else:
        # Download text documents from GCS
        doc_contents = []
        for doc in documents:
            text = await storage_service.download_text(doc.gcs_path)
            doc_contents.append({"document_id": doc.id, "text": text})

        # Run OrchestratorAgent on each
        from medbilldozer.providers import get_provider
        provider_instance = get_provider(provider)

        all_issues = []
        for doc_content in doc_contents:
            issues = await provider_instance.analyze(doc_content["text"])
            all_issues.extend(issues)

        # Build coverage matrix (cross-document validation)
        coverage_matrix = self._build_coverage_matrix(all_issues, documents)

        results = {
            "issues": all_issues,
            "coverage_matrix": coverage_matrix
        }

    # 5. Calculate metrics
    total_savings = sum(issue.get("max_savings", 0) for issue in results["issues"])
    issues_count = len(results["issues"])

    # 6. Save results
    await db_service.update_analysis_results(
        analysis_id,
        results,
        results.get("coverage_matrix"),
        total_savings,
        issues_count
    )

    # 7. Insert individual issues
    for issue_data in results["issues"]:
        await db_service.create_issue(analysis_id, issue_data)

    # 8. Mark complete
    await db_service.update_analysis_status(analysis_id, "completed", completed_at=now())
```

---

#### 3.3.5 MultimodalAnalysisService (`services/multimodal_analysis_service.py`)

**Responsibilities:**
- Handle mixed text + image document sets
- Perform clinical image validation
- Cross-reference text and image findings

**Workflow:**
```python
async def run_multimodal_analysis(self, documents, provider):
    # Step 1: Categorize documents
    text_docs = [d for d in documents if d.content_type.startswith("text/") or d.content_type == "application/pdf"]
    image_docs = [d for d in documents if d.content_type.startswith("image/")]

    # Step 2: Analyze text documents (bills, EOBs)
    text_issues = []
    for doc in text_docs:
        text = await storage_service.download_text(doc.gcs_path)
        issues = await provider_instance.analyze(text)
        text_issues.extend(issues)

    # Step 3: Analyze images (X-rays, prescriptions)
    from medbilldozer.validators import ClinicalValidator
    clinical_validator = ClinicalValidator()

    image_issues = []
    for doc in image_docs:
        # Download image
        image_bytes = await storage_service.download_file(doc.gcs_path)

        # Run clinical validation
        findings = await clinical_validator.validate_image(image_bytes, doc.content_type)
        image_issues.extend(findings)

    # Step 4: Cross-reference findings
    cross_ref_issues = self._cross_reference_findings(text_issues, image_issues)

    # Step 5: Compile results
    all_issues = text_issues + image_issues + cross_ref_issues
    coverage_matrix = self._build_multimodal_coverage_matrix(all_issues, documents)

    return {
        "issues": all_issues,
        "coverage_matrix": coverage_matrix,
        "text_document_count": len(text_docs),
        "image_document_count": len(image_docs),
        "cross_reference_findings": len(cross_ref_issues)
    }
```

---

## 4. Data Flow

### 4.1 Document Upload Flow

```
User selects file → Frontend
  ↓
  POST /api/documents/upload-url
  Body: {filename, content_type, document_type?}
  ↓
  Backend generates signed URL (15min expiry)
  - Creates document_id (UUID)
  - Generates GCS path: {user_id}/{document_id}/{filename}
  - Calls storage_service.generate_signed_upload_url()
  ↓
  Response: {document_id, upload_url, gcs_path, expires_at}
  ↓
  Frontend uploads file directly to GCS
  - PUT {upload_url}
  - Body: file bytes
  - Headers: {Content-Type}
  ↓
  GCS stores file
  ↓
  Frontend confirms upload
  - POST /api/documents/confirm
  - Body: {document_id, filename, gcs_path, size_bytes}
  ↓
  Backend saves metadata to Supabase
  - INSERT INTO documents (document_id, user_id, filename, gcs_path, ...)
  ↓
  Response: DocumentResponse
  ↓
  Frontend displays uploaded document in list
```

**Why Signed URLs?**
- **Performance**: Direct upload to GCS bypasses backend
- **Security**: Time-limited, method-scoped (PUT only)
- **Scalability**: No backend bottleneck for large files

---

### 4.2 Analysis Flow

```
User selects documents + clicks "Analyze" → Frontend
  ↓
  POST /api/analyze/
  Body: {document_ids: [uuid, uuid, ...], provider?: "medgemma-ensemble"}
  ↓
  Backend creates analysis record
  - INSERT INTO analyses (user_id, document_ids, provider, status="queued")
  - Returns analysis_id immediately
  ↓
  Backend spawns background task
  - asyncio.create_task(analysis_service.run_analysis(...))
  ↓
  Response: {analysis_id, status: "queued", estimated_completion: "2-5 minutes"}
  ↓
  Frontend navigates to AnalysisDashboard
  - Starts polling: GET /api/analyze/{analysis_id} every 2 seconds
  ↓
  Backend processes in background:
    1. Update status to "processing"
    2. Download documents from GCS
    3. Run LLM analysis (MedGemma/GPT/Gemini)
    4. Extract issues
    5. Build coverage matrix
    6. Calculate total savings
    7. Save results to database
    8. Insert issues
    9. Update status to "completed"
  ↓
  Frontend polls and detects status change
  - GET /api/analyze/{analysis_id}
  - Response: {status: "completed", results, coverage_matrix, total_savings, issues_count}
  ↓
  Frontend stops polling
  - Displays results
  - Fetches detailed issues: GET /api/issues?analysis_id={id}
  ↓
  User views issues with evidence, recommended actions, savings
```

**Why Async + Polling?**
- **Long-running tasks**: Analysis can take 30s - 5min
- **Non-blocking**: User can navigate away and return
- **Scalability**: Backend can queue/throttle analysis jobs
- **Simple implementation**: No WebSocket infrastructure needed

---

### 4.3 Authentication Flow

```
User clicks "Sign in with Google" → Frontend
  ↓
  Firebase Auth SDK initiates OAuth flow
  ↓
  User approves in Google popup
  ↓
  Firebase returns ID token (JWT signed by Google)
  ↓
  Frontend sends ID token to backend
  - POST /api/auth/login
  - Body: {firebase_id_token}
  ↓
  Backend verifies with Firebase Admin SDK
  - firebase_admin.auth.verify_id_token(id_token)
  - Extracts: uid, email, name
  ↓
  Backend creates/updates user in Supabase
  - INSERT INTO user_profiles (...) ON CONFLICT (firebase_uid) DO UPDATE
  - Updates last_login_at
  ↓
  Backend generates JWT tokens
  - access_token (1hr expiry): {user_id, firebase_uid, email}
  - refresh_token (7d expiry): {sub: user_id, type: "refresh"}
  ↓
  Response: {access_token, refresh_token, user: {...}}
  Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=Strict
  ↓
  Frontend stores access_token in Zustand store (memory)
  Frontend stores refresh_token in httpOnly cookie (automatic)
  ↓
  All subsequent requests include:
  - Header: Authorization: Bearer {access_token}
  ↓
  Backend verifies JWT on every request
  - Extract token from header
  - Verify signature with JWT_SECRET_KEY
  - Extract user_id from payload
  - Lookup user in Supabase
  - Inject user into request context
  ↓
  On 401 (token expired):
    Frontend detects 401 response
    ↓
    POST /api/auth/refresh (cookie sent automatically)
    ↓
    Backend verifies refresh_token from cookie
    ↓
    Backend generates new access_token
    ↓
    Frontend updates Zustand store
    ↓
    Frontend retries original request with new token
```

---

## 5. Security Model

### 5.1 Authentication & Authorization

**Multi-Layer Security:**

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| **Frontend Auth** | Firebase OAuth | User identity via Google/GitHub |
| **API Auth** | JWT Bearer Tokens | Stateless request verification |
| **Session Refresh** | HTTP-only Cookies | Long-lived session without XSS risk |
| **Database Auth** | Row Level Security (RLS) | User data isolation |
| **Storage Auth** | Signed URLs | Time-limited file access |

**Token Security:**
- Access tokens: Short-lived (1hr), stored in memory
- Refresh tokens: Long-lived (7d), httpOnly cookie
- Signature: HS256 with secret key
- No sensitive data in JWT payload

**Row Level Security (RLS):**
```sql
-- Users can only see their own data
CREATE POLICY "Users can view their own documents"
    ON documents FOR SELECT
    USING (user_id IN (
        SELECT user_id FROM user_profiles
        WHERE firebase_uid = auth.uid()::text
    ));

CREATE POLICY "Users can view their own analyses"
    ON analyses FOR SELECT
    USING (user_id IN (
        SELECT user_id FROM user_profiles
        WHERE firebase_uid = auth.uid()::text
    ));
```

---

### 5.2 CORS Configuration

**Allowed Origins:**
- `http://localhost:5173` (dev frontend)
- `http://localhost:3000` (alternative dev port)
- Production domain (when deployed)

**Settings:**
- `allow_credentials: true` (for cookies)
- `allow_methods: ["*"]` (all HTTP methods)
- `allow_headers: ["*"]` (including Authorization)

---

### 5.3 Secrets Management

**Environment Variables:**
```bash
# Firebase (service account)
FIREBASE_PROJECT_ID
FIREBASE_PRIVATE_KEY
FIREBASE_CLIENT_EMAIL

# Google Cloud Storage (service account)
GCS_PROJECT_ID
GCS_SERVICE_ACCOUNT_KEY

# Supabase
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY

# JWT
JWT_SECRET_KEY  # Used for signing tokens

# AI Providers
OPENAI_API_KEY
GEMINI_API_KEY
HF_API_TOKEN
```

**Best Practices:**
- Never commit secrets to git
- Use `.env` files locally (gitignored)
- Use Google Cloud Secret Manager in production
- Rotate keys regularly

---

## 6. Database Schema

### 6.1 Entity Relationship Diagram

```
user_profiles (1) ──────────< (N) documents
     │                            │
     │                            │
     │                            │
     └──────────< (N) analyses <──┘
                       │
                       │
                       └──────────< (N) issues
```

---

### 6.2 Table Definitions

#### user_profiles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | UUID | PK, DEFAULT gen_random_uuid() | Internal user ID |
| firebase_uid | TEXT | UNIQUE, NOT NULL | Firebase UID from auth |
| email | TEXT | NOT NULL | User email |
| display_name | TEXT | NULL | User's display name |
| avatar_url | TEXT | NULL | Profile picture URL |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Account creation |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last profile update |
| last_login_at | TIMESTAMPTZ | NULL | Last login timestamp |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| metadata | JSONB | DEFAULT '{}' | Custom user data |

**Indexes:**
- `idx_user_profiles_firebase_uid` on `firebase_uid`
- `idx_user_profiles_email` on `email`
- `idx_user_profiles_created_at` on `created_at DESC`

---

#### documents

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| document_id | UUID | PK, DEFAULT gen_random_uuid() | Document ID |
| user_id | UUID | FK → user_profiles, NOT NULL | Owner |
| filename | TEXT | NOT NULL | Display filename |
| original_filename | TEXT | NOT NULL | Original upload name |
| gcs_path | TEXT | NOT NULL | GCS blob path |
| content_type | TEXT | NOT NULL | MIME type |
| size_bytes | BIGINT | NOT NULL | File size |
| uploaded_at | TIMESTAMPTZ | DEFAULT NOW() | Upload timestamp |
| status | TEXT | CHECK (uploaded, processing, analyzing, completed, failed) | Processing status |
| document_type | TEXT | CHECK (medical_bill, dental_bill, insurance_eob, pharmacy_receipt, fsa_claim, clinical_image, other) | Document category |
| extracted_text | TEXT | NULL | OCR/extracted content |
| metadata | JSONB | DEFAULT '{}' | Custom metadata |
| error_message | TEXT | NULL | Error details if failed |

**Indexes:**
- `idx_documents_user_id` on `user_id`
- `idx_documents_uploaded_at` on `uploaded_at DESC`
- `idx_documents_status` on `status`
- `idx_documents_document_type` on `document_type`

**Constraints:**
- `unique_user_gcs_path` on `(user_id, gcs_path)`

---

#### analyses

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| analysis_id | UUID | PK, DEFAULT gen_random_uuid() | Analysis job ID |
| user_id | UUID | FK → user_profiles, NOT NULL | Owner |
| document_ids | UUID[] | NOT NULL | Array of document IDs |
| provider | TEXT | DEFAULT 'medgemma-ensemble' | LLM provider used |
| status | TEXT | CHECK (queued, processing, completed, failed) | Job status |
| results | JSONB | NULL | Full analysis results |
| coverage_matrix | JSONB | NULL | Cross-document validation |
| total_savings_detected | NUMERIC(10,2) | NULL | Sum of max_savings |
| issues_count | INTEGER | DEFAULT 0 | Number of issues found |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Job creation |
| started_at | TIMESTAMPTZ | NULL | Processing start |
| completed_at | TIMESTAMPTZ | NULL | Processing end |
| error_message | TEXT | NULL | Error details if failed |
| processing_time_seconds | INTEGER | NULL | Duration (auto-calculated) |
| metadata | JSONB | DEFAULT '{}' | Custom metadata |

**Indexes:**
- `idx_analyses_user_id` on `user_id`
- `idx_analyses_status` on `status`
- `idx_analyses_created_at` on `created_at DESC`
- `idx_analyses_completed_at` on `completed_at DESC`

**Triggers:**
- `update_analyses_processing_time`: Auto-calculates `processing_time_seconds` on completion

---

#### issues

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| issue_id | UUID | PK, DEFAULT gen_random_uuid() | Issue ID |
| analysis_id | UUID | FK → analyses, NOT NULL | Parent analysis |
| document_id | UUID | FK → documents, NULL | Source document |
| issue_type | TEXT | NOT NULL | Category (e.g., "overcharge", "duplicate") |
| summary | TEXT | NOT NULL | Brief description |
| evidence | TEXT | NULL | Supporting details |
| code | TEXT | NULL | Medical/billing code |
| recommended_action | TEXT | NULL | What user should do |
| max_savings | NUMERIC(10,2) | DEFAULT 0 | Potential savings |
| confidence | TEXT | CHECK (high, medium, low) | Confidence level |
| source | TEXT | CHECK (llm, deterministic, clinical) | Detection method |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Detection timestamp |
| metadata | JSONB | DEFAULT '{}' | Custom metadata |

**Indexes:**
- `idx_issues_analysis_id` on `analysis_id`
- `idx_issues_document_id` on `document_id`
- `idx_issues_issue_type` on `issue_type`
- `idx_issues_max_savings` on `max_savings DESC`

**Triggers:**
- `increment_issues_count_trigger`: Auto-increments `analyses.issues_count` on insert

---

### 6.3 Views

#### user_analytics

```sql
CREATE VIEW user_analytics AS
SELECT
    up.user_id,
    up.email,
    up.display_name,
    up.created_at,
    COUNT(DISTINCT d.document_id) as total_documents,
    COUNT(DISTINCT a.analysis_id) as total_analyses,
    COALESCE(SUM(a.total_savings_detected), 0) as total_savings_detected,
    COALESCE(SUM(a.issues_count), 0) as total_issues_found,
    MAX(up.last_login_at) as last_active
FROM user_profiles up
LEFT JOIN documents d ON up.user_id = d.user_id
LEFT JOIN analyses a ON up.user_id = a.user_id AND a.status = 'completed'
GROUP BY up.user_id, up.email, up.display_name, up.created_at;
```

---

## 7. API Endpoints

### 7.1 Authentication

#### POST /api/auth/login
**Description:** Exchange Firebase ID token for JWT tokens
**Request:**
```json
{
  "firebase_id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
}
```
**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "display_name": "John Doe",
    "avatar_url": "https://...",
    "created_at": "2026-01-15T10:30:00Z",
    "last_login_at": "2026-02-17T08:00:00Z"
  }
}
```
**Set-Cookie:** `refresh_token=...; HttpOnly; Secure; SameSite=Strict; Max-Age=604800`

---

#### POST /api/auth/refresh
**Description:** Refresh access token using refresh token from cookie
**Request:** (No body, refresh_token sent via cookie)
**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

#### POST /api/auth/logout
**Description:** Invalidate refresh token
**Response:**
```json
{
  "message": "Logged out successfully"
}
```
**Set-Cookie:** `refresh_token=; Max-Age=0` (clears cookie)

---

### 7.2 Documents

#### POST /api/documents/upload-url
**Description:** Get signed URL for direct GCS upload
**Auth:** Required
**Request:**
```json
{
  "filename": "medical_bill_2026-02.pdf",
  "content_type": "application/pdf",
  "document_type": "medical_bill"
}
```
**Response:**
```json
{
  "document_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "upload_url": "https://storage.googleapis.com/medbilldozer-documents/user123/doc456/medical_bill.pdf?X-Goog-Algorithm=...",
  "gcs_path": "user123/doc456/medical_bill.pdf",
  "expires_at": "2026-02-17T10:45:00Z"
}
```

---

#### POST /api/documents/confirm
**Description:** Confirm upload and save metadata
**Auth:** Required
**Request:**
```json
{
  "document_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "filename": "medical_bill_2026-02.pdf",
  "gcs_path": "user123/doc456/medical_bill.pdf",
  "size_bytes": 245678
}
```
**Response:**
```json
{
  "document_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "filename": "medical_bill_2026-02.pdf",
  "content_type": "application/pdf",
  "size_bytes": 245678,
  "uploaded_at": "2026-02-17T10:32:00Z",
  "status": "uploaded",
  "document_type": "medical_bill"
}
```

---

#### GET /api/documents/
**Description:** List user's documents
**Auth:** Required
**Query Params:** `limit` (default: 50), `offset` (default: 0)
**Response:**
```json
{
  "documents": [
    {
      "document_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "filename": "medical_bill_2026-02.pdf",
      "content_type": "application/pdf",
      "size_bytes": 245678,
      "uploaded_at": "2026-02-17T10:32:00Z",
      "status": "completed",
      "document_type": "medical_bill",
      "download_url": "https://storage.googleapis.com/..."
    }
  ],
  "total": 15
}
```

---

#### DELETE /api/documents/{document_id}
**Description:** Delete document and GCS file
**Auth:** Required
**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

---

### 7.3 Analysis

#### POST /api/analyze/
**Description:** Trigger analysis on selected documents
**Auth:** Required
**Request:**
```json
{
  "document_ids": [
    "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "9f3b2d81-5c4a-49ab-bd2f-8e1d3c7a9b4e"
  ],
  "provider": "medgemma-ensemble"
}
```
**Response:**
```json
{
  "analysis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "queued",
  "estimated_completion": "2-5 minutes"
}
```

---

#### GET /api/analyze/{analysis_id}
**Description:** Get analysis status and results
**Auth:** Required
**Response (queued/processing):**
```json
{
  "analysis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "created_at": "2026-02-17T10:35:00Z",
  "started_at": "2026-02-17T10:35:03Z"
}
```
**Response (completed):**
```json
{
  "analysis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "provider": "medgemma-ensemble",
  "results": {
    "issues": [...],
    "coverage_matrix": {...}
  },
  "coverage_matrix": {...},
  "total_savings_detected": 342.50,
  "issues_count": 5,
  "created_at": "2026-02-17T10:35:00Z",
  "started_at": "2026-02-17T10:35:03Z",
  "completed_at": "2026-02-17T10:37:15Z",
  "processing_time_seconds": 132
}
```

---

### 7.4 Issues

#### GET /api/issues/?analysis_id={id}
**Description:** Get issues for an analysis
**Auth:** Required
**Response:**
```json
{
  "issues": [
    {
      "issue_id": "i1i2i3i4-i5i6-i7i8-i9i0-iabcdefghij",
      "analysis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "document_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "issue_type": "overcharge",
      "summary": "Lab test charged at $450 when average cost is $120",
      "evidence": "CPT code 80053 (Comprehensive Metabolic Panel) typically costs $80-$150",
      "code": "80053",
      "recommended_action": "Contact billing department to request repricing based on fair market value",
      "max_savings": 330.00,
      "confidence": "high",
      "source": "llm",
      "created_at": "2026-02-17T10:37:10Z"
    }
  ],
  "total": 5
}
```

---

## 8. Deployment Architecture

### 8.1 Production Stack

```
┌────────────────────────────────────────────────────────────┐
│                    USERS (Browser)                         │
└────────────────────────────────────────────────────────────┘
                            ↓ HTTPS
┌────────────────────────────────────────────────────────────┐
│                  FRONTEND (Vercel/Netlify)                 │
│  - React SPA (static build from Vite)                      │
│  - CDN edge caching                                        │
│  - Custom domain with SSL                                  │
└────────────────────────────────────────────────────────────┘
                            ↓ HTTPS
┌────────────────────────────────────────────────────────────┐
│               BACKEND (Google Cloud Run)                   │
│  - Docker container (Python 3.11)                          │
│  - Auto-scaling (0-100 instances)                          │
│  - Health checks on /health                                │
│  - Environment variables from Secret Manager               │
└────────────────────────────────────────────────────────────┘
         ↓              ↓               ↓              ↓
    ┌────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
    │Firebase│   │   GCS    │   │Supabase  │   │ AI APIs  │
    │  Auth  │   │ Buckets  │   │PostgreSQL│   │MedGemma/ │
    │        │   │          │   │   RLS    │   │GPT/Gemini│
    └────────┘   └──────────┘   └──────────┘   └──────────┘
```

---

### 8.2 Docker Configuration

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Set Python path
ENV PYTHONPATH=/app

# Cloud Run sets PORT env var
ENV PORT=8080

# Run with 2 workers
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 2
```

**Build & Deploy:**
```bash
# Build image
docker build -t medbilldozer-api .

# Test locally
docker run -p 8080:8080 --env-file .env medbilldozer-api

# Push to Google Container Registry
docker tag medbilldozer-api gcr.io/PROJECT_ID/medbilldozer-api
docker push gcr.io/PROJECT_ID/medbilldozer-api

# Deploy to Cloud Run
gcloud run deploy medbilldozer-api \
  --image gcr.io/PROJECT_ID/medbilldozer-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "SUPABASE_URL=..." \
  --set-secrets "JWT_SECRET_KEY=jwt-secret:latest"
```

---

### 8.3 Environment Configuration

**Development (.env):**
```bash
# API
APP_NAME=MedBillDozer API
SERVER_HOST=127.0.0.1
SERVER_PORT=8080
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Firebase
FIREBASE_PROJECT_ID=medbilldozer-dev
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@medbilldozer-dev.iam.gserviceaccount.com

# GCS
GCS_PROJECT_ID=medbilldozer-dev
GCS_BUCKET_DOCUMENTS=medbilldozer-documents-dev
GCS_BUCKET_CLINICAL_IMAGES=medbilldozer-clinical-dev

# Supabase (beta)
SUPABASE_BETA_URL=https://xyz.supabase.co
SUPABASE_BETA_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# JWT
JWT_SECRET_KEY=your-256-bit-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# AI
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
HF_API_TOKEN=hf_...
```

**Production (Google Secret Manager):**
- Store sensitive values as secrets
- Reference in Cloud Run deployment
- Auto-injected as environment variables

---

## 9. Technology Stack

### 9.1 Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2 | UI framework |
| TypeScript | 5.x | Type safety |
| Vite | 5.x | Build tool & dev server |
| React Router DOM | 6.x | Client-side routing |
| Zustand | 4.x | State management |
| Axios | 1.x | HTTP client |
| Tailwind CSS | 3.x | Utility-first CSS |
| React Dropzone | 14.x | File upload UI |
| Lucide React | Latest | Icon library |

---

### 9.2 Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11 | Runtime |
| FastAPI | 0.x | Web framework |
| Uvicorn | 0.x | ASGI server |
| Pydantic | 2.x | Data validation |
| Firebase Admin SDK | 6.x | Auth verification |
| Google Cloud Storage | 2.x | File storage |
| Supabase Python | 2.x | Database client |
| PyJWT | 2.x | JWT encoding/decoding |
| Python-Jose | 3.x | JWT utilities |

---

### 9.3 Infrastructure

| Service | Provider | Purpose |
|---------|----------|---------|
| Authentication | Firebase Auth | OAuth 2.0 (Google, GitHub) |
| Database | Supabase (PostgreSQL) | Relational data with RLS |
| File Storage | Google Cloud Storage | Document persistence |
| Hosting (Frontend) | Vercel/Netlify | Static site hosting |
| Hosting (Backend) | Google Cloud Run | Containerized API |
| Secrets | Google Secret Manager | Credential management |
| AI/LLM | MedGemma/OpenAI/Gemini | Document analysis |

---

### 9.4 Development Tools

| Tool | Purpose |
|------|---------|
| Git | Version control |
| Docker | Containerization |
| ESLint | Frontend linting |
| Prettier | Code formatting |
| Black | Python formatting |
| pytest | Backend testing |
| Vitest | Frontend testing |

---

## 10. Performance Considerations

### 10.1 Optimizations

**Frontend:**
- Code splitting with React.lazy()
- Memoization with React.memo()
- Debounced polling (2-3 second interval)
- CDN caching for static assets

**Backend:**
- Async/await for I/O operations
- Connection pooling for Supabase
- Signed URLs for direct GCS access (bypasses backend)
- Background tasks for long-running analysis

**Database:**
- Indexes on frequently queried columns
- JSONB for flexible metadata storage
- Views for aggregated analytics

---

### 10.2 Scalability

**Horizontal Scaling:**
- Cloud Run auto-scales from 0 to 100 instances
- Stateless design (JWT-based auth)
- No server-side sessions

**Vertical Scaling:**
- Adjustable CPU/memory limits in Cloud Run
- Supabase scales with plan tier

**Rate Limiting:**
- Implement rate limiting middleware (future)
- Throttle analysis jobs per user

---

## 11. Monitoring & Observability

### 11.1 Logging

**Backend:**
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- Error stack traces

**Frontend:**
- Console logging in development
- Error boundary for crash reporting
- Analytics events (future)

---

### 11.2 Health Checks

**API Health Endpoint:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.3.0",
        "timestamp": datetime.utcnow().isoformat()
    }
```

**Docker Health Check:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

---

## 12. Future Enhancements

### 12.1 Planned Features

- **Real-time Updates**: WebSocket for live analysis progress
- **Batch Processing**: Queue system for multiple analyses
- **Email Notifications**: Alert when analysis completes
- **Export Reports**: PDF generation of analysis results
- **Mobile App**: React Native client
- **Admin Dashboard**: User analytics and system metrics

---

### 12.2 Technical Debt

- Add comprehensive unit tests (backend & frontend)
- Implement rate limiting
- Add request caching (Redis)
- Optimize LLM prompts for cost reduction
- Implement circuit breakers for external APIs

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **EOB** | Explanation of Benefits (insurance document) |
| **GCS** | Google Cloud Storage |
| **JWT** | JSON Web Token (authentication) |
| **RLS** | Row Level Security (database access control) |
| **SPA** | Single Page Application |
| **CPT Code** | Current Procedural Terminology (medical billing code) |
| **MedGemma** | Google's medical domain LLM |
| **Signed URL** | Time-limited, pre-authenticated URL for cloud storage |

---

## Appendix B: References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Google Cloud Storage](https://cloud.google.com/storage/docs)
- [React Documentation](https://react.dev/)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)

---

**Document Version:** 1.0
**Last Updated:** February 17, 2026
**Author:** MedBillDozer Team
