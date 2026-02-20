-- Migration 002: Add Document Action Tracking
-- Date: 2026-02-20
-- Purpose: Add action tracking columns to documents table for workflow management

-- ============================================================================
-- ADD ACTION TRACKING COLUMNS
-- ============================================================================

-- Add action status column with constraint
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='documents' AND column_name='action'
    ) THEN
        ALTER TABLE documents
        ADD COLUMN action TEXT CHECK (action IN ('ignored', 'followup', 'resolved'));
    END IF;
END $$;

-- Add action notes column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='documents' AND column_name='action_notes'
    ) THEN
        ALTER TABLE documents ADD COLUMN action_notes TEXT;
    END IF;
END $$;

-- Add action date column (automatically set by trigger)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='documents' AND column_name='action_date'
    ) THEN
        ALTER TABLE documents ADD COLUMN action_date TIMESTAMPTZ;
    END IF;
END $$;

-- Add action updated by column (foreign key to user_profiles)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='documents' AND column_name='action_updated_by'
    ) THEN
        ALTER TABLE documents
        ADD COLUMN action_updated_by UUID REFERENCES user_profiles(user_id);
    END IF;
END $$;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Index for filtering by action status (partial index for non-NULL values)
CREATE INDEX IF NOT EXISTS idx_documents_action
    ON documents(action) WHERE action IS NOT NULL;

-- Index for sorting by action date
CREATE INDEX IF NOT EXISTS idx_documents_action_date
    ON documents(action_date DESC);

-- GIN index for JSONB profile_id queries
CREATE INDEX IF NOT EXISTS idx_documents_metadata_profile_id
    ON documents USING GIN ((metadata->'profile_id'));

-- ============================================================================
-- TRIGGER TO AUTO-UPDATE ACTION_DATE
-- ============================================================================

-- Function to automatically set action_date when action is updated
CREATE OR REPLACE FUNCTION update_document_action_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    -- If action changed and new action is not null, set action_date to now
    IF OLD.action IS DISTINCT FROM NEW.action AND NEW.action IS NOT NULL THEN
        NEW.action_date = NOW();
    END IF;

    -- If action is cleared (set to null), also clear action_date
    IF NEW.action IS NULL THEN
        NEW.action_date = NULL;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists and recreate
DROP TRIGGER IF EXISTS update_document_action_timestamp_trigger ON documents;

CREATE TRIGGER update_document_action_timestamp_trigger
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_document_action_timestamp();

-- ============================================================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================================================

-- Policy for updating action fields (users can update actions on their own documents)
DROP POLICY IF EXISTS "Users can update actions on their own documents" ON documents;

CREATE POLICY "Users can update actions on their own documents"
    ON documents FOR UPDATE
    USING (user_id IN (
        SELECT user_id FROM user_profiles WHERE firebase_uid = auth.uid()::text
    ))
    WITH CHECK (user_id IN (
        SELECT user_id FROM user_profiles WHERE firebase_uid = auth.uid()::text
    ));

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Grant necessary permissions to service role
GRANT SELECT, INSERT, UPDATE ON documents TO service_role;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify columns were added (uncomment to run manually)
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'documents'
-- AND column_name IN ('action', 'action_notes', 'action_date', 'action_updated_by')
-- ORDER BY column_name;

-- Verify indexes were created
-- SELECT indexname, indexdef
-- FROM pg_indexes
-- WHERE tablename = 'documents'
-- AND indexname LIKE 'idx_documents_action%'
-- ORDER BY indexname;
