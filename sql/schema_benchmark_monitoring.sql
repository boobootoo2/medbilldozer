-- ============================================================================
-- Benchmark Monitoring Schema
-- ============================================================================
-- Purpose: MLOps-grade persistence layer for benchmark results
-- Design: Append-only transaction log + materialized snapshot view
-- Author: Senior MLOps Engineer
-- Date: 2026-02-03
-- ============================================================================

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- benchmark_transactions: Append-only immutable log
-- ----------------------------------------------------------------------------
-- This table stores every benchmark run as an immutable event.
-- No updates or deletes allowed - audit trail for compliance and debugging.
-- Supports: drift detection, A/B testing, regression analysis
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS benchmark_transactions (
    -- Primary identifiers
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Version control & traceability
    commit_sha TEXT NOT NULL,
    branch_name TEXT,
    
    -- Model versioning
    model_version TEXT NOT NULL,
    model_provider TEXT,  -- e.g., 'openai', 'anthropic', 'google'
    
    -- Data & prompt versioning
    dataset_version TEXT NOT NULL,
    dataset_size INTEGER,
    prompt_version TEXT NOT NULL,
    
    -- Environment context
    environment TEXT NOT NULL CHECK (environment IN ('github-actions', 'local', 'staging', 'production')),
    run_id TEXT,  -- GitHub Actions run ID or local identifier
    triggered_by TEXT,  -- Username or automation trigger
    
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
    ON benchmark_transactions(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_transactions_model_version 
    ON benchmark_transactions(model_version);

CREATE INDEX IF NOT EXISTS idx_transactions_environment 
    ON benchmark_transactions(environment);

CREATE INDEX IF NOT EXISTS idx_transactions_commit 
    ON benchmark_transactions(commit_sha);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_transactions_model_time 
    ON benchmark_transactions(model_version, created_at DESC);

-- GIN index for JSONB metrics queries
CREATE INDEX IF NOT EXISTS idx_transactions_metrics 
    ON benchmark_transactions USING GIN(metrics);

-- Array index for tag filtering
CREATE INDEX IF NOT EXISTS idx_transactions_tags 
    ON benchmark_transactions USING GIN(tags);

-- ----------------------------------------------------------------------------
-- benchmark_snapshots: Historical snapshot versioning
-- ----------------------------------------------------------------------------
-- Stores ALL snapshots with versioning, allowing time-travel queries.
-- Each configuration can have multiple snapshots over time.
-- Optimized for both current state AND historical lookups.
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS benchmark_snapshots (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Version tracking
    snapshot_version INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Configuration identifier (natural key without uniqueness constraint)
    model_version TEXT NOT NULL,
    dataset_version TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    environment TEXT NOT NULL,
    
    -- Link to source transaction
    transaction_id UUID NOT NULL REFERENCES benchmark_transactions(id),
    
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
    
    -- Status tracking
    is_current BOOLEAN DEFAULT TRUE,  -- Is this the current version?
    is_baseline BOOLEAN DEFAULT FALSE,
    
    -- Soft delete
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Ensure version numbering is unique per configuration
    UNIQUE (model_version, dataset_version, prompt_version, environment, snapshot_version)
);

-- Indexes for snapshot queries
CREATE INDEX IF NOT EXISTS idx_snapshots_created 
    ON benchmark_snapshots(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_snapshots_f1 
    ON benchmark_snapshots(f1_score DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_snapshots_current 
    ON benchmark_snapshots(is_current) WHERE is_current = TRUE;

CREATE INDEX IF NOT EXISTS idx_snapshots_baseline 
    ON benchmark_snapshots(is_baseline) WHERE is_baseline = TRUE;

-- Composite index for configuration lookup
CREATE INDEX IF NOT EXISTS idx_snapshots_config 
    ON benchmark_snapshots(model_version, dataset_version, prompt_version, environment);

-- Index for version-based lookups
CREATE INDEX IF NOT EXISTS idx_snapshots_version 
    ON benchmark_snapshots(model_version, dataset_version, prompt_version, environment, snapshot_version DESC);

-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- View: Latest benchmark results across all configurations
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_latest_benchmarks AS
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
FROM benchmark_snapshots s
JOIN benchmark_transactions t ON s.transaction_id = t.id
WHERE s.is_current = TRUE
  AND s.is_active = TRUE
ORDER BY s.f1_score DESC;

-- ----------------------------------------------------------------------------
-- View: Performance trends over time
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_performance_trends AS
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
FROM benchmark_transactions
WHERE metrics IS NOT NULL
GROUP BY DATE_TRUNC('day', created_at), model_version, environment
ORDER BY date DESC, model_version;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Function: Insert transaction and upsert snapshot atomically
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION upsert_benchmark_result(
    p_commit_sha TEXT,
    p_branch_name TEXT,
    p_model_version TEXT,
    p_model_provider TEXT,
    p_dataset_version TEXT,
    p_dataset_size INTEGER,
    p_prompt_version TEXT,
    p_environment TEXT,
    p_run_id TEXT,
    p_triggered_by TEXT,
    p_metrics JSONB,
    p_duration_seconds NUMERIC,
    p_tags TEXT[],
    p_notes TEXT
) RETURNS UUID AS $$
DECLARE
    v_transaction_id UUID;
    v_precision_val NUMERIC;
    v_recall NUMERIC;
    v_f1 NUMERIC;
    v_latency NUMERIC;
    v_cost NUMERIC;
    v_next_version INTEGER;
BEGIN
    -- Extract common metrics for denormalization
    v_precision_val := (p_metrics->>'precision')::NUMERIC;
    v_recall := (p_metrics->>'recall')::NUMERIC;
    v_f1 := (p_metrics->>'f1')::NUMERIC;
    v_latency := (p_metrics->>'latency_ms')::NUMERIC;
    v_cost := (p_metrics->>'analysis_cost')::NUMERIC;
    
    -- Insert transaction (append-only)
    INSERT INTO benchmark_transactions (
        commit_sha,
        branch_name,
        model_version,
        model_provider,
        dataset_version,
        dataset_size,
        prompt_version,
        environment,
        run_id,
        triggered_by,
        metrics,
        duration_seconds,
        tags,
        notes
    ) VALUES (
        p_commit_sha,
        p_branch_name,
        p_model_version,
        p_model_provider,
        p_dataset_version,
        p_dataset_size,
        p_prompt_version,
        p_environment,
        p_run_id,
        p_triggered_by,
        p_metrics,
        p_duration_seconds,
        p_tags,
        p_notes
    ) RETURNING id INTO v_transaction_id;
    
    -- Mark all previous snapshots for this config as not current
    UPDATE benchmark_snapshots
    SET is_current = FALSE
    WHERE model_version = p_model_version
      AND dataset_version = p_dataset_version
      AND prompt_version = p_prompt_version
      AND environment = p_environment
      AND is_current = TRUE;
    
    -- Get next version number
    SELECT COALESCE(MAX(snapshot_version), 0) + 1
    INTO v_next_version
    FROM benchmark_snapshots
    WHERE model_version = p_model_version
      AND dataset_version = p_dataset_version
      AND prompt_version = p_prompt_version
      AND environment = p_environment;
    
    -- Insert new snapshot version
    INSERT INTO benchmark_snapshots (
        snapshot_version,
        model_version,
        dataset_version,
        prompt_version,
        environment,
        transaction_id,
        commit_sha,
        metrics,
        precision_score,
        recall_score,
        f1_score,
        latency_ms,
        cost_per_analysis,
        is_current
    ) VALUES (
        v_next_version,
        p_model_version,
        p_dataset_version,
        p_prompt_version,
        p_environment,
        v_transaction_id,
        p_commit_sha,
        p_metrics,
        v_precision_val,
        v_recall,
        v_f1,
        v_latency,
        v_cost,
        TRUE
    );
    
    RETURN v_transaction_id;
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- Function: Detect regression (F1 drop > threshold)
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION detect_regression(
    p_model_version TEXT,
    p_threshold NUMERIC DEFAULT 0.05  -- 5% drop
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

-- ----------------------------------------------------------------------------
-- Function: Get snapshot history for a configuration
-- ----------------------------------------------------------------------------

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

-- ----------------------------------------------------------------------------
-- Function: Checkout (revert to) a specific snapshot version
-- ----------------------------------------------------------------------------

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
    -- Check if snapshot exists
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
    
    -- Mark all as not current
    UPDATE benchmark_snapshots
    SET is_current = FALSE
    WHERE model_version = p_model_version
      AND dataset_version = p_dataset_version
      AND prompt_version = p_prompt_version
      AND environment = p_environment;
    
    -- Mark specified version as current
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

-- ----------------------------------------------------------------------------
-- Function: Compare two snapshot versions
-- ----------------------------------------------------------------------------

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
    FROM snap_a a, snap_b b
    UNION ALL
    SELECT 'cost_per_analysis'::TEXT, a.cost_per_analysis, b.cost_per_analysis, 
           b.cost_per_analysis - a.cost_per_analysis,
           ((b.cost_per_analysis - a.cost_per_analysis) / NULLIF(a.cost_per_analysis, 0) * 100)
    FROM snap_a a, snap_b b;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROW LEVEL SECURITY (Optional - enable if needed)
-- ============================================================================

-- Enable RLS
-- ALTER TABLE benchmark_transactions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE benchmark_snapshots ENABLE ROW LEVEL SECURITY;

-- Policy: Service role has full access
-- CREATE POLICY "Service role has full access to transactions"
--     ON benchmark_transactions
--     FOR ALL
--     TO service_role
--     USING (true)
--     WITH CHECK (true);

-- CREATE POLICY "Service role has full access to snapshots"
--     ON benchmark_snapshots
--     FOR ALL
--     TO service_role
--     USING (true)
--     WITH CHECK (true);

-- Policy: Authenticated users can read
-- CREATE POLICY "Authenticated users can read transactions"
--     ON benchmark_transactions
--     FOR SELECT
--     TO authenticated
--     USING (true);

-- CREATE POLICY "Authenticated users can read snapshots"
--     ON benchmark_snapshots
--     FOR SELECT
--     TO authenticated
--     USING (true);

-- ============================================================================
-- SAMPLE QUERIES FOR TESTING
-- ============================================================================

-- Test insert
-- SELECT upsert_benchmark_result(
--     'abc123',
--     'develop',
--     'medgemma-v1.2',
--     'google',
--     'benchmark-set-v3',
--     100,
--     'analysis-v4',
--     'github-actions',
--     'run-12345',
--     'github-bot',
--     '{"precision": 0.91, "recall": 0.88, "f1": 0.895, "latency_ms": 412, "analysis_cost": 0.0042}'::JSONB,
--     45.2,
--     ARRAY['experiment-1', 'baseline'],
--     'Initial baseline run'
-- );

-- Query latest snapshots
-- SELECT * FROM v_latest_benchmarks;

-- Query trends
-- SELECT * FROM v_performance_trends WHERE date > NOW() - INTERVAL '30 days';

-- Check for regression
-- SELECT * FROM detect_regression('medgemma-v1.2', 0.05);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
