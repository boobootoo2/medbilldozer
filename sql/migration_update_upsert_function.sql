-- Migration: Update upsert_benchmark_result to handle cost savings metrics
-- Date: 2026-02-05
-- Purpose: Add cost savings parameters and columns to the upsert function

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
    v_total_potential_savings NUMERIC;
    v_total_missed_savings NUMERIC;
    v_avg_savings_per_patient NUMERIC;
    v_savings_capture_rate NUMERIC;
BEGIN
    -- Extract common metrics for denormalization
    v_precision_val := (p_metrics->>'precision')::NUMERIC;
    v_recall := (p_metrics->>'recall')::NUMERIC;
    v_f1 := (p_metrics->>'f1')::NUMERIC;
    v_latency := (p_metrics->>'latency_ms')::NUMERIC;
    v_cost := (p_metrics->>'analysis_cost')::NUMERIC;
    
    -- Extract cost savings metrics (if available)
    v_total_potential_savings := (p_metrics->>'total_potential_savings')::NUMERIC;
    v_total_missed_savings := (p_metrics->>'total_missed_savings')::NUMERIC;
    v_avg_savings_per_patient := (p_metrics->>'avg_savings_per_patient')::NUMERIC;
    v_savings_capture_rate := (p_metrics->>'savings_capture_rate')::NUMERIC;
    
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
        total_potential_savings,
        total_missed_savings,
        avg_savings_per_patient,
        savings_capture_rate,
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
        v_total_potential_savings,
        v_total_missed_savings,
        v_avg_savings_per_patient,
        v_savings_capture_rate,
        TRUE
    );
    
    RETURN v_transaction_id;
END;
$$ LANGUAGE plpgsql;

-- Verify function was updated
SELECT 
    proname as function_name,
    pronargs as num_args,
    pg_get_functiondef(oid) as definition
FROM pg_proc
WHERE proname = 'upsert_benchmark_result'
LIMIT 1;
