-- Safe Migration: Add issue status tracking (checks if already exists)
-- Date: 2026-02-17

-- Add status column only if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='issues' AND column_name='status'
    ) THEN
        ALTER TABLE issues
        ADD COLUMN status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'follow_up', 'resolved', 'ignored'));
    END IF;
END $$;

-- Add tracking fields only if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='issues' AND column_name='status_updated_at'
    ) THEN
        ALTER TABLE issues ADD COLUMN status_updated_at TIMESTAMPTZ DEFAULT NOW();
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='issues' AND column_name='status_updated_by'
    ) THEN
        ALTER TABLE issues ADD COLUMN status_updated_by UUID REFERENCES user_profiles(user_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='issues' AND column_name='notes'
    ) THEN
        ALTER TABLE issues ADD COLUMN notes TEXT;
    END IF;
END $$;

-- Create indexes only if they don't exist
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);
CREATE INDEX IF NOT EXISTS idx_issues_status_updated_at ON issues(status_updated_at DESC);

-- Create or replace the trigger function
CREATE OR REPLACE FUNCTION update_issue_status_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        NEW.status_updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if exists, then create it
DROP TRIGGER IF EXISTS update_issue_status_timestamp_trigger ON issues;
CREATE TRIGGER update_issue_status_timestamp_trigger
    BEFORE UPDATE ON issues
    FOR EACH ROW EXECUTE FUNCTION update_issue_status_timestamp();

-- Create RLS policy only if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'issues'
        AND policyname = 'Users can update status of their own issues'
    ) THEN
        CREATE POLICY "Users can update status of their own issues"
            ON issues FOR UPDATE
            USING (analysis_id IN (
                SELECT analysis_id FROM analyses
                WHERE user_id IN (SELECT user_id FROM user_profiles WHERE firebase_uid = auth.uid()::text)
            ))
            WITH CHECK (analysis_id IN (
                SELECT analysis_id FROM analyses
                WHERE user_id IN (SELECT user_id FROM user_profiles WHERE firebase_uid = auth.uid()::text)
            ));
    END IF;
END $$;

-- Create or replace the statistics view
CREATE OR REPLACE VIEW issue_statistics AS
SELECT
    a.user_id,
    a.analysis_id,
    COUNT(*) FILTER (WHERE i.status = 'open') as open_count,
    COUNT(*) FILTER (WHERE i.status = 'follow_up') as follow_up_count,
    COUNT(*) FILTER (WHERE i.status = 'resolved') as resolved_count,
    COUNT(*) FILTER (WHERE i.status = 'ignored') as ignored_count,
    SUM(i.max_savings) FILTER (WHERE i.status = 'open') as open_potential_savings,
    SUM(i.max_savings) FILTER (WHERE i.status = 'follow_up') as follow_up_potential_savings,
    SUM(i.max_savings) FILTER (WHERE i.status = 'resolved') as resolved_savings
FROM analyses a
LEFT JOIN issues i ON a.analysis_id = i.analysis_id
GROUP BY a.user_id, a.analysis_id;

-- Grant permissions
GRANT SELECT ON issue_statistics TO service_role;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration completed successfully!';
    RAISE NOTICE 'Issue status tracking is now enabled.';
END $$;
