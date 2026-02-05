-- Migration: Add cost savings metrics to benchmark_snapshots
-- Date: 2026-02-05
-- Purpose: Track ROI and cost savings potential from error detection

-- Add cost savings columns
ALTER TABLE benchmark_snapshots
    ADD COLUMN IF NOT EXISTS total_potential_savings NUMERIC(10, 2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS total_missed_savings NUMERIC(10, 2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS avg_savings_per_patient NUMERIC(10, 2) DEFAULT 0,
    ADD COLUMN IF NOT EXISTS savings_capture_rate NUMERIC(5, 2) DEFAULT 0;

-- Add column comments
COMMENT ON COLUMN benchmark_snapshots.total_potential_savings IS 
    'Total dollar amount saved from detected billing errors';
COMMENT ON COLUMN benchmark_snapshots.total_missed_savings IS 
    'Total dollar amount from undetected billing errors';
COMMENT ON COLUMN benchmark_snapshots.avg_savings_per_patient IS 
    'Average savings per patient from detected errors';
COMMENT ON COLUMN benchmark_snapshots.savings_capture_rate IS 
    'Percentage of potential savings captured (ROI metric)';

-- Add index for cost savings queries
CREATE INDEX IF NOT EXISTS idx_benchmark_snapshots_savings 
    ON benchmark_snapshots(total_potential_savings DESC NULLS LAST);

-- Verify columns were added
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'benchmark_snapshots'
  AND column_name IN (
      'total_potential_savings',
      'total_missed_savings', 
      'avg_savings_per_patient',
      'savings_capture_rate'
  )
ORDER BY column_name;
