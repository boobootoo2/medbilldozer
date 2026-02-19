-- Migration: Add issue status tracking for follow-up, resolved, and ignore
-- Date: 2026-02-17

-- Add status column to issues table
ALTER TABLE issues
ADD COLUMN status TEXT NOT NULL DEFAULT 'open'
CHECK (status IN ('open', 'follow_up', 'resolved', 'ignored'));

-- Add tracking fields for status changes
ALTER TABLE issues
ADD COLUMN status_updated_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN status_updated_by UUID REFERENCES user_profiles(user_id),
ADD COLUMN notes TEXT;

-- Create index on status for filtering
CREATE INDEX idx_issues_status ON issues(status);

-- Create index on status_updated_at
CREATE INDEX idx_issues_status_updated_at ON issues(status_updated_at DESC);

-- Create trigger to update status_updated_at when status changes
CREATE OR REPLACE FUNCTION update_issue_status_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        NEW.status_updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_issue_status_timestamp_trigger
    BEFORE UPDATE ON issues
    FOR EACH ROW EXECUTE FUNCTION update_issue_status_timestamp();

-- Add RLS policy for updating issue status
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

-- Create view for issue statistics by status
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

COMMENT ON VIEW issue_statistics IS 'Provides aggregate statistics on issues by status for each analysis';
