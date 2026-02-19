-- Create a PostgreSQL function to upsert user
-- This bypasses PostgREST schema cache issues

CREATE OR REPLACE FUNCTION upsert_user_profile(
    p_firebase_uid TEXT,
    p_email TEXT,
    p_display_name TEXT DEFAULT NULL,
    p_avatar_url TEXT DEFAULT NULL
)
RETURNS TABLE (
    user_id UUID,
    firebase_uid TEXT,
    email TEXT,
    display_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    INSERT INTO user_profiles (firebase_uid, email, display_name, avatar_url, last_login_at)
    VALUES (p_firebase_uid, p_email, p_display_name, p_avatar_url, NOW())
    ON CONFLICT (firebase_uid)
    DO UPDATE SET
        email = EXCLUDED.email,
        display_name = EXCLUDED.display_name,
        avatar_url = EXCLUDED.avatar_url,
        last_login_at = EXCLUDED.last_login_at,
        updated_at = NOW()
    RETURNING
        user_profiles.user_id,
        user_profiles.firebase_uid,
        user_profiles.email,
        user_profiles.display_name,
        user_profiles.avatar_url,
        user_profiles.created_at,
        user_profiles.updated_at,
        user_profiles.last_login_at,
        user_profiles.is_active,
        user_profiles.metadata;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission to service role
GRANT EXECUTE ON FUNCTION upsert_user_profile TO service_role;
