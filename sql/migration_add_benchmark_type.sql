-- ============================================================================
-- Migration: Add benchmark_type column
-- ============================================================================
-- Purpose: Support different benchmark types (regular vs patient cross-document)
-- Date: 2026-02-04
-- ============================================================================

-- Add benchmark_type column to benchmark_transactions
ALTER TABLE benchmark_transactions
ADD COLUMN IF NOT EXISTS benchmark_type TEXT NOT NULL DEFAULT 'standard'
CHECK (benchmark_type IN ('standard', 'patient_cross_document'));

-- Add comment for documentation
COMMENT ON COLUMN benchmark_transactions.benchmark_type IS 
'Type of benchmark: standard (single document) or patient_cross_document (multi-document with patient context)';

-- Create index for filtering by benchmark type
CREATE INDEX IF NOT EXISTS idx_transactions_benchmark_type 
    ON benchmark_transactions(benchmark_type);

-- Composite index for common patient benchmark queries
CREATE INDEX IF NOT EXISTS idx_transactions_type_model 
    ON benchmark_transactions(benchmark_type, model_version, created_at DESC);

-- Add benchmark_type column to benchmark_snapshots
ALTER TABLE benchmark_snapshots
ADD COLUMN IF NOT EXISTS benchmark_type TEXT NOT NULL DEFAULT 'standard'
CHECK (benchmark_type IN ('standard', 'patient_cross_document'));

-- Add comment for documentation
COMMENT ON COLUMN benchmark_snapshots.benchmark_type IS 
'Type of benchmark: standard (single document) or patient_cross_document (multi-document with patient context)';

-- Create index for snapshots
CREATE INDEX IF NOT EXISTS idx_snapshots_benchmark_type 
    ON benchmark_snapshots(benchmark_type);

-- Update existing records to have 'standard' type (already default, but explicit)
UPDATE benchmark_transactions 
SET benchmark_type = 'standard' 
WHERE benchmark_type IS NULL;

UPDATE benchmark_snapshots 
SET benchmark_type = 'standard' 
WHERE benchmark_type IS NULL;

-- ============================================================================
-- Verification
-- ============================================================================

-- Show counts by benchmark type
SELECT 
    benchmark_type,
    COUNT(*) as count,
    COUNT(DISTINCT model_version) as unique_models
FROM benchmark_transactions
GROUP BY benchmark_type;

SELECT 
    benchmark_type,
    COUNT(*) as count,
    COUNT(DISTINCT model_version) as unique_models
FROM benchmark_snapshots
GROUP BY benchmark_type;

-- ============================================================================
-- Usage Examples
-- ============================================================================

-- Query patient benchmarks only
-- SELECT * FROM benchmark_transactions 
-- WHERE benchmark_type = 'patient_cross_document'
-- ORDER BY created_at DESC;

-- Query standard benchmarks only
-- SELECT * FROM benchmark_transactions 
-- WHERE benchmark_type = 'standard'
-- ORDER BY created_at DESC;

-- Compare both types for a model
-- SELECT 
--     benchmark_type,
--     AVG((metrics->>'f1')::NUMERIC) as avg_f1,
--     COUNT(*) as run_count
-- FROM benchmark_transactions
-- WHERE model_version = 'medgemma'
-- GROUP BY benchmark_type;
