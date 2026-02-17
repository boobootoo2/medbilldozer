-- Quick verification: Check what columns currently exist in user_profiles table
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'user_profiles'
ORDER BY ordinal_position;

-- Show sample of current data (if any)
SELECT * FROM user_profiles LIMIT 5;
