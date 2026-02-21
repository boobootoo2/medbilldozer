-- Migration: Add Insurance Integration Tables
-- Version: 001
-- Date: 2026-02-19
-- Description: Adds tables for insurance connections, benefits, claims, and sync jobs

-- ============================================================================
-- INSURANCE CONNECTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS insurance_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    payer_id VARCHAR(100) NOT NULL,  -- e.g., "uhc", "anthem", "aetna"
    payer_name VARCHAR(255) NOT NULL,
    member_id VARCHAR(100),
    connection_type VARCHAR(50) NOT NULL,  -- 'fhir_oauth', 'api_key', 'manual'
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    token_expires_at TIMESTAMPTZ,
    last_sync_at TIMESTAMPTZ,
    sync_status VARCHAR(50) DEFAULT 'active',  -- 'active', 'error', 'disconnected'
    sync_error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_connection_type CHECK (
        connection_type IN ('fhir_oauth', 'api_key', 'manual', 'pverify')
    ),
    CONSTRAINT valid_sync_status CHECK (
        sync_status IN ('active', 'syncing', 'error', 'disconnected')
    )
);

-- ============================================================================
-- INSURANCE BENEFITS
-- ============================================================================

CREATE TABLE IF NOT EXISTS insurance_benefits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id UUID NOT NULL REFERENCES insurance_connections(id) ON DELETE CASCADE,
    plan_year INT NOT NULL,
    deductible_individual DECIMAL(10,2),
    deductible_family DECIMAL(10,2),
    deductible_met DECIMAL(10,2) DEFAULT 0,
    oop_max_individual DECIMAL(10,2),
    oop_max_family DECIMAL(10,2),
    oop_met DECIMAL(10,2) DEFAULT 0,
    copay_primary_care DECIMAL(10,2),
    copay_specialist DECIMAL(10,2),
    copay_er DECIMAL(10,2),
    copay_urgent_care DECIMAL(10,2),
    coverage_details JSONB,  -- Full FHIR Coverage resource
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(connection_id, plan_year)
);

-- ============================================================================
-- CLAIMS
-- ============================================================================

CREATE TABLE IF NOT EXISTS claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id UUID NOT NULL REFERENCES insurance_connections(id) ON DELETE CASCADE,
    claim_number VARCHAR(100),
    service_date DATE NOT NULL,
    provider_name VARCHAR(255),
    provider_npi VARCHAR(20),
    billed_amount DECIMAL(10,2),
    allowed_amount DECIMAL(10,2),
    paid_by_insurance DECIMAL(10,2),
    patient_responsibility DECIMAL(10,2),
    claim_status VARCHAR(50),  -- 'processed', 'pending', 'denied', 'appealed'
    denial_reason TEXT,
    procedure_codes JSONB,  -- Array of CPT/HCPCS codes
    diagnosis_codes JSONB,  -- Array of ICD-10 codes
    in_network BOOLEAN,
    raw_data JSONB,  -- Full FHIR ExplanationOfBenefit resource
    imported_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_claim_status CHECK (
        claim_status IN ('processed', 'pending', 'denied', 'appealed', 'paid')
    )
);

-- ============================================================================
-- DENTAL INSURANCE CONNECTIONS
-- ============================================================================

CREATE TABLE IF NOT EXISTS dental_insurance_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    payer_id VARCHAR(100) NOT NULL,
    payer_name VARCHAR(255) NOT NULL,
    member_id VARCHAR(100) NOT NULL,
    connection_type VARCHAR(50) NOT NULL DEFAULT 'zuub',  -- 'zuub', 'pverify', 'manual'
    annual_maximum DECIMAL(10,2),
    annual_maximum_remaining DECIMAL(10,2),
    coverage_details JSONB,  -- Procedure coverage percentages, frequency limits
    last_verified_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_dental_connection_type CHECK (
        connection_type IN ('zuub', 'pverify', 'manual')
    )
);

-- ============================================================================
-- SYNC JOBS
-- ============================================================================

CREATE TABLE IF NOT EXISTS sync_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL,  -- 'insurance_sync', 'claims_import', 'portal_sync'
    connection_id UUID REFERENCES insurance_connections(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'running', 'completed', 'failed'
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    result JSONB,  -- Sync results (claims imported, errors, etc.)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_job_type CHECK (
        job_type IN ('insurance_sync', 'claims_import', 'portal_sync', 'benefit_check', 'dental_sync')
    ),
    CONSTRAINT valid_job_status CHECK (
        status IN ('pending', 'running', 'completed', 'failed', 'cancelled')
    )
);

-- ============================================================================
-- ALERTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,  -- 'new_claim', 'billing_error', 'deductible_reset', etc.
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'
    related_claim_id UUID REFERENCES claims(id) ON DELETE SET NULL,
    related_document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    data JSONB,  -- Additional alert data
    read BOOLEAN DEFAULT FALSE,
    dismissed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT valid_alert_type CHECK (
        alert_type IN ('new_claim', 'billing_error', 'bill_incoming', 'deductible_reset',
                      'out_of_network', 'claim_denied', 'savings_found')
    ),
    CONSTRAINT valid_priority CHECK (
        priority IN ('low', 'medium', 'high', 'critical')
    )
);

-- ============================================================================
-- LINK DOCUMENTS TO CLAIMS
-- ============================================================================

-- Add foreign key to existing documents table
ALTER TABLE documents
ADD COLUMN IF NOT EXISTS linked_claim_id UUID REFERENCES claims(id) ON DELETE SET NULL;

ALTER TABLE documents
ADD COLUMN IF NOT EXISTS match_confidence DECIMAL(3,2);  -- 0.00 to 1.00

ALTER TABLE documents
ADD COLUMN IF NOT EXISTS match_type VARCHAR(50);  -- 'exact_claim_number', 'fuzzy_date_provider', 'amount_date'

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Insurance connections
CREATE INDEX IF NOT EXISTS idx_insurance_connections_user_id
ON insurance_connections(user_id);

CREATE INDEX IF NOT EXISTS idx_insurance_connections_payer
ON insurance_connections(payer_id);

CREATE INDEX IF NOT EXISTS idx_insurance_connections_status
ON insurance_connections(sync_status) WHERE sync_status != 'disconnected';

-- Insurance benefits
CREATE INDEX IF NOT EXISTS idx_insurance_benefits_connection_id
ON insurance_benefits(connection_id);

CREATE INDEX IF NOT EXISTS idx_insurance_benefits_year
ON insurance_benefits(plan_year DESC);

-- Claims
CREATE INDEX IF NOT EXISTS idx_claims_connection_id
ON claims(connection_id);

CREATE INDEX IF NOT EXISTS idx_claims_service_date
ON claims(service_date DESC);

CREATE INDEX IF NOT EXISTS idx_claims_claim_number
ON claims(claim_number) WHERE claim_number IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_claims_status
ON claims(claim_status);

CREATE INDEX IF NOT EXISTS idx_claims_imported
ON claims(imported_at DESC);

-- Dental connections
CREATE INDEX IF NOT EXISTS idx_dental_connections_user_id
ON dental_insurance_connections(user_id);

-- Sync jobs
CREATE INDEX IF NOT EXISTS idx_sync_jobs_status
ON sync_jobs(status) WHERE status IN ('pending', 'running');

CREATE INDEX IF NOT EXISTS idx_sync_jobs_connection
ON sync_jobs(connection_id);

CREATE INDEX IF NOT EXISTS idx_sync_jobs_created
ON sync_jobs(created_at DESC);

-- Alerts
CREATE INDEX IF NOT EXISTS idx_user_alerts_user_id
ON user_alerts(user_id);

CREATE INDEX IF NOT EXISTS idx_user_alerts_unread
ON user_alerts(user_id, created_at DESC) WHERE read = FALSE;

CREATE INDEX IF NOT EXISTS idx_user_alerts_priority
ON user_alerts(priority, created_at DESC) WHERE read = FALSE;

-- Documents with claims
CREATE INDEX IF NOT EXISTS idx_documents_linked_claim
ON documents(linked_claim_id) WHERE linked_claim_id IS NOT NULL;

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE insurance_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE insurance_benefits ENABLE ROW LEVEL SECURITY;
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE dental_insurance_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_alerts ENABLE ROW LEVEL SECURITY;

-- Insurance Connections: Users see only their own
CREATE POLICY "Users see only own insurance connections"
ON insurance_connections
FOR ALL
USING (auth.uid() = user_id);

-- Insurance Benefits: Users see only their own through connections
CREATE POLICY "Users see only own insurance benefits"
ON insurance_benefits
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM insurance_connections
        WHERE insurance_connections.id = insurance_benefits.connection_id
        AND insurance_connections.user_id = auth.uid()
    )
);

-- Claims: Users see only their own through connections
CREATE POLICY "Users see only own claims"
ON claims
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM insurance_connections
        WHERE insurance_connections.id = claims.connection_id
        AND insurance_connections.user_id = auth.uid()
    )
);

-- Dental Connections: Users see only their own
CREATE POLICY "Users see only own dental connections"
ON dental_insurance_connections
FOR ALL
USING (auth.uid() = user_id);

-- Sync Jobs: Users see only jobs for their connections
CREATE POLICY "Users see only own sync jobs"
ON sync_jobs
FOR ALL
USING (
    connection_id IS NULL OR EXISTS (
        SELECT 1 FROM insurance_connections
        WHERE insurance_connections.id = sync_jobs.connection_id
        AND insurance_connections.user_id = auth.uid()
    )
);

-- Alerts: Users see only their own
CREATE POLICY "Users see only own alerts"
ON user_alerts
FOR ALL
USING (auth.uid() = user_id);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update updated_at timestamp on insurance_connections
CREATE OR REPLACE FUNCTION update_insurance_connections_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_insurance_connections_updated_at
    BEFORE UPDATE ON insurance_connections
    FOR EACH ROW
    EXECUTE FUNCTION update_insurance_connections_updated_at();

-- ============================================================================
-- INITIAL DATA / SEED DATA
-- ============================================================================

-- Add supported payers (reference data)
CREATE TABLE IF NOT EXISTS supported_payers (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    logo_url VARCHAR(500),
    supports_fhir BOOLEAN DEFAULT FALSE,
    supports_pverify BOOLEAN DEFAULT TRUE,
    category VARCHAR(50),  -- 'major', 'regional', 'medicaid', 'medicare'
    market_share_percent DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO supported_payers (id, name, supports_fhir, category, market_share_percent) VALUES
('uhc', 'UnitedHealthcare', TRUE, 'major', 14.5),
('anthem', 'Anthem/Elevance', TRUE, 'major', 13.2),
('aetna', 'Aetna (CVS Health)', TRUE, 'major', 11.8),
('cigna', 'Cigna', TRUE, 'major', 6.4),
('humana', 'Humana', TRUE, 'major', 5.7),
('bcbs', 'Blue Cross Blue Shield', TRUE, 'major', 30.0),
('kaiser', 'Kaiser Permanente', TRUE, 'major', 7.1)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: User insurance summary
CREATE OR REPLACE VIEW user_insurance_summary AS
SELECT
    ic.user_id,
    ic.id AS connection_id,
    ic.payer_name,
    ic.member_id,
    ic.sync_status,
    ic.last_sync_at,
    ib.deductible_individual,
    ib.deductible_met,
    ib.oop_max_individual,
    ib.oop_met,
    COUNT(DISTINCT c.id) AS total_claims,
    SUM(c.patient_responsibility) AS total_patient_responsibility,
    SUM(c.paid_by_insurance) AS total_paid_by_insurance
FROM insurance_connections ic
LEFT JOIN insurance_benefits ib ON ic.id = ib.connection_id
    AND ib.plan_year = EXTRACT(YEAR FROM CURRENT_DATE)
LEFT JOIN claims c ON ic.id = c.connection_id
GROUP BY ic.user_id, ic.id, ic.payer_name, ic.member_id, ic.sync_status,
         ic.last_sync_at, ib.deductible_individual, ib.deductible_met,
         ib.oop_max_individual, ib.oop_met;

-- View: Recent unmatched claims (potential for document matching)
CREATE OR REPLACE VIEW unmatched_claims AS
SELECT
    c.*,
    ic.user_id
FROM claims c
JOIN insurance_connections ic ON c.connection_id = ic.id
WHERE NOT EXISTS (
    SELECT 1 FROM documents d
    WHERE d.linked_claim_id = c.id
)
AND c.service_date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY c.service_date DESC;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE insurance_connections IS 'Stores user connections to insurance payers via FHIR OAuth or API keys';
COMMENT ON TABLE insurance_benefits IS 'Cached insurance benefits data from payer APIs (deductibles, copays, etc.)';
COMMENT ON TABLE claims IS 'Insurance claims imported from payer APIs (ExplanationOfBenefit resources)';
COMMENT ON TABLE dental_insurance_connections IS 'Dental insurance connections (via Zuub or pVerify)';
COMMENT ON TABLE sync_jobs IS 'Background job tracking for insurance data synchronization';
COMMENT ON TABLE user_alerts IS 'Proactive alerts for users (new claims, billing errors, etc.)';
COMMENT ON TABLE supported_payers IS 'Reference data for supported insurance payers';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 001_add_insurance_tables.sql completed successfully';
    RAISE NOTICE 'Created tables: insurance_connections, insurance_benefits, claims, dental_insurance_connections, sync_jobs, user_alerts, supported_payers';
    RAISE NOTICE 'Added indexes, RLS policies, triggers, and views';
END $$;
