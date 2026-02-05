# Workflow Permissions Fix

## 🎯 Issue: 403 Permission Denied When Pushing

### Error
```
remote: Permission to boobootoo2/medbilldozer.git denied to github-actions[bot].
fatal: unable to access 'https://github.com/boobootoo2/medbilldozer/': The requested URL returned error: 403
Error: Process completed with exit code 128.
```

### Root Cause
GitHub Actions workflow doesn't have permission to push commits back to the repository.

## ✅ Solution (2 Steps)

### Step 1: Update Workflow File ✅ DONE

Added permissions to `.github/workflows/run_benchmarks.yml`:

```yaml
jobs:
  benchmark:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # Allow workflow to push commits
    
    steps:
      - uses: actions/checkout@v3
        with:
          token: ${{ secrets.GITHUB_TOKEN }}  # Use built-in token
```

### Step 2: Enable Workflow Permissions in Repository Settings

⚠️ **You need to do this manually**:

1. **Go to Repository Settings**
   - Navigate to: <https://github.com/boobootoo2/medbilldozer/settings/actions>
   - Or: Repository → Settings → Actions → General

2. **Find "Workflow permissions"** (scroll down)

3. **Select**: ✅ **"Read and write permissions"**
   - Instead of: ❌ "Read repository contents and packages permissions"

4. **Check**: ✅ **"Allow GitHub Actions to create and approve pull requests"**

5. **Click**: **"Save"**

## 🔍 What This Does

### permissions: contents: write
Grants the workflow permission to:
- Push commits back to the repository
- Create/update files in benchmarks/results/
- Commit with message "📊 Update benchmark results"

### token: ${{ secrets.GITHUB_TOKEN }}
Uses the built-in GitHub Actions token for authentication:
- Automatically provided by GitHub
- No need to create a Personal Access Token
- Scoped to this repository only
- Expires after workflow completes

## 📊 Expected Behavior After Fix

### Current Behavior ❌
```
1. Workflow runs benchmarks ✅
2. Generates results JSON ✅
3. Commits locally ✅
4. Tries to push → 403 ERROR ❌
```

### After Fix ✅
```
1. Workflow runs benchmarks ✅
2. Generates results JSON ✅
3. Commits locally ✅
4. Pushes to develop branch ✅
5. Dashboard auto-updates ✅
```

## 🎯 Verification

After enabling workflow permissions:

1. **Trigger workflow manually**:
   - Go to: Actions → Run Benchmarks → Run workflow

2. **Watch for success**:
   - Benchmarks run (3 providers)
   - Results committed
   - **Push succeeds** ✅

3. **Check for new commit**:
   - Message: "📊 Update benchmark results"
   - Files: benchmarks/results/*.json

4. **Pull results locally**:
   ```bash
   git pull origin develop
   ls -lh benchmarks/results/
   ```

## 🔒 Security Notes

### Safe: Using GITHUB_TOKEN
- ✅ Automatically scoped to repository
- ✅ Expires after workflow
- ✅ Can't access other repositories
- ✅ Limited to workflow's permissions

### Alternative: Personal Access Token (Not Needed)
You could create a PAT, but it's unnecessary:
- ❌ More complex setup
- ❌ Requires manual token creation
- ❌ Needs to be stored as secret
- ❌ Broader permissions than needed

### Recommendation
✅ Use built-in `GITHUB_TOKEN` (what we're doing)

## 📝 Alternative: Disable Auto-Push

If you prefer to NOT auto-commit results:

### Option 1: Upload as Artifact (No Push)
```yaml
- name: Upload benchmark results
  uses: actions/upload-artifact@v3
  with:
    name: benchmark-results
    path: benchmarks/results/
```

Then manually download and commit.

### Option 2: Create Pull Request Instead
```yaml
- name: Create Pull Request
  uses: peter-evans/create-pull-request@v5
  with:
    commit-message: "📊 Update benchmark results"
    branch: benchmark-updates
    title: "Automated Benchmark Results"
```

Requires approval before merging.

### Option 3: Keep Current (Recommended) ✅
Auto-commit is best for benchmarks:
- ✅ Automatic updates
- ✅ No manual intervention
- ✅ Dashboard stays current
- ✅ Git history tracks changes

## 🐛 Troubleshooting

### Still getting 403 after fix?

**Check**: Repository settings → Actions → Workflow permissions
- Must be: "Read and write permissions"
- Not: "Read repository contents only"

### Workflow permissions option not visible?

**Possible causes**:
1. Organization-level policy overrides
2. Enterprise account restrictions
3. Need repository admin access

**Solution**: 
- Contact repository admin
- Or use Personal Access Token as secret

### Different error: "refusing to allow a GitHub App to create or update workflow"?

**Cause**: Trying to modify `.github/workflows/` files  
**Solution**: Exclude workflow files from commit:
```yaml
git add benchmarks/results/
# Don't add .github/workflows/
```

## 🎓 Understanding GitHub Permissions

### Repository Permissions Levels
```
Read-only:
- ✅ Checkout code
- ✅ Read files
- ❌ Push commits
- ❌ Create branches

Read and write:
- ✅ Checkout code
- ✅ Read files
- ✅ Push commits ← We need this!
- ✅ Create branches
```

### Workflow-Specific Permissions
```yaml
permissions:
  contents: write        # Push/commit files
  pull-requests: write   # Create/update PRs
  issues: write          # Create/comment on issues
  checks: write          # Update check runs
```

We only need `contents: write` for benchmark commits.

## ✅ Checklist

- [x] Update workflow file (add permissions)
- [ ] Enable "Read and write permissions" in repo settings ← **YOU DO THIS**
- [ ] Test workflow manually
- [ ] Verify commit is pushed
- [ ] Pull results locally

## 📚 Documentation

- GitHub Docs: [Workflow Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)
- GitHub Actions: [GITHUB_TOKEN](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)

---

**Status**: Workflow file updated ✅  
**Action Required**: Enable repository workflow permissions (see Step 2)  
**Expected Result**: Workflow will push commits successfully 🚀
