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
SELECT 
    current.run_id,
    current.model_version,
    current.category,
    current.created_at as current_run_date,
    
    -- Current metrics
    current.precision as current_precision,
    current.recall as current_recall,
    current.f1 as current_f1,
    current.issue_count as current_issue_count,
    
    -- Previous metrics
    previous.run_id as previous_run_id,
    previous.created_at as previous_run_date,
    previous.precision as previous_precision,
    previous.recall as previous_recall,
    previous.f1 as previous_f1,
    previous.issue_count as previous_issue_count,
    
    -- Deltas
    (current.precision - COALESCE(previous.precision, 0)) as precision_delta,
    (current.recall - COALESCE(previous.recall, 0)) as recall_delta,
    (current.f1 - COALESCE(previous.f1, 0)) as f1_delta,
    (current.issue_count - COALESCE(previous.issue_count, 0)) as issue_count_delta,
    
    -- Regression severity classification
    CASE
        WHEN (current.f1 - COALESCE(previous.f1, 0)) < -0.10 THEN 'CRITICAL'
        WHEN (current.f1 - COALESCE(previous.f1, 0)) < -0.05 THEN 'WARNING'
        WHEN (current.f1 - COALESCE(previous.f1, 0)) > 0.05 THEN 'IMPROVEMENT'
        ELSE 'STABLE'
    END as regression_severity
    
FROM benchmark_category_metrics current
LEFT JOIN LATERAL (
    SELECT *
    FROM benchmark_category_metrics previous_run
    WHERE previous_run.model_version = current.model_version
      AND previous_run.category = current.category
      AND previous_run.created_at < current.created_at
    ORDER BY previous_run.created_at DESC
    LIMIT 1
) previous ON true
ORDER BY current.created_at DESC, current.category;

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
