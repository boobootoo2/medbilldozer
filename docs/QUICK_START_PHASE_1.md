# Quick Start Guide: Phase 1 Implementation

**Start Date:** February 19, 2026
**Duration:** 3 months (Weeks 1-12)
**Goal:** MVP insurance integration with UnitedHealthcare
**Budget:** $75,000

---

## Week 1: Infrastructure Setup (Feb 19-26)

### Day 1-2: Database Migration

```bash
# 1. Create migration file
cd /Users/jgs/Documents/GitHub/medbilldozer
mkdir -p sql/migrations
touch sql/migrations/001_add_insurance_tables.sql
```

Copy the SQL from [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md#11-database-migration) into this file.

```bash
# 2. Test on staging
psql $STAGING_DATABASE_URL -f sql/migrations/001_add_insurance_tables.sql

# 3. Apply to production (after testing)
psql $PRODUCTION_DATABASE_URL -f sql/migrations/001_add_insurance_tables.sql
```

**Verification:**
```sql
-- Check tables exist
\dt insurance_*
\dt claims
\dt sync_jobs

-- Check RLS policies
SELECT * FROM pg_policies WHERE tablename LIKE 'insurance%';
```

### Day 3-5: Task Queue Setup

```bash
# 1. Install dependencies
cd backend
pip install google-cloud-tasks protobuf

# Update requirements.txt
echo "google-cloud-tasks>=2.0.0" >> requirements.txt
echo "protobuf>=4.0.0" >> requirements.txt
```

```bash
# 2. Create Cloud Tasks queue
gcloud tasks queues create insurance-sync-queue \
    --location=us-central1 \
    --max-concurrent-dispatches=10 \
    --max-dispatches-per-second=5
```

```bash
# 3. Create task service
touch backend/app/services/task_service.py
```

Copy the `TaskService` class from the roadmap.

**Verification:**
```bash
# Test queue exists
gcloud tasks queues describe insurance-sync-queue --location=us-central1
```

---

## Week 2: UHC Registration & Setup (Feb 26 - Mar 5)

### Step 1: Register with UnitedHealthcare

1. **Visit:** https://developer.uhc.com/
2. **Create Account:**
   - Use company email: dev@medbilldozer.com
   - Company: MedBillDozer
   - Purpose: FHIR integration for medical billing analysis

3. **Register Application:**
   - App Name: MedBillDozer
   - Description: Medical billing analysis platform
   - Redirect URI: `https://medbilldozer.com/insurance/callback`
   - Scopes: Patient.read, Coverage.read, ExplanationOfBenefit.read

4. **Save Credentials:**
```bash
# Add to Google Secret Manager
gcloud secrets create UHC_CLIENT_ID --data-file=- <<< "your_client_id"
gcloud secrets create UHC_CLIENT_SECRET --data-file=- <<< "your_client_secret"
```

5. **Test in Sandbox:**
   - Use UHC test credentials
   - Test OAuth flow
   - Verify FHIR API access

### Step 2: Review FHIR Documentation

- [ ] Read UHC FHIR R4 Implementation Guide
- [ ] Understand Patient resource structure
- [ ] Understand Coverage resource structure
- [ ] Understand ExplanationOfBenefit structure
- [ ] Note any UHC-specific quirks

**Estimated Time:** 3-5 business days for approval

---

## Week 3-4: Backend Implementation (Mar 5-19)

### Step 1: FHIR Client

```bash
# 1. Install dependencies
pip install httpx fuzzywuzzy python-Levenshtein cryptography

# Update requirements.txt
echo "httpx>=0.25.0" >> requirements.txt
echo "fuzzywuzzy>=0.18.0" >> requirements.txt
echo "python-Levenshtein>=0.21.0" >> requirements.txt
echo "cryptography>=41.0.0" >> requirements.txt
```

```bash
# 2. Create FHIR service
touch backend/app/services/fhir_service.py
```

Copy the `FHIRClient` class from roadmap.

### Step 2: Insurance API Endpoints

```bash
# 1. Create insurance API
touch backend/app/api/insurance.py
```

Copy the insurance router from roadmap.

```bash
# 2. Register router in main.py
```

Add to `backend/app/main.py`:
```python
from app.api import insurance

app.include_router(insurance.router)
```

### Step 3: Database Service Updates

```bash
# Edit backend/app/services/db_service.py
```

Add methods:
- `create_insurance_connection()`
- `get_insurance_connection()`
- `update_insurance_connection()`
- `create_insurance_benefits()`
- `create_claim()`

### Step 4: Generate Encryption Key

```python
# Generate key for token encryption
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

```bash
# Store in Secret Manager
gcloud secrets create INSURANCE_TOKEN_ENCRYPTION_KEY --data-file=- <<< "your_key"
```

**Testing:**
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/api/insurance/connect/fhir \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"payer_id": "uhc", "authorization_code": "test_code"}'
```

---

## Week 4: Frontend Implementation (Mar 19-26)

### Step 1: Update Insurance Modal

```bash
# Edit frontend/src/components/insurance/InsuranceConnectionModal.tsx
```

Replace mock implementation with real OAuth flow from roadmap.

### Step 2: Create OAuth Callback Page

```bash
# Create callback page
touch frontend/src/pages/InsuranceCallbackPage.tsx
```

Copy implementation from roadmap.

```bash
# Add route to router
```

In `frontend/src/App.tsx`:
```typescript
import { InsuranceCallbackPage } from './pages/InsuranceCallbackPage';

// Add route
<Route path="/insurance/callback" element={<InsuranceCallbackPage />} />
```

### Step 3: Add OAuth Initiate Endpoint

In `backend/app/api/insurance.py`:
```python
@router.post("/oauth/initiate")
async def initiate_oauth(
    payer_id: str,
    current_user = Depends(get_current_user)
):
    """Generate OAuth authorization URL."""
    config = get_payer_config(payer_id)

    state = secrets.token_urlsafe(32)

    auth_url = (
        f"{config['authorize_url']}?"
        f"client_id={config['client_id']}&"
        f"redirect_uri={config['redirect_uri']}&"
        f"response_type=code&"
        f"scope=patient/*.read&"
        f"state={state}"
    )

    return {
        "authorization_url": auth_url,
        "state": state
    }
```

**Testing:**
```bash
# Start frontend
cd frontend
npm run dev

# Test OAuth flow
# 1. Click "Connect Insurance"
# 2. Select UnitedHealthcare
# 3. Should redirect to UHC login
# 4. After login, should redirect back with code
# 5. Should see success message
```

---

## Week 5-8: Email Forwarding & Beta Testing (Mar 26 - Apr 23)

### Step 1: Mailgun Setup

1. **Sign up:** https://www.mailgun.com/
2. **Add domain:** medbilldozer.com
3. **Verify DNS records**
4. **Get API key**

```bash
# Store API key
gcloud secrets create MAILGUN_API_KEY --data-file=- <<< "your_key"
gcloud secrets create MAILGUN_DOMAIN --data-file=- <<< "medbilldozer.com"
```

### Step 2: Implement Email Service

```bash
# Install mailgun SDK
pip install mailgun

# Create email service
touch backend/app/services/email_service.py
```

Copy implementation from roadmap.

### Step 3: Add Email Inbound Webhook

```bash
# Create email API
touch backend/app/api/email.py
```

```python
from fastapi import APIRouter, Request, BackgroundTasks

router = APIRouter(prefix="/api/email", tags=["email"])

@router.post("/inbound")
async def handle_inbound_email(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle forwarded emails from Mailgun."""
    form_data = await request.form()

    sender = form_data.get("sender")
    recipient = form_data.get("recipient")
    subject = form_data.get("subject")

    # Extract user ID
    user_id = extract_user_id_from_email(recipient)

    # Process attachments
    attachment_count = int(form_data.get("attachment-count", 0))
    for i in range(1, attachment_count + 1):
        attachment = form_data.get(f"attachment-{i}")
        if attachment:
            # Upload and analyze
            background_tasks.add_task(process_email_attachment, user_id, attachment)

    return {"status": "success"}
```

### Step 4: Beta User Recruitment

**Target:** 100 beta users

1. **Invite existing users** (from v0.3)
2. **Post on social media:**
   - Twitter/X
   - LinkedIn
   - Reddit (r/Insurance, r/personalfinance)
3. **Email list:** beta@medbilldozer.com
4. **Offer incentives:** Free premium for 6 months

**Beta Onboarding Checklist:**
- [ ] Welcome email with instructions
- [ ] Setup video tutorial
- [ ] 1-on-1 onboarding calls (first 20 users)
- [ ] Feedback survey
- [ ] Weekly check-ins

---

## Week 9-12: Monitoring & Iteration (Apr 23 - May 14)

### Step 1: Set Up Monitoring

```bash
# Install monitoring tools
pip install sentry-sdk cloud-monitoring

# Configure Sentry
export SENTRY_DSN="your_dsn"
```

In `backend/app/main.py`:
```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0
)
```

### Step 2: Add Analytics

Track key metrics:
- Insurance connection attempts
- Connection success rate
- Claims imported per user
- Time to first analysis
- User satisfaction (NPS)

```python
# backend/app/services/analytics_service.py

class AnalyticsService:
    async def track_event(self, user_id: str, event: str, properties: dict):
        """Track analytics event."""
        await db.insert_analytics_event({
            "user_id": user_id,
            "event": event,
            "properties": properties,
            "timestamp": datetime.utcnow()
        })
```

### Step 3: Daily Sync Job

```bash
# Set up Cloud Scheduler
gcloud scheduler jobs create http daily-insurance-sync \
    --schedule="0 3 * * *" \
    --uri="https://api.medbilldozer.com/api/insurance/sync-all" \
    --http-method=POST \
    --location=us-central1
```

### Step 4: User Feedback Loop

**Weekly Cadence:**
- Monday: Review previous week metrics
- Tuesday: User interviews (3-5 per week)
- Wednesday: Bug fixes & improvements
- Thursday: Deploy updates
- Friday: Monitor & adjust

**Key Questions:**
1. How easy was it to connect insurance?
2. Did you find any billing errors?
3. What features are missing?
4. Would you recommend to others?

---

## Success Criteria Checklist

### Technical:
- [ ] Database migration complete
- [ ] Task queue operational
- [ ] UHC OAuth flow working
- [ ] FHIR data sync working
- [ ] Claims auto-import working
- [ ] Email forwarding working
- [ ] Monitoring configured

### User Metrics:
- [ ] 100 beta users signed up
- [ ] 85%+ connection success rate
- [ ] <5 min average onboarding time
- [ ] 50+ claims auto-imported total
- [ ] 95%+ email forwarding success

### Business:
- [ ] UHC partnership established
- [ ] Mailgun account configured
- [ ] Legal review complete (BAAs)
- [ ] Team hired (4 people)
- [ ] Budget on track

---

## Troubleshooting Guide

### Issue: OAuth flow fails

**Symptoms:** Error after UHC login redirect

**Solutions:**
1. Check redirect URI matches exactly
2. Verify client ID/secret
3. Check state parameter matches
4. Look at UHC API logs

### Issue: Token expired errors

**Symptoms:** Sync fails with 401

**Solutions:**
1. Implement token refresh logic
2. Check token expiry calculation
3. Add retry with refresh

### Issue: Claims not importing

**Symptoms:** Sync completes but no claims

**Solutions:**
1. Check date range (past 6 months)
2. Verify patient ID is correct
3. Check FHIR response format
4. Look for empty entries

### Issue: Email forwarding not working

**Symptoms:** Emails not processed

**Solutions:**
1. Verify Mailgun DNS records
2. Check webhook URL
3. Test with Mailgun logs
4. Verify recipient format

---

## Resources

### Documentation:
- [STREAMLINED_INTAKE_PLAN.md](./STREAMLINED_INTAKE_PLAN.md) - Full strategy
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) - Detailed roadmap
- UHC FHIR Docs: https://developer.uhc.com/docs
- Mailgun Docs: https://documentation.mailgun.com

### Support:
- Engineering Lead: dev@medbilldozer.com
- UHC Support: developer-support@uhc.com
- Mailgun Support: support@mailgun.com

### Team Meetings:
- Daily standup: 9:00 AM PT
- Weekly planning: Monday 10:00 AM PT
- Sprint review: Friday 2:00 PM PT

---

## Next Steps

**Today (Feb 19):**
1. [ ] Review this guide with team
2. [ ] Create project in Jira/Linear
3. [ ] Set up Slack channels (#phase-1-dev, #beta-users)
4. [ ] Schedule kickoff meeting

**This Week:**
1. [ ] Start database migration
2. [ ] Set up Cloud Tasks queue
3. [ ] Register with UHC portal
4. [ ] Hire backend engineers

**Next Week:**
1. [ ] Begin FHIR client implementation
2. [ ] Start legal review (BAAs)
3. [ ] Design beta user onboarding
4. [ ] Create marketing materials

---

**Let's build this! 🚀**

**Questions?** Reach out to: dev@medbilldozer.com

---

**Document prepared by:** MedBillDozer Engineering Team
**Last updated:** February 19, 2026
