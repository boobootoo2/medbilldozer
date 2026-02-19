-- MedBillDozer Challenge Schema
-- Tables for challenge scenarios and player progress tracking

-- Challenge Scenarios Table
CREATE TABLE IF NOT EXISTS challenge_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('billing_only', 'clinical_validation', 'combined', 'clean_case', 'malpractice')),
    difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard', 'expert')),
    patient_name TEXT NOT NULL,
    patient_avatar TEXT,
    patient_profile JSONB NOT NULL,
    clinical_images JSONB,
    patient_story TEXT,
    provider_bill JSONB NOT NULL,
    insurance_eob JSONB NOT NULL,
    expected_issues JSONB NOT NULL,
    has_billing_errors BOOLEAN DEFAULT FALSE,
    has_clinical_errors BOOLEAN DEFAULT FALSE,
    malpractice_data JSONB,
    max_score INTEGER NOT NULL DEFAULT 1000,
    time_bonus_threshold INTEGER DEFAULT 300,
    tags TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Player Progress Table
CREATE TABLE IF NOT EXISTS player_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    score INTEGER,
    base_score INTEGER,
    accuracy_bonus INTEGER,
    speed_bonus INTEGER,
    difficulty_multiplier FLOAT,
    completion_time INTEGER,  -- seconds
    issues_found JSONB,
    issues_expected JSONB,
    accuracy FLOAT,
    achievements_earned TEXT[],
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (scenario_id) REFERENCES challenge_scenarios(scenario_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_challenge_scenarios_category ON challenge_scenarios(category);
CREATE INDEX IF NOT EXISTS idx_challenge_scenarios_difficulty ON challenge_scenarios(difficulty);
CREATE INDEX IF NOT EXISTS idx_challenge_scenarios_active ON challenge_scenarios(is_active);
CREATE INDEX IF NOT EXISTS idx_player_progress_session ON player_progress(session_id);
CREATE INDEX IF NOT EXISTS idx_player_progress_scenario ON player_progress(scenario_id);
CREATE INDEX IF NOT EXISTS idx_player_progress_completed ON player_progress(completed_at);

-- View for scenario statistics
CREATE OR REPLACE VIEW v_scenario_statistics AS
SELECT
    category,
    difficulty,
    COUNT(*) as scenario_count,
    AVG(max_score) as avg_max_score,
    SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_count
FROM challenge_scenarios
GROUP BY category, difficulty;

-- View for player statistics
CREATE OR REPLACE VIEW v_player_statistics AS
SELECT
    session_id,
    COUNT(*) as scenarios_completed,
    AVG(score) as avg_score,
    AVG(accuracy) as avg_accuracy,
    SUM(completion_time) as total_time,
    COUNT(DISTINCT unnest(achievements_earned)) as unique_achievements
FROM player_progress
GROUP BY session_id;

-- View for top scores (session leaderboard)
CREATE OR REPLACE VIEW v_top_scores AS
SELECT
    pp.session_id,
    pp.score,
    pp.accuracy,
    pp.completion_time,
    cs.scenario_id,
    cs.category,
    cs.difficulty,
    pp.completed_at
FROM player_progress pp
JOIN challenge_scenarios cs ON pp.scenario_id = cs.scenario_id
ORDER BY pp.score DESC, pp.accuracy DESC, pp.completion_time ASC
LIMIT 100;

-- Function to update timestamp on row update
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER update_challenge_scenarios_updated_at
    BEFORE UPDATE ON challenge_scenarios
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- RPC function to upsert challenge scenario
CREATE OR REPLACE FUNCTION upsert_challenge_scenario(
    p_scenario_id TEXT,
    p_category TEXT,
    p_difficulty TEXT,
    p_patient_name TEXT,
    p_patient_avatar TEXT,
    p_patient_profile JSONB,
    p_clinical_images JSONB,
    p_patient_story TEXT,
    p_provider_bill JSONB,
    p_insurance_eob JSONB,
    p_expected_issues JSONB,
    p_has_billing_errors BOOLEAN,
    p_has_clinical_errors BOOLEAN,
    p_malpractice_data JSONB,
    p_max_score INTEGER,
    p_time_bonus_threshold INTEGER,
    p_tags TEXT[]
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO challenge_scenarios (
        scenario_id, category, difficulty, patient_name, patient_avatar,
        patient_profile, clinical_images, patient_story, provider_bill,
        insurance_eob, expected_issues, has_billing_errors, has_clinical_errors,
        malpractice_data, max_score, time_bonus_threshold, tags
    ) VALUES (
        p_scenario_id, p_category, p_difficulty, p_patient_name, p_patient_avatar,
        p_patient_profile, p_clinical_images, p_patient_story, p_provider_bill,
        p_insurance_eob, p_expected_issues, p_has_billing_errors, p_has_clinical_errors,
        p_malpractice_data, p_max_score, p_time_bonus_threshold, p_tags
    )
    ON CONFLICT (scenario_id) DO UPDATE SET
        category = EXCLUDED.category,
        difficulty = EXCLUDED.difficulty,
        patient_name = EXCLUDED.patient_name,
        patient_avatar = EXCLUDED.patient_avatar,
        patient_profile = EXCLUDED.patient_profile,
        clinical_images = EXCLUDED.clinical_images,
        patient_story = EXCLUDED.patient_story,
        provider_bill = EXCLUDED.provider_bill,
        insurance_eob = EXCLUDED.insurance_eob,
        expected_issues = EXCLUDED.expected_issues,
        has_billing_errors = EXCLUDED.has_billing_errors,
        has_clinical_errors = EXCLUDED.has_clinical_errors,
        malpractice_data = EXCLUDED.malpractice_data,
        max_score = EXCLUDED.max_score,
        time_bonus_threshold = EXCLUDED.time_bonus_threshold,
        tags = EXCLUDED.tags
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- RPC function to record player progress
CREATE OR REPLACE FUNCTION record_player_progress(
    p_session_id TEXT,
    p_scenario_id TEXT,
    p_score INTEGER,
    p_base_score INTEGER,
    p_accuracy_bonus INTEGER,
    p_speed_bonus INTEGER,
    p_difficulty_multiplier FLOAT,
    p_completion_time INTEGER,
    p_issues_found JSONB,
    p_issues_expected JSONB,
    p_accuracy FLOAT,
    p_achievements_earned TEXT[]
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO player_progress (
        session_id, scenario_id, score, base_score, accuracy_bonus, speed_bonus,
        difficulty_multiplier, completion_time, issues_found, issues_expected,
        accuracy, achievements_earned
    ) VALUES (
        p_session_id, p_scenario_id, p_score, p_base_score, p_accuracy_bonus, p_speed_bonus,
        p_difficulty_multiplier, p_completion_time, p_issues_found, p_issues_expected,
        p_accuracy, p_achievements_earned
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your security model)
-- GRANT SELECT ON challenge_scenarios TO anon;
-- GRANT SELECT, INSERT ON player_progress TO anon;
-- GRANT SELECT ON v_scenario_statistics TO anon;
-- GRANT SELECT ON v_player_statistics TO anon;
-- GRANT SELECT ON v_top_scores TO anon;
