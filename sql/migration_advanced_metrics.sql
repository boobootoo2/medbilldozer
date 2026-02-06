-- ============================================================================
-- Advanced Metrics Migration for MedBillDozer Benchmark Tracking
-- ============================================================================
-- Author: Senior ML Infrastructure Engineer
-- Date: 2026-02-05
-- Purpose: Add risk-weighted recall, category tracking, ROI, and hybrid model support
-- 
-- BACKWARD COMPATIBLE: Does not modify existing schema, only adds new capabilities
-- ============================================================================

-- ============================================================================
-- 1. CREATE CATEGORY-LEVEL TRACKING TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS benchmark_category_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    benchmark_run_id UUID NOT NULL,
    category TEXT NOT NULL,
    total INT NOT NULL,
    detected INT NOT NULL,
    detection_rate FLOAT NOT NULL,
    delta_from_previous FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key to benchmark_transactions (append-only log)
    CONSTRAINT fk_benchmark_run 
        FOREIGN KEY (benchmark_run_id) 
        REFERENCES benchmark_transactions(id) 
        ON DELETE CASCADE
);

-- Index for fast lookups by benchmark run
CREATE INDEX IF NOT EXISTS idx_category_metrics_benchmark_run 
    ON benchmark_category_metrics(benchmark_run_id);

-- Composite index for category queries
CREATE INDEX IF NOT EXISTS idx_category_metrics_category 
    ON benchmark_category_metrics(benchmark_run_id, category);

-- Index for time-series analysis
CREATE INDEX IF NOT EXISTS idx_category_metrics_created_at 
    ON benchmark_category_metrics(created_at DESC);

COMMENT ON TABLE benchmark_category_metrics IS 
    'Category-level performance metrics with regression tracking';

COMMENT ON COLUMN benchmark_category_metrics.delta_from_previous IS 
    'Change in detection rate from previous run (NULL for first run)';

-- ============================================================================
-- 2. ADD ADVANCED METRICS SUPPORT TO EXISTING TABLES
-- ============================================================================

-- The following metrics will be stored in the existing `metrics` JSONB column
-- No schema changes needed - JSONB is flexible and backward compatible
--
-- New keys that can be stored in benchmark_transactions.metrics:
-- - risk_weighted_recall: FLOAT (0.0 to 1.0)
-- - conservatism_index: FLOAT (0.0 to 1.0, FN / (FN + FP))
-- - false_negatives: INT
-- - false_positives: INT  
-- - true_positives: INT
-- - p95_latency_ms: FLOAT
-- - roi_ratio: FLOAT (savings / inference_cost)
-- - inference_cost_usd: FLOAT
-- - unique_detections: INT (for hybrid models)
-- - overlap_detections: INT (for hybrid models)
-- - complementarity_gain: FLOAT (for hybrid models)
--
-- All existing keys remain untouched for backward compatibility

-- ============================================================================
-- 3. CREATE HELPER FUNCTION FOR CATEGORY REGRESSION CALCULATION
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_category_delta(
    p_model_version TEXT,
    p_category TEXT,
    p_current_rate FLOAT,
    p_environment TEXT DEFAULT 'local'
)
RETURNS FLOAT
LANGUAGE plpgsql
AS $$
DECLARE
    v_previous_rate FLOAT;
    v_delta FLOAT;
BEGIN
    -- Get the most recent previous detection rate for this model and category
    SELECT 
        detection_rate INTO v_previous_rate
    FROM benchmark_category_metrics bcm
    INNER JOIN benchmark_transactions bt ON bcm.benchmark_run_id = bt.id
    WHERE 
        bt.model_version = p_model_version
        AND bcm.category = p_category
        AND bt.environment = p_environment
    ORDER BY bcm.created_at DESC
    LIMIT 1 OFFSET 1; -- Skip the current run, get the previous one
    
    -- Calculate delta (NULL if no previous run)
    IF v_previous_rate IS NOT NULL THEN
        v_delta := p_current_rate - v_previous_rate;
    ELSE
        v_delta := NULL;
    END IF;
    
    RETURN v_delta;
END;
$$;

COMMENT ON FUNCTION calculate_category_delta IS 
    'Calculate detection rate change from previous run for regression tracking';

-- ============================================================================
-- 4. CREATE VIEW FOR ADVANCED METRICS ANALYSIS
-- ============================================================================

CREATE OR REPLACE VIEW v_advanced_benchmark_metrics AS
SELECT 
    bt.id as benchmark_run_id,
    bt.model_version,
    bt.model_provider,
    bt.environment,
    bt.created_at,
    bt.commit_sha,
    
    -- Standard metrics
    (bt.metrics->>'precision')::FLOAT as precision,
    (bt.metrics->>'recall')::FLOAT as recall,
    (bt.metrics->>'f1')::FLOAT as f1_score,
    (bt.metrics->>'latency_ms')::FLOAT as avg_latency_ms,
    
    -- Advanced metrics (new, nullable for backward compatibility)
    (bt.metrics->>'risk_weighted_recall')::FLOAT as risk_weighted_recall,
    (bt.metrics->>'conservatism_index')::FLOAT as conservatism_index,
    (bt.metrics->>'p95_latency_ms')::FLOAT as p95_latency_ms,
    (bt.metrics->>'roi_ratio')::FLOAT as roi_ratio,
    (bt.metrics->>'inference_cost_usd')::FLOAT as inference_cost_usd,
    
    -- Confusion matrix
    (bt.metrics->>'true_positives')::INT as true_positives,
    (bt.metrics->>'false_positives')::INT as false_positives,
    (bt.metrics->>'false_negatives')::INT as false_negatives,
    
    -- Hybrid model metrics
    (bt.metrics->>'unique_detections')::INT as unique_detections,
    (bt.metrics->>'overlap_detections')::INT as overlap_detections,
    (bt.metrics->>'complementarity_gain')::FLOAT as complementarity_gain,
    
    -- Cost savings
    (bt.metrics->>'total_potential_savings')::FLOAT as total_potential_savings,
    (bt.metrics->>'savings_capture_rate')::FLOAT as savings_capture_rate
    
FROM benchmark_transactions bt
ORDER BY bt.created_at DESC;

COMMENT ON VIEW v_advanced_benchmark_metrics IS 
    'Unified view of standard and advanced benchmark metrics with null-safe extraction';

-- ============================================================================
-- 5. CREATE VIEW FOR CATEGORY REGRESSION TRACKING
-- ============================================================================

CREATE OR REPLACE VIEW v_category_regression_tracking AS
WITH ranked_metrics AS (
    SELECT 
        bcm.*,
        bt.model_version,
        bt.environment,
        ROW_NUMBER() OVER (
            PARTITION BY bt.model_version, bcm.category, bt.environment
            ORDER BY bcm.created_at DESC
        ) as run_rank
    FROM benchmark_category_metrics bcm
    INNER JOIN benchmark_transactions bt ON bcm.benchmark_run_id = bt.id
)
SELECT 
    current.id,
    current.benchmark_run_id,
    current.model_version,
    current.category,
    current.total,
    current.detected,
    current.detection_rate as current_rate,
    previous.detection_rate as previous_rate,
    current.delta_from_previous,
    current.created_at,
    
    -- Regression severity classification
    CASE 
        WHEN current.delta_from_previous IS NULL THEN 'baseline'
        WHEN current.delta_from_previous < -0.1 THEN 'severe_regression'
        WHEN current.delta_from_previous < -0.05 THEN 'moderate_regression'
        WHEN current.delta_from_previous < 0 THEN 'minor_regression'
        WHEN current.delta_from_previous = 0 THEN 'stable'
        WHEN current.delta_from_previous > 0 THEN 'improvement'
    END as regression_status
    
FROM ranked_metrics current
LEFT JOIN ranked_metrics previous 
    ON current.model_version = previous.model_version
    AND current.category = previous.category
    AND current.environment = previous.environment
    AND previous.run_rank = 2
WHERE current.run_rank = 1;

COMMENT ON VIEW v_category_regression_tracking IS 
    'Category-level regression detection with severity classification';

-- ============================================================================
-- 6. UPDATE UPSERT FUNCTION TO HANDLE ADVANCED METRICS
-- ============================================================================

-- Update the existing upsert function to also handle category metrics
CREATE OR REPLACE FUNCTION upsert_benchmark_result_with_categories(
    p_transaction_id UUID,
    p_model_version TEXT,
    p_dataset_version TEXT,
    p_prompt_version TEXT,
    p_environment TEXT,
    p_metrics JSONB,
    p_category_metrics JSONB DEFAULT NULL,
    p_snapshot_version INT DEFAULT 1
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_snapshot_id UUID;
    v_category RECORD;
BEGIN
    -- First, ensure transaction exists (backward compatible with old function)
    -- This is handled by calling code
    
    -- Then, upsert snapshot
    INSERT INTO benchmark_snapshots (
        model_version,
        dataset_version,
        prompt_version,
        environment,
        snapshot_version,
        metrics,
        is_current,
        created_at
    ) VALUES (
        p_model_version,
        p_dataset_version,
        p_prompt_version,
        p_environment,
        p_snapshot_version,
        p_metrics,
        TRUE,
        NOW()
    )
    ON CONFLICT (model_version, dataset_version, prompt_version, environment, snapshot_version)
    DO UPDATE SET
        metrics = EXCLUDED.metrics,
        is_current = TRUE,
        created_at = NOW()
    RETURNING id INTO v_snapshot_id;
    
    -- Mark other versions as not current
    UPDATE benchmark_snapshots
    SET is_current = FALSE
    WHERE model_version = p_model_version
      AND dataset_version = p_dataset_version
      AND prompt_version = p_prompt_version
      AND environment = p_environment
      AND snapshot_version != p_snapshot_version;
    
    -- Insert category metrics if provided
    IF p_category_metrics IS NOT NULL THEN
        FOR v_category IN 
            SELECT * FROM jsonb_each(p_category_metrics)
        LOOP
            INSERT INTO benchmark_category_metrics (
                benchmark_run_id,
                category,
                total,
                detected,
                detection_rate,
                delta_from_previous
            ) VALUES (
                p_transaction_id,
                v_category.key,
                (v_category.value->>'total')::INT,
                (v_category.value->>'detected')::INT,
                (v_category.value->>'detection_rate')::FLOAT,
                calculate_category_delta(
                    p_model_version,
                    v_category.key,
                    (v_category.value->>'detection_rate')::FLOAT,
                    p_environment
                )
            );
        END LOOP;
    END IF;
    
    RETURN v_snapshot_id;
END;
$$;

COMMENT ON FUNCTION upsert_benchmark_result_with_categories IS 
    'Enhanced upsert that also handles category-level metrics with regression tracking';

-- ============================================================================
-- 7. GRANT PERMISSIONS (Adjust as needed for your RLS setup)
-- ============================================================================

-- Grant permissions to service role (adjust role name as needed)
-- GRANT ALL ON benchmark_category_metrics TO service_role;
-- GRANT EXECUTE ON FUNCTION calculate_category_delta TO service_role;
-- GRANT EXECUTE ON FUNCTION upsert_benchmark_result_with_categories TO service_role;

-- ============================================================================
-- 8. VERIFICATION QUERIES
-- ============================================================================

-- Verify table creation
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'benchmark_category_metrics'
    ) THEN
        RAISE NOTICE '✅ Table benchmark_category_metrics created successfully';
    ELSE
        RAISE EXCEPTION '❌ Failed to create benchmark_category_metrics table';
    END IF;
END $$;

-- Verify indexes
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'benchmark_category_metrics' 
        AND indexname = 'idx_category_metrics_benchmark_run'
    ) THEN
        RAISE NOTICE '✅ Indexes created successfully';
    END IF;
END $$;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Summary of changes:
-- ✅ Added benchmark_category_metrics table for per-category tracking
-- ✅ Added indexes for performance
-- ✅ Added helper function for regression calculation
-- ✅ Added views for advanced metrics analysis
-- ✅ Added enhanced upsert function
-- ✅ Maintained 100% backward compatibility
-- ✅ All existing queries will continue to work
-- ✅ New metrics are optional and null-safe

SELECT 'Migration completed successfully!' as status;
