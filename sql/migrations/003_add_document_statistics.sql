-- Migration 003: Add Document Action Statistics View
-- Date: 2026-02-20
-- Purpose: Create materialized view for efficient document action statistics

-- ============================================================================
-- DOCUMENT ACTION STATISTICS VIEW
-- ============================================================================

-- Create view for aggregated document action statistics
-- This view provides quick counts and totals for dashboard displays
CREATE OR REPLACE VIEW document_action_statistics AS
SELECT
    d.user_id,
    (d.metadata->>'profile_id') as profile_id,
    (d.metadata->>'profile_name') as profile_name,
    COUNT(*) as total_documents,
    COUNT(*) FILTER (WHERE d.action = 'followup') as followup_count,
    COUNT(*) FILTER (WHERE d.action = 'ignored') as ignored_count,
    COUNT(*) FILTER (WHERE d.action = 'resolved') as resolved_count,
    COUNT(*) FILTER (WHERE d.action IS NULL AND d.status IN ('pending', 'uploaded')) as pending_count,
    COUNT(*) FILTER (WHERE d.status = 'completed') as completed_count,

    -- Financial aggregations
    SUM(
        CAST(d.metadata->>'patient_responsibility_amount' AS NUMERIC)
    ) FILTER (WHERE d.action = 'followup') as followup_amount,

    SUM(
        CAST(d.metadata->>'patient_responsibility_amount' AS NUMERIC)
    ) FILTER (WHERE d.action = 'resolved') as resolved_amount,

    SUM(
        CAST(d.metadata->>'patient_responsibility_amount' AS NUMERIC)
    ) as total_amount,

    -- Date tracking
    MAX(d.action_date) as last_action_date,
    MAX(d.uploaded_at) as last_upload_date

FROM documents d
GROUP BY d.user_id, (d.metadata->>'profile_id'), (d.metadata->>'profile_name');

-- Grant permissions to view
GRANT SELECT ON document_action_statistics TO service_role;

-- ============================================================================
-- DOCUMENT ISSUE COUNTS VIEW
-- ============================================================================

-- View to efficiently get issue counts per document
-- Useful for computing flagged status
CREATE OR REPLACE VIEW document_issue_counts AS
SELECT
    i.document_id,
    COUNT(*) as total_issues,
    COUNT(*) FILTER (WHERE i.confidence = 'high') as high_confidence_count,
    COUNT(*) FILTER (WHERE i.confidence = 'high' AND i.metadata->>'status' = 'open') as high_confidence_open_count,
    SUM(i.max_savings) as total_potential_savings,
    MAX(i.created_at) as latest_issue_date
FROM issues i
WHERE i.document_id IS NOT NULL
GROUP BY i.document_id;

-- Grant permissions to view
GRANT SELECT ON document_issue_counts TO service_role;

-- ============================================================================
-- ENRICHED DOCUMENTS VIEW
-- ============================================================================

-- Comprehensive view joining documents with their issue counts
-- Provides all data needed for EnrichedDocumentResponse
CREATE OR REPLACE VIEW enriched_documents AS
SELECT
    d.document_id,
    d.user_id,
    d.filename,
    d.original_filename,
    d.gcs_path,
    d.content_type,
    d.size_bytes,
    d.uploaded_at,
    d.status,
    d.document_type,
    d.extracted_text,
    d.metadata,
    d.error_message,

    -- Action tracking
    d.action,
    d.action_notes,
    d.action_date,
    d.action_updated_by,

    -- Profile metadata
    (d.metadata->>'profile_id') as profile_id,
    (d.metadata->>'profile_name') as profile_name,
    (d.metadata->>'profile_type') as profile_type,
    (d.metadata->>'provider_name') as provider_name,
    (d.metadata->>'service_date') as service_date,
    CAST(d.metadata->>'patient_responsibility_amount' AS NUMERIC) as patient_responsibility_amount,

    -- Issue counts (computed)
    COALESCE(ic.total_issues, 0) as total_issues_count,
    COALESCE(ic.high_confidence_count, 0) as high_confidence_issues_count,
    COALESCE(ic.high_confidence_open_count, 0) as high_confidence_open_issues,
    COALESCE(ic.total_potential_savings, 0) as total_potential_savings,

    -- Flagged status (computed from high confidence open issues)
    CASE
        WHEN COALESCE(ic.high_confidence_open_count, 0) > 0 THEN true
        ELSE false
    END as flagged

FROM documents d
LEFT JOIN document_issue_counts ic ON d.document_id = ic.document_id;

-- Grant permissions to view
GRANT SELECT ON enriched_documents TO service_role;

-- ============================================================================
-- ROW LEVEL SECURITY FOR VIEWS
-- ============================================================================

-- Enable RLS on views (inherits from base tables)
ALTER VIEW document_action_statistics SET (security_barrier = true);
ALTER VIEW document_issue_counts SET (security_barrier = true);
ALTER VIEW enriched_documents SET (security_barrier = true);

-- ============================================================================
-- INDEXES FOR VIEW PERFORMANCE
-- ============================================================================

-- Index on metadata->profile_id for fast profile filtering
-- (Already created in migration 002, including here for completeness)
CREATE INDEX IF NOT EXISTS idx_documents_metadata_profile_id
    ON documents USING GIN ((metadata->'profile_id'));

-- Index on metadata->patient_responsibility_amount for aggregations
CREATE INDEX IF NOT EXISTS idx_documents_metadata_amount
    ON documents USING GIN ((metadata->'patient_responsibility_amount'));

-- Index on issues.document_id for join performance
CREATE INDEX IF NOT EXISTS idx_issues_document_id_confidence
    ON issues(document_id, confidence);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify views were created (uncomment to run manually)
-- SELECT viewname, definition
-- FROM pg_views
-- WHERE viewname IN ('document_action_statistics', 'document_issue_counts', 'enriched_documents')
-- ORDER BY viewname;

-- Test statistics view
-- SELECT * FROM document_action_statistics LIMIT 5;

-- Test issue counts view
-- SELECT * FROM document_issue_counts LIMIT 5;

-- Test enriched documents view
-- SELECT document_id, filename, flagged, high_confidence_open_issues
-- FROM enriched_documents
-- LIMIT 5;
