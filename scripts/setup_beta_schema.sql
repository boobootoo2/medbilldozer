-- ============================================================================
-- Setup Beta Supabase Schema
-- ============================================================================
-- This creates the exact schema from production for the beta environment
-- Based on: sql/schema_benchmark_monitoring.sql
-- Run this in the beta Supabase SQL editor before syncing data
-- ============================================================================

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- benchmark_transactions: Append-only immutable log
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.benchmark_transactions (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Version control & traceability
    commit_sha TEXT NOT NULL,
    branch_name TEXT,
    
    -- Model versioning
    model_version TEXT NOT NULL,
    model_provider TEXT,
    
    -- Data & prompt versioning
    dataset_version TEXT NOT NULL,
    dataset_size INTEGER,
    prompt_version TEXT NOT NULL,
    
    -- Benchmark type (added via migration)
    benchmark_type TEXT NOT NULL DEFAULT 'standard' CHECK (benchmark_type IN ('standard', 'patient_cross_document')),
    
    -- Environment context
    environment TEXT NOT NULL CHECK (environment IN ('github-actions', 'local', 'staging', 'production')),
    run_id TEXT,
    triggered_by TEXT,
    
    -- Performance metrics (JSONB for flexibility)
    metrics JSONB NOT NULL,
    
    -- Runtime metadata
    duration_seconds NUMERIC(10, 2),
    error_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    
    -- Optional: tags for experimentation
    tags TEXT[],
    notes TEXT,
    
    -- Prevent modifications
    CONSTRAINT immutable_transaction CHECK (created_at <= NOW())
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_transactions_created_at 
    ON public.benchmark_transactions(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_model_version 
    ON public.benchmark_transactions(model_version);

CREATE INDEX IF NOT EXISTS idx_transactions_environment 
    ON public.benchmark_transactions(environment);

CREATE INDEX IF NOT EXISTS idx_transactions_commit 
    ON public.benchmark_transactions(commit_sha);

CREATE INDEX IF NOT EXISTS idx_transactions_model_time 
    ON public.benchmark_transactions(model_version, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_metrics 
    ON public.benchmark_transactions USING GIN(metrics);

CREATE INDEX IF NOT EXISTS idx_transactions_tags 
    ON public.benchmark_transactions USING GIN(tags);

CREATE INDEX IF NOT EXISTS idx_transactions_benchmark_type 
    ON public.benchmark_transactions(benchmark_type);

CREATE INDEX IF NOT EXISTS idx_transactions_type_model 
    ON public.benchmark_transactions(benchmark_type, model_version, created_at DESC);

-- ----------------------------------------------------------------------------
-- benchmark_snapshots: Historical snapshot versioning
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.benchmark_snapshots (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Version tracking
    snapshot_version INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Configuration identifier
    model_version TEXT NOT NULL,
    dataset_version TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    environment TEXT NOT NULL,
    
    -- Link to source transaction
    transaction_id UUID NOT NULL REFERENCES public.benchmark_transactions(id),
    
    -- Snapshot metadata
    commit_sha TEXT NOT NULL,
    
    -- Cached metrics (denormalized for query performance)
    metrics JSONB NOT NULL,
    
    -- Summary statistics
    precision_score NUMERIC(5, 4),
    recall_score NUMERIC(5, 4),
    f1_score NUMERIC(5, 4),
    latency_ms NUMERIC(10, 2),
    cost_per_analysis NUMERIC(10, 6),
    
    -- Benchmark type (added via migration)
    benchmark_type TEXT NOT NULL DEFAULT 'standard' CHECK (benchmark_type IN ('standard', 'patient_cross_document')),
    
    -- Cost savings metrics (added via migration)
    total_potential_savings NUMERIC(10, 2) DEFAULT 0,
    total_missed_savings NUMERIC(10, 2) DEFAULT 0,
    avg_savings_per_patient NUMERIC(10, 2) DEFAULT 0,
    savings_capture_rate NUMERIC(5, 2) DEFAULT 0,
    
    -- Status tracking
    is_current BOOLEAN DEFAULT TRUE,
    is_baseline BOOLEAN DEFAULT FALSE,
    
    -- Soft delete
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Unique constraint
    UNIQUE (model_version, dataset_version, prompt_version, environment, snapshot_version)
);

-- Indexes for snapshot queries
CREATE INDEX IF NOT EXISTS idx_snapshots_created 
    ON public.benchmark_snapshots(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_snapshots_f1 
    ON public.benchmark_snapshots(f1_score DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_snapshots_current 
    ON public.benchmark_snapshots(is_current) WHERE is_current = TRUE;

CREATE INDEX IF NOT EXISTS idx_snapshots_baseline 
    ON public.benchmark_snapshots(is_baseline) WHERE is_baseline = TRUE;

CREATE INDEX IF NOT EXISTS idx_snapshots_config 
    ON public.benchmark_snapshots(model_version, dataset_version, prompt_version, environment);

CREATE INDEX IF NOT EXISTS idx_snapshots_version 
    ON public.benchmark_snapshots(model_version, dataset_version, prompt_version, environment, snapshot_version DESC);

CREATE INDEX IF NOT EXISTS idx_snapshots_benchmark_type 
    ON public.benchmark_snapshots(benchmark_type);

CREATE INDEX IF NOT EXISTS idx_benchmark_snapshots_savings 
    ON public.benchmark_snapshots(total_potential_savings DESC NULLS LAST);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Latest benchmark results across all configurations
CREATE OR REPLACE VIEW public.v_latest_benchmarks AS
SELECT 
    s.model_version,
    s.dataset_version,
    s.prompt_version,
    s.environment,
    s.snapshot_version,
    s.f1_score,
    s.precision_score,
    s.recall_score,
    s.latency_ms,
    s.cost_per_analysis,
    s.created_at,
    s.commit_sha,
    t.run_id,
    t.triggered_by,
    s.metrics
FROM public.benchmark_snapshots s
JOIN public.benchmark_transactions t ON s.transaction_id = t.id
WHERE s.is_current = TRUE
  AND s.is_active = TRUE
ORDER BY s.f1_score DESC;

-- Performance trends over time
CREATE OR REPLACE VIEW public.v_performance_trends AS
SELECT 
    DATE_TRUNC('day', created_at) AS date,
    model_version,
    environment,
    COUNT(*) AS run_count,
    AVG((metrics->>'f1')::NUMERIC) AS avg_f1,
    AVG((metrics->>'precision')::NUMERIC) AS avg_precision,
    AVG((metrics->>'recall')::NUMERIC) AS avg_recall,
    AVG((metrics->>'latency_ms')::NUMERIC) AS avg_latency_ms,
    AVG((metrics->>'analysis_cost')::NUMERIC) AS avg_cost
FROM public.benchmark_transactions
WHERE metrics IS NOT NULL
GROUP BY DATE_TRUNC('day', created_at), model_version, environment
ORDER BY date DESC, model_version;

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Drop any existing policies first
DROP POLICY IF EXISTS "Service role has full access to snapshots" ON public.benchmark_snapshots;
DROP POLICY IF EXISTS "Service role has full access to transactions" ON public.benchmark_transactions;
DROP POLICY IF EXISTS "Public can read snapshots" ON public.benchmark_snapshots;
DROP POLICY IF EXISTS "Public can read transactions" ON public.benchmark_transactions;

-- Enable RLS
ALTER TABLE public.benchmark_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.benchmark_transactions ENABLE ROW LEVEL SECURITY;

-- Service role policies (full access) - MUST come before other policies
CREATE POLICY "Service role has full access to transactions" 
    ON public.benchmark_transactions
    FOR ALL 
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to snapshots" 
    ON public.benchmark_snapshots
    FOR ALL 
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Public read-only policies
CREATE POLICY "Public can read transactions" 
    ON public.benchmark_transactions
    FOR SELECT 
    TO anon, authenticated
    USING (true);

CREATE POLICY "Public can read snapshots" 
    ON public.benchmark_snapshots
    FOR SELECT 
    TO anon, authenticated
    USING (true);

-- ============================================================================
-- FUNCTIONS (RPC endpoints for application)
-- ============================================================================

-- Function: Detect performance regression
CREATE OR REPLACE FUNCTION detect_regression(
    p_model_version TEXT,
    p_threshold NUMERIC DEFAULT 0.05
) RETURNS TABLE (
    current_f1 NUMERIC,
    baseline_f1 NUMERIC,
    f1_drop NUMERIC,
    is_regression BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH current AS (
        SELECT f1_score
        FROM benchmark_snapshots
        WHERE model_version = p_model_version
          AND is_current = TRUE
          AND is_active = TRUE
        LIMIT 1
    ),
    baseline AS (
        SELECT f1_score
        FROM benchmark_snapshots
        WHERE model_version = p_model_version
          AND is_baseline = TRUE
        LIMIT 1
    )
    SELECT 
        c.f1_score AS current_f1,
        b.f1_score AS baseline_f1,
        (b.f1_score - c.f1_score) AS f1_drop,
        (b.f1_score - c.f1_score) > p_threshold AS is_regression
    FROM current c, baseline b;
END;
$$ LANGUAGE plpgsql;

-- Function: Get snapshot history
CREATE OR REPLACE FUNCTION get_snapshot_history(
    p_model_version TEXT,
    p_dataset_version TEXT,
    p_prompt_version TEXT,
    p_environment TEXT,
    p_limit INTEGER DEFAULT 10
) RETURNS TABLE (
    snapshot_version INTEGER,
    created_at TIMESTAMPTZ,
    commit_sha TEXT,
    f1_score NUMERIC,
    precision_score NUMERIC,
    recall_score NUMERIC,
    latency_ms NUMERIC,
    is_current BOOLEAN,
    is_baseline BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.snapshot_version,
        s.created_at,
        s.commit_sha,
        s.f1_score,
        s.precision_score,
        s.recall_score,
        s.latency_ms,
        s.is_current,
        s.is_baseline
    FROM benchmark_snapshots s
    WHERE s.model_version = p_model_version
      AND s.dataset_version = p_dataset_version
      AND s.prompt_version = p_prompt_version
      AND s.environment = p_environment
      AND s.is_active = TRUE
    ORDER BY s.snapshot_version DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function: Checkout (revert to) a specific snapshot version
CREATE OR REPLACE FUNCTION checkout_snapshot(
    p_model_version TEXT,
    p_dataset_version TEXT,
    p_prompt_version TEXT,
    p_environment TEXT,
    p_snapshot_version INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_snapshot_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM benchmark_snapshots
        WHERE model_version = p_model_version
          AND dataset_version = p_dataset_version
          AND prompt_version = p_prompt_version
          AND environment = p_environment
          AND snapshot_version = p_snapshot_version
          AND is_active = TRUE
    ) INTO v_snapshot_exists;
    
    IF NOT v_snapshot_exists THEN
        RAISE EXCEPTION 'Snapshot version % not found', p_snapshot_version;
    END IF;
    
    UPDATE benchmark_snapshots
    SET is_current = FALSE
    WHERE model_version = p_model_version
      AND dataset_version = p_dataset_version
      AND prompt_version = p_prompt_version
      AND environment = p_environment;
    
    UPDATE benchmark_snapshots
    SET is_current = TRUE
    WHERE model_version = p_model_version
      AND dataset_version = p_dataset_version
      AND prompt_version = p_prompt_version
      AND environment = p_environment
      AND snapshot_version = p_snapshot_version;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function: Compare two snapshot versions
CREATE OR REPLACE FUNCTION compare_snapshots(
    p_model_version TEXT,
    p_dataset_version TEXT,
    p_prompt_version TEXT,
    p_environment TEXT,
    p_version_a INTEGER,
    p_version_b INTEGER
) RETURNS TABLE (
    metric TEXT,
    version_a_value NUMERIC,
    version_b_value NUMERIC,
    delta NUMERIC,
    percent_change NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH snap_a AS (
        SELECT f1_score, precision_score, recall_score, latency_ms, cost_per_analysis
        FROM benchmark_snapshots
        WHERE model_version = p_model_version
          AND dataset_version = p_dataset_version
          AND prompt_version = p_prompt_version
          AND environment = p_environment
          AND snapshot_version = p_version_a
    ),
    snap_b AS (
        SELECT f1_score, precision_score, recall_score, latency_ms, cost_per_analysis
        FROM benchmark_snapshots
        WHERE model_version = p_model_version
          AND dataset_version = p_dataset_version
          AND prompt_version = p_prompt_version
          AND environment = p_environment
          AND snapshot_version = p_version_b
    )
    SELECT 'f1_score'::TEXT, a.f1_score, b.f1_score, 
           b.f1_score - a.f1_score, 
           ((b.f1_score - a.f1_score) / NULLIF(a.f1_score, 0) * 100)
    FROM snap_a a, snap_b b
    UNION ALL
    SELECT 'precision'::TEXT, a.precision_score, b.precision_score, 
           b.precision_score - a.precision_score,
           ((b.precision_score - a.precision_score) / NULLIF(a.precision_score, 0) * 100)
    FROM snap_a a, snap_b b
    UNION ALL
    SELECT 'recall'::TEXT, a.recall_score, b.recall_score, 
           b.recall_score - a.recall_score,
           ((b.recall_score - a.recall_score) / NULLIF(a.recall_score, 0) * 100)
    FROM snap_a a, snap_b b
    UNION ALL
    SELECT 'latency_ms'::TEXT, a.latency_ms, b.latency_ms, 
           b.latency_ms - a.latency_ms,
           ((b.latency_ms - a.latency_ms) / NULLIF(a.latency_ms, 0) * 100)
    FROM snap_a a, snap_b b;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GRANTS
-- ============================================================================

GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT SELECT ON public.benchmark_snapshots TO anon, authenticated;
GRANT SELECT ON public.benchmark_transactions TO anon, authenticated;
GRANT SELECT ON public.v_latest_benchmarks TO anon, authenticated;
GRANT SELECT ON public.v_performance_trends TO anon, authenticated;
GRANT ALL ON public.benchmark_snapshots TO service_role;
GRANT ALL ON public.benchmark_transactions TO service_role;

-- Grant execute on functions
GRANT EXECUTE ON FUNCTION detect_regression(TEXT, NUMERIC) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION get_snapshot_history(TEXT, TEXT, TEXT, TEXT, INTEGER) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION checkout_snapshot(TEXT, TEXT, TEXT, TEXT, INTEGER) TO service_role;
GRANT EXECUTE ON FUNCTION compare_snapshots(TEXT, TEXT, TEXT, TEXT, INTEGER, INTEGER) TO anon, authenticated, service_role;

-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Beta Supabase schema setup complete!';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - benchmark_transactions (with ALL migration columns)';
    RAISE NOTICE '  - benchmark_snapshots (with ALL migration columns)';
    RAISE NOTICE '';
    RAISE NOTICE 'Views created:';
    RAISE NOTICE '  - v_latest_benchmarks';
    RAISE NOTICE '  - v_performance_trends';
    RAISE NOTICE '';
    RAISE NOTICE 'Functions created:';
    RAISE NOTICE '  - detect_regression(model_version, threshold)';
    RAISE NOTICE '  - get_snapshot_history(model, dataset, prompt, env, limit)';
    RAISE NOTICE '  - checkout_snapshot(model, dataset, prompt, env, version)';
    RAISE NOTICE '  - compare_snapshots(model, dataset, prompt, env, v1, v2)';
    RAISE NOTICE '';
    RAISE NOTICE 'RLS Policies:';
    RAISE NOTICE '  - Service role: Full access (INSERT, UPDATE, DELETE, SELECT)';
    RAISE NOTICE '  - Anon/Authenticated: Read-only (SELECT)';
    RAISE NOTICE '';
    RAISE NOTICE 'IMPORTANT: Make sure SUPABASE_BETA_KEY is the SERVICE ROLE key!';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Verify SUPABASE_BETA_KEY env var is the service_role key';
    RAISE NOTICE '  2. Run: python3 scripts/sync_supabase_data.py';
    RAISE NOTICE '  3. Verify beta Streamlit app loads correctly';
    RAISE NOTICE '=================================================';
END $$;
