-- ============================================================================
-- Clinical Validation Snapshots Table
-- ============================================================================
-- This table stores clinical validation benchmark results with multi-modal
-- medical image analysis data.
--
-- Usage:
--   Run this SQL in your production Supabase SQL Editor
--   or via psql/Supabase CLI
-- ============================================================================

-- Create clinical_validation_snapshots table
CREATE TABLE IF NOT EXISTS public.clinical_validation_snapshots (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Model and versioning
    model_version TEXT NOT NULL,
    dataset_version TEXT DEFAULT 'clinical_validation_v1',
    prompt_version TEXT DEFAULT 'v1',

    -- Environment and metadata
    environment TEXT DEFAULT 'production',
    benchmark_type TEXT DEFAULT 'clinical_validation',
    triggered_by TEXT,

    -- Performance metrics (stored as JSONB for flexibility)
    metrics JSONB,

    -- Detailed scenario results
    scenario_results JSONB,

    -- Denormalized fields for easier querying (populated by trigger)
    total_patients INTEGER,
    successful INTEGER,
    failed INTEGER,
    f1_score NUMERIC,
    precision_score NUMERIC,
    recall NUMERIC,
    domain_detection NUMERIC,
    avg_confidence NUMERIC,
    performance_data JSONB
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- Index on created_at for time-series queries
CREATE INDEX IF NOT EXISTS idx_clinical_snapshots_created_at
ON public.clinical_validation_snapshots(created_at DESC);

-- Index on model_version for filtering
CREATE INDEX IF NOT EXISTS idx_clinical_snapshots_model
ON public.clinical_validation_snapshots(model_version);

-- Index on environment for filtering
CREATE INDEX IF NOT EXISTS idx_clinical_snapshots_environment
ON public.clinical_validation_snapshots(environment);

-- Composite index for dashboard queries
CREATE INDEX IF NOT EXISTS idx_clinical_snapshots_env_created
ON public.clinical_validation_snapshots(environment, created_at DESC);

-- Index on benchmark_type for filtering
CREATE INDEX IF NOT EXISTS idx_clinical_snapshots_type
ON public.clinical_validation_snapshots(benchmark_type);

-- ============================================================================
-- Row Level Security (RLS)
-- ============================================================================

-- Enable RLS
ALTER TABLE public.clinical_validation_snapshots ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for idempotency)
DROP POLICY IF EXISTS "Service role has full access" ON public.clinical_validation_snapshots;
DROP POLICY IF EXISTS "Authenticated users can read" ON public.clinical_validation_snapshots;
DROP POLICY IF EXISTS "Anon users can read" ON public.clinical_validation_snapshots;
DROP POLICY IF EXISTS "Only service role can insert" ON public.clinical_validation_snapshots;
DROP POLICY IF EXISTS "Only service role can update" ON public.clinical_validation_snapshots;
DROP POLICY IF EXISTS "Only service role can delete" ON public.clinical_validation_snapshots;

-- Policy: Allow service role full access
CREATE POLICY "Service role has full access"
ON public.clinical_validation_snapshots
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Policy: Allow authenticated users to read
CREATE POLICY "Authenticated users can read"
ON public.clinical_validation_snapshots
FOR SELECT
TO authenticated
USING (true);

-- Policy: Allow anon users to read (for dashboard)
CREATE POLICY "Anon users can read"
ON public.clinical_validation_snapshots
FOR SELECT
TO anon
USING (true);

-- Policy: Only service role can insert
CREATE POLICY "Only service role can insert"
ON public.clinical_validation_snapshots
FOR INSERT
TO service_role
WITH CHECK (true);

-- Policy: Only service role can update
CREATE POLICY "Only service role can update"
ON public.clinical_validation_snapshots
FOR UPDATE
TO service_role
USING (true)
WITH CHECK (true);

-- Policy: Only service role can delete
CREATE POLICY "Only service role can delete"
ON public.clinical_validation_snapshots
FOR DELETE
TO service_role
USING (true);

-- ============================================================================
-- Triggers
-- ============================================================================

-- Function to compute denormalized fields from metrics JSONB
CREATE OR REPLACE FUNCTION compute_clinical_snapshot_fields()
RETURNS TRIGGER AS $$
BEGIN
    -- Extract and compute fields from metrics JSONB
    NEW.total_patients := COALESCE((NEW.metrics->>'total_scenarios')::INTEGER, 0);
    NEW.successful := COALESCE((NEW.metrics->>'correct_determinations')::INTEGER, 0);
    NEW.failed := COALESCE(
        (NEW.metrics->>'total_scenarios')::INTEGER -
        (NEW.metrics->>'correct_determinations')::INTEGER,
        0
    );
    NEW.f1_score := COALESCE((NEW.metrics->>'accuracy')::NUMERIC, 0);
    NEW.precision_score := COALESCE((NEW.metrics->>'error_detection_rate')::NUMERIC, 0);
    NEW.recall := COALESCE((NEW.metrics->>'error_detection_rate')::NUMERIC, 0);
    NEW.domain_detection := COALESCE((NEW.metrics->>'error_detection_rate')::NUMERIC * 100, 0);
    NEW.avg_confidence := COALESCE((NEW.metrics->>'accuracy')::NUMERIC, 0);

    -- Build performance_data JSONB
    NEW.performance_data := jsonb_build_object(
        'accuracy', (NEW.metrics->>'accuracy')::NUMERIC,
        'error_detection_rate', (NEW.metrics->>'error_detection_rate')::NUMERIC,
        'false_positive_rate', (NEW.metrics->>'false_positive_rate')::NUMERIC,
        'total_scenarios', (NEW.metrics->>'total_scenarios')::INTEGER,
        'correct_determinations', (NEW.metrics->>'correct_determinations')::INTEGER
    );

    -- Update timestamp
    NEW.updated_at := NOW();

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to compute fields on INSERT or UPDATE
CREATE TRIGGER trigger_compute_clinical_snapshot_fields
BEFORE INSERT OR UPDATE ON public.clinical_validation_snapshots
FOR EACH ROW
EXECUTE FUNCTION compute_clinical_snapshot_fields();

-- ============================================================================
-- Grants
-- ============================================================================

-- Grant SELECT to anon role (for public dashboard access)
GRANT SELECT ON public.clinical_validation_snapshots TO anon;

-- Grant SELECT to authenticated role
GRANT SELECT ON public.clinical_validation_snapshots TO authenticated;

-- Grant ALL to service role
GRANT ALL ON public.clinical_validation_snapshots TO service_role;

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE public.clinical_validation_snapshots IS
'Clinical validation benchmark results with multi-modal medical image analysis';

COMMENT ON COLUMN public.clinical_validation_snapshots.metrics IS
'Performance metrics including accuracy, error_detection_rate, false_positive_rate, etc.';

COMMENT ON COLUMN public.clinical_validation_snapshots.scenario_results IS
'Detailed results for each clinical scenario tested';

COMMENT ON COLUMN public.clinical_validation_snapshots.domain_detection IS
'Percentage of domain-specific errors detected (computed from error_detection_rate)';

-- ============================================================================
-- Sample Query
-- ============================================================================

-- Verify the table was created successfully
-- SELECT
--     id,
--     created_at,
--     model_version,
--     environment,
--     total_patients,
--     successful,
--     failed,
--     domain_detection
-- FROM public.clinical_validation_snapshots
-- ORDER BY created_at DESC
-- LIMIT 10;
