-- ============================================================================
-- FIX VIEW SECURITY: Change SECURITY DEFINER to SECURITY INVOKER
-- ============================================================================
-- 
-- Issue: Supabase security scan detected views with SECURITY DEFINER property
-- Risk: Views execute with creator's privileges, potentially bypassing RLS
-- Solution: Recreate views with SECURITY INVOKER to use querying user's permissions
--
-- Date: February 11, 2026
-- ============================================================================

-- Drop and recreate v_advanced_benchmark_metrics with SECURITY INVOKER
DROP VIEW IF EXISTS v_advanced_benchmark_metrics;

CREATE OR REPLACE VIEW v_advanced_benchmark_metrics 
WITH (security_invoker = true)
AS
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
    'Unified view of standard and advanced benchmark metrics with null-safe extraction. Uses SECURITY INVOKER for proper RLS enforcement.';

-- Drop and recreate v_category_regression_tracking with SECURITY INVOKER
DROP VIEW IF EXISTS v_category_regression_tracking;

CREATE OR REPLACE VIEW v_category_regression_tracking
WITH (security_invoker = true)
AS
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
    'Tracks performance changes across benchmark runs for regression detection. Uses SECURITY INVOKER for proper RLS enforcement.';

-- Grant appropriate permissions
GRANT SELECT ON v_advanced_benchmark_metrics TO authenticated;
GRANT SELECT ON v_advanced_benchmark_metrics TO anon;

GRANT SELECT ON v_category_regression_tracking TO authenticated;
GRANT SELECT ON v_category_regression_tracking TO anon;

-- Verification query
DO $$
BEGIN
    RAISE NOTICE 'Views recreated with SECURITY INVOKER';
    RAISE NOTICE 'Security properties:';
    RAISE NOTICE '  v_advanced_benchmark_metrics: security_invoker = true';
    RAISE NOTICE '  v_category_regression_tracking: security_invoker = true';
END $$;
