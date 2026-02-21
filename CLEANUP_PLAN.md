# Repository Cleanup Plan - February 21, 2026

## Summary
Found **multiple redundant documentation files** that can be safely removed or consolidated.

---

## 🗑️ Files Recommended for Deletion

### Category 1: CORS Documentation (Remove 4, Keep 1)
**KEEP:** `CORS_FIX_COMPLETE.md` (151 lines) - Most recent, comprehensive fix documentation

**REMOVE:**
- ❌ `CORS_CHANGES.md` (242 lines) - Superseded by CORS_FIX_COMPLETE.md
- ❌ `CORS_SETUP_SUMMARY.md` (276 lines) - Duplicate information
- ❌ `CORS_VERIFICATION.md` (319 lines) - Testing info included in complete doc
- ❌ `QUICK_CORS_FIX.md` (92 lines) - Quick fix superseded by complete solution

**Rationale:** All CORS issues have been resolved. CORS_FIX_COMPLETE.md contains the definitive solution with verification steps.

---

### Category 2: Deployment Status Snapshots (Outdated)
- ❌ `DEPLOYMENT_STATUS.md` (4.9K) - Outdated deployment snapshot
- ❌ `VERCEL_FIX.md` (5.6K) - Vercel issue resolved, no longer needed
- ❌ `ANALYTICS_IMPLEMENTATION_SUMMARY.md` (7.4K) - If feature is complete, move to docs/

**Rationale:** These are point-in-time status files that are now outdated.

---

### Category 3: Backup Files
- ❌ `requirements.txt.bak` - Backup of requirements.txt
- ❌ `test_medical_bill.txt` (if test data) - Move to benchmarks/inputs/

---

### Category 4: Deployment Config Files (Consolidate or Archive)
**Consider removing if env vars are now in Cloud Run:**
- ❌ `backend-env-vars.yaml` (244B)
- ❌ `cloud-run-env-update.yaml` (451B)
- ❌ `cloud-run-env.yaml` (197B)

**Consider keeping:**
- ✅ `deploy-manual.sh` (if still used)
- ✅ `setup-vercel-env.sh` (if still used)

---

### Category 5: Duplicate Documentation in docs/

#### Beta Mode (3 files → Keep 1)
**KEEP:** `docs/BETA_MODE_GUIDE.md` (410 lines) - Most comprehensive

**REMOVE:**
- ❌ `docs/BETA_MODE.md` (209 lines) - Subset of guide
- ❌ `docs/BETA_MODE_QUICKSTART.md` (120 lines) - Include in main guide

---

#### Quickstart (2 files → Keep 1)
**KEEP:** `docs/QUICK_START.md` (423 lines) - More comprehensive

**REMOVE:**
- ❌ `docs/QUICKSTART.md` (269 lines) - Duplicate

---

#### Implementation Docs (3 files → Keep 1)
**KEEP:** `docs/IMPLEMENTATION_ROADMAP.md` (836 lines) - Most comprehensive

**REMOVE:**
- ❌ `docs/IMPLEMENTATION_PROGRESS.md` (376 lines) - Outdated progress snapshot
- ❌ `docs/IMPLEMENTATION_SUMMARY.md` (345 lines) - Duplicate of roadmap

---

#### Clinical Validation (2 similar files)
**Consider merging:**
- `docs/CLINICAL_VALIDATION_QUICKSTART.md` (386 lines)
- `docs/CLINICAL_VALIDATION_REAL_IMPLEMENTATION.md` (373 lines)

If they cover the same topic, merge into one.

---

### Category 6: Old/Outdated Files in docs/
- ❌ `docs/SECURITY_VIEW_FIX.md` (if issue resolved)
- ❌ `docs/EXPONENTIAL_BACKOFF_COMPLETE.md` (if feature complete, merge into main docs)
- ❌ `docs/FULL_STACK_COMPLETE.md` (if project summary, merge into README)
- ❌ `docs/RELEASE_NOTES_v0.2.md` (if v0.3.1 is current, archive old release notes)

---

## 📊 Cleanup Impact

| Category | Files to Remove | Space Saved |
|----------|----------------|-------------|
| CORS docs | 4 | ~25KB |
| Deployment snapshots | 3 | ~18KB |
| Backups | 2 | ~7KB |
| Config files | 3 | ~1KB |
| Duplicate docs | 6+ | ~50KB |
| **Total** | **18+** | **~100KB** |

---

## ✅ Recommended Actions

### Option 1: Safe Cleanup (Recommended)
```bash
# Create archive folder
mkdir -p .archive/2026-02

# Move outdated files to archive
mv CORS_CHANGES.md CORS_SETUP_SUMMARY.md CORS_VERIFICATION.md QUICK_CORS_FIX.md .archive/2026-02/
mv DEPLOYMENT_STATUS.md VERCEL_FIX.md ANALYTICS_IMPLEMENTATION_SUMMARY.md .archive/2026-02/
mv requirements.txt.bak test_medical_bill.txt .archive/2026-02/
mv backend-env-vars.yaml cloud-run-env-update.yaml cloud-run-env.yaml .archive/2026-02/

# Move duplicate docs
mv docs/BETA_MODE.md docs/BETA_MODE_QUICKSTART.md .archive/2026-02/
mv docs/QUICKSTART.md docs/IMPLEMENTATION_PROGRESS.md docs/IMPLEMENTATION_SUMMARY.md .archive/2026-02/

# Commit
git add .archive/
git commit -m "chore: archive outdated documentation files"
```

### Option 2: Permanent Deletion
```bash
# Delete redundant CORS docs (keep CORS_FIX_COMPLETE.md)
rm CORS_CHANGES.md CORS_SETUP_SUMMARY.md CORS_VERIFICATION.md QUICK_CORS_FIX.md

# Delete outdated deployment docs
rm DEPLOYMENT_STATUS.md VERCEL_FIX.md ANALYTICS_IMPLEMENTATION_SUMMARY.md

# Delete backups
rm requirements.txt.bak test_medical_bill.txt

# Delete old config files
rm backend-env-vars.yaml cloud-run-env-update.yaml cloud-run-env.yaml

# Delete duplicate docs
rm docs/BETA_MODE.md docs/BETA_MODE_QUICKSTART.md
rm docs/QUICKSTART.md
rm docs/IMPLEMENTATION_PROGRESS.md docs/IMPLEMENTATION_SUMMARY.md

# Commit
git add -A
git commit -m "chore: remove redundant and outdated documentation"
```

---

## 📝 Files to Keep

### Root Level
- ✅ `CORS_FIX_COMPLETE.md` - Definitive CORS solution
- ✅ `FIREBASE_SETUP.md` - Setup instructions (move to docs/ if needed)
- ✅ `DEPLOYMENT_CHECKLIST.md` - Active checklist
- ✅ `RELEASE_NOTES_v0.3.1.md` - Current release
- ✅ `README.md` - Main readme
- ✅ `.env.example` - Template for env vars

### docs/
- ✅ `docs/README.md` - Documentation index
- ✅ `docs/ARCHITECTURE.md` - System architecture
- ✅ `docs/USER_GUIDE.md` - User documentation
- ✅ `docs/BETA_MODE_GUIDE.md` - Comprehensive beta guide
- ✅ `docs/QUICK_START.md` - Getting started guide
- ✅ `docs/IMPLEMENTATION_ROADMAP.md` - Development roadmap
- ✅ `docs/TESTING.md` - Testing documentation
- ✅ `docs/TROUBLESHOOTING.md` - Problem solving

---

## 🎯 Next Steps

1. Review this cleanup plan
2. Choose Option 1 (archive) or Option 2 (delete)
3. Execute cleanup
4. Update `docs/README.md` or `docs/INDEX.md` to reflect remaining docs
5. Commit changes

---

## ⚠️ Before Deleting

- Verify CORS_FIX_COMPLETE.md contains all necessary CORS information
- Ensure current deployment processes don't reference removed files
- Check if any scripts reference removed config files
- Consider creating a single `docs/RELEASE_NOTES.md` that includes all versions
