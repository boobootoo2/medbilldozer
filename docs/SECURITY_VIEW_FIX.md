# Security Fix: View SECURITY DEFINER → SECURITY INVOKER

## Issue

Supabase security scan detected views defined with `SECURITY DEFINER` property:
- `v_advanced_benchmark_metrics`
- `v_category_regression_tracking`

### Risk

Views with `SECURITY DEFINER` execute with the privileges of the view's creator rather than the querying user, potentially bypassing Row Level Security (RLS) policies.

## Solution

Recreate views with `SECURITY INVOKER` property to enforce proper RLS and use querying user's permissions.

## How to Apply

### Option 1: Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Click **New Query**
4. Copy the contents of `sql/fix_view_security.sql`
5. Paste into the query editor
6. Click **Run** (or press Cmd/Ctrl + Enter)
7. Verify success message: "Views recreated with SECURITY INVOKER"

### Option 2: Command Line (psql)

```bash
# Connect to your Supabase database
psql postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres

# Run the migration
\i sql/fix_view_security.sql

# Verify
\d+ v_advanced_benchmark_metrics
\d+ v_category_regression_tracking
```

## Verification

After applying the fix, verify the security properties:

```sql
-- Check view options
SELECT 
    schemaname,
    viewname,
    viewowner,
    definition
FROM pg_views
WHERE viewname IN ('v_advanced_benchmark_metrics', 'v_category_regression_tracking');

-- Both views should now show security_invoker = true in their definition
```

## Impact Assessment

### ✅ Safe Changes

- **No breaking changes**: Views maintain same columns and data
- **Query compatibility**: All existing queries continue to work
- **Performance**: No performance impact
- **RLS enforcement**: Now properly enforces Row Level Security

### 📋 Post-Migration Checklist

- [ ] Run migration in Supabase SQL Editor
- [ ] Verify views created successfully
- [ ] Test dashboard still loads benchmark data
- [ ] Confirm no permission errors in application logs
- [ ] Re-run Supabase security scan to verify fix

## Background

### What is SECURITY DEFINER?

In PostgreSQL, views can be defined with two security models:

1. **SECURITY DEFINER** (default in older PostgreSQL)
   - View executes with **creator's privileges**
   - Can bypass RLS policies
   - Security risk if view creator has elevated permissions

2. **SECURITY INVOKER** (recommended)
   - View executes with **querying user's privileges**
   - Enforces RLS policies properly
   - More secure for multi-tenant applications

### Why This Matters

Supabase uses RLS policies to control data access. Views with `SECURITY DEFINER` can inadvertently expose data that should be protected by RLS, creating a security vulnerability.

## Files Changed

- **sql/fix_view_security.sql** - Migration script to fix views
- **docs/SECURITY_VIEW_FIX.md** - This documentation

## Related

- Original view creation: `sql/migration_advanced_metrics.sql`
- Benchmark data access: `scripts/benchmark_data_access.py`
- Dashboard: `pages/production_stability.py`

## References

- [PostgreSQL Views Documentation](https://www.postgresql.org/docs/current/sql-createview.html)
- [Supabase Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [PostgreSQL Security Best Practices](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)

---

**Status**: Ready to apply  
**Risk Level**: Low (no breaking changes)  
**Estimated Time**: < 1 minute  
**Date Created**: February 11, 2026
