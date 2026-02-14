-- ============================================================================
-- Temporarily Disable RLS for Data Sync
-- ============================================================================
-- Run this in BETA Supabase BEFORE syncing data
-- Then run enable_rls_beta.sql AFTER sync is complete
-- ============================================================================

-- Disable RLS on both tables
ALTER TABLE public.benchmark_transactions DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.benchmark_snapshots DISABLE ROW LEVEL SECURITY;

-- Verify RLS is disabled
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN ('benchmark_transactions', 'benchmark_snapshots');

-- Show message
DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'RLS TEMPORARILY DISABLED';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Tables: benchmark_transactions, benchmark_snapshots';
    RAISE NOTICE '';
    RAISE NOTICE 'IMPORTANT: Re-enable RLS after sync!';
    RAISE NOTICE 'Run: enable_rls_beta.sql';
    RAISE NOTICE '=================================================';
END $$;
