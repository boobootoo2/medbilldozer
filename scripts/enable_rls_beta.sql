-- ============================================================================
-- Re-enable RLS After Data Sync
-- ============================================================================
-- Run this in BETA Supabase AFTER syncing data
-- ============================================================================

-- Drop any existing policies
DROP POLICY IF EXISTS "Service role has full access to snapshots" ON public.benchmark_snapshots;
DROP POLICY IF EXISTS "Service role has full access to transactions" ON public.benchmark_transactions;
DROP POLICY IF EXISTS "Public can read snapshots" ON public.benchmark_snapshots;
DROP POLICY IF EXISTS "Public can read transactions" ON public.benchmark_transactions;

-- Re-enable RLS
ALTER TABLE public.benchmark_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.benchmark_snapshots ENABLE ROW LEVEL SECURITY;

-- Create service role policies (full access)
CREATE POLICY "Service role has full access to transactions" 
    ON public.benchmark_transactions
    FOR ALL 
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to snapshots" 
    ON public.benchmark_snapshots
    FOR ALL 
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Create public read-only policies
CREATE POLICY "Public can read transactions" 
    ON public.benchmark_transactions
    FOR SELECT 
    TO anon, authenticated
    USING (true);

CREATE POLICY "Public can read snapshots" 
    ON public.benchmark_snapshots
    FOR SELECT 
    TO anon, authenticated
    USING (true);

-- Verify RLS is enabled and policies exist
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN ('benchmark_transactions', 'benchmark_snapshots');

SELECT 
    schemaname,
    tablename,
    policyname,
    roles,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
    AND tablename IN ('benchmark_transactions', 'benchmark_snapshots')
ORDER BY tablename, policyname;

-- Show message
DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'RLS RE-ENABLED';
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Tables: benchmark_transactions, benchmark_snapshots';
    RAISE NOTICE 'Policies:';
    RAISE NOTICE '  - Service role: Full access';
    RAISE NOTICE '  - Public: Read-only';
    RAISE NOTICE '=================================================';
END $$;
