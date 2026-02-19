-- MedBillDozer Production API Schema Extensions (Safe to Re-run)
-- This extends existing Supabase schemas with user profile and document management

-- ============================================================================
-- USER PROFILES
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    display_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_firebase_uid ON user_profiles(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_created_at ON user_profiles(created_at DESC);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE
    ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- DOCUMENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    gcs_path TEXT NOT NULL,
    content_type TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'uploaded'
        CHECK (status IN ('uploaded', 'processing', 'analyzing', 'completed', 'failed')),
    document_type TEXT CHECK (document_type IN (
        'medical_bill', 'dental_bill', 'insurance_eob', 'pharmacy_receipt',
        'fsa_claim', 'clinical_image', 'other'
    )),
    extracted_text TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,
    CONSTRAINT unique_user_gcs_path UNIQUE (user_id, gcs_path)
);

CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at ON documents(uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type);

-- ============================================================================
-- ANALYSES
-- ============================================================================

CREATE TABLE IF NOT EXISTS analyses (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    document_ids UUID[] NOT NULL,
    provider TEXT NOT NULL DEFAULT 'medgemma-ensemble',
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    results JSONB,
    coverage_matrix JSONB,
    total_savings_detected NUMERIC(10, 2),
    issues_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    processing_time_seconds INTEGER,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_completed_at ON analyses(completed_at DESC);

-- Trigger to calculate processing time
CREATE OR REPLACE FUNCTION calculate_processing_time()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'completed' AND NEW.started_at IS NOT NULL THEN
        NEW.processing_time_seconds = EXTRACT(EPOCH FROM (NOW() - NEW.started_at))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_analyses_processing_time ON analyses;
CREATE TRIGGER update_analyses_processing_time BEFORE UPDATE
    ON analyses FOR EACH ROW EXECUTE FUNCTION calculate_processing_time();

-- ============================================================================
-- ISSUES (Billing Issues Detected)
-- ============================================================================

CREATE TABLE IF NOT EXISTS issues (
    issue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES analyses(analysis_id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(document_id) ON DELETE CASCADE,
    issue_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    evidence TEXT,
    code TEXT,
    recommended_action TEXT,
    max_savings NUMERIC(10, 2) DEFAULT 0,
    confidence TEXT CHECK (confidence IN ('high', 'medium', 'low')),
    source TEXT CHECK (source IN ('llm', 'deterministic', 'clinical')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_issues_analysis_id ON issues(analysis_id);
CREATE INDEX IF NOT EXISTS idx_issues_document_id ON issues(document_id);
CREATE INDEX IF NOT EXISTS idx_issues_issue_type ON issues(issue_type);
CREATE INDEX IF NOT EXISTS idx_issues_max_savings ON issues(max_savings DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables (safe to run multiple times)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE issues ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist, then create them
DROP POLICY IF EXISTS "Users can view their own profile" ON user_profiles;
CREATE POLICY "Users can view their own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid()::text = firebase_uid);

DROP POLICY IF EXISTS "Users can update their own profile" ON user_profiles;
CREATE POLICY "Users can update their own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid()::text = firebase_uid);

DROP POLICY IF EXISTS "Users can view their own documents" ON documents;
CREATE POLICY "Users can view their own documents"
    ON documents FOR SELECT
    USING (user_id IN (SELECT user_id FROM user_profiles WHERE firebase_uid = auth.uid()::text));

DROP POLICY IF EXISTS "Users can insert their own documents" ON documents;
CREATE POLICY "Users can insert their own documents"
    ON documents FOR INSERT
    WITH CHECK (user_id IN (SELECT user_id FROM user_profiles WHERE firebase_uid = auth.uid()::text));

DROP POLICY IF EXISTS "Users can delete their own documents" ON documents;
CREATE POLICY "Users can delete their own documents"
    ON documents FOR DELETE
    USING (user_id IN (SELECT user_id FROM user_profiles WHERE firebase_uid = auth.uid()::text));

DROP POLICY IF EXISTS "Users can view their own analyses" ON analyses;
CREATE POLICY "Users can view their own analyses"
    ON analyses FOR SELECT
    USING (user_id IN (SELECT user_id FROM user_profiles WHERE firebase_uid = auth.uid()::text));

DROP POLICY IF EXISTS "Users can insert their own analyses" ON analyses;
CREATE POLICY "Users can insert their own analyses"
    ON analyses FOR INSERT
    WITH CHECK (user_id IN (SELECT user_id FROM user_profiles WHERE firebase_uid = auth.uid()::text));

DROP POLICY IF EXISTS "Users can view issues from their analyses" ON issues;
CREATE POLICY "Users can view issues from their analyses"
    ON issues FOR SELECT
    USING (analysis_id IN (
        SELECT analysis_id FROM analyses
        WHERE user_id IN (SELECT user_id FROM user_profiles WHERE firebase_uid = auth.uid()::text)
    ));

-- ============================================================================
-- VIEWS
-- ============================================================================

-- User analytics view
CREATE OR REPLACE VIEW user_analytics AS
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

-- Recent activity view
CREATE OR REPLACE VIEW recent_activity AS
SELECT
    'analysis' as activity_type,
    a.analysis_id as id,
    a.user_id,
    a.status,
    a.created_at,
    a.completed_at,
    a.total_savings_detected as value
FROM analyses a
UNION ALL
SELECT
    'document' as activity_type,
    d.document_id as id,
    d.user_id,
    d.status,
    d.uploaded_at as created_at,
    NULL as completed_at,
    NULL as value
FROM documents d
ORDER BY created_at DESC;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to get user ID from Firebase UID
CREATE OR REPLACE FUNCTION get_user_id_from_firebase_uid(firebase_uid_param TEXT)
RETURNS UUID AS $$
    SELECT user_id FROM user_profiles WHERE firebase_uid = firebase_uid_param;
$$ LANGUAGE SQL STABLE;

-- Function to increment analysis issues count
CREATE OR REPLACE FUNCTION increment_analysis_issues_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE analyses
    SET issues_count = issues_count + 1
    WHERE analysis_id = NEW.analysis_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS increment_issues_count_trigger ON issues;
CREATE TRIGGER increment_issues_count_trigger
    AFTER INSERT ON issues
    FOR EACH ROW EXECUTE FUNCTION increment_analysis_issues_count();

-- ============================================================================
-- GRANTS (Service Role)
-- ============================================================================

GRANT ALL ON user_profiles TO service_role;
GRANT ALL ON documents TO service_role;
GRANT ALL ON analyses TO service_role;
GRANT ALL ON issues TO service_role;
