# Snapshot History UI Guide

## Overview

The **Snapshot History** tab in the Benchmark Monitoring Dashboard provides a comprehensive interface for viewing and managing snapshot versions of your ML models.

## Features

### 1. Model Selection
- Select any model from the dropdown to view its version history
- Shows all models that have snapshots in the database

### 2. Version History Overview
Displays key metrics at the top:
- **Total Versions**: Number of snapshot versions for the selected model
- **Current Version**: The currently active version (marked as "current")
- **Baselines**: Number of baseline snapshots
- **Latest F1**: F1 score of the most recent version

### 3. Snapshot Version Table
Shows all historical versions with:
- **Version**: Sequential version number (v1, v2, v3, etc.)
- **Status**: Visual indicators
  - ✅ CURRENT - Currently active version
  - ⭐ BASELINE - Baseline version (typically v1)
  - Empty - Historical version
- **Performance Metrics**: F1, Precision, Recall scores
- **Latency**: Response time in milliseconds
- **Created At**: Timestamp of snapshot creation
- **Commit SHA**: Git commit that created this version

### 4. Checkout/Rollback Feature

**Purpose**: Revert to a previous snapshot version to compare or restore performance.

**How to Use**:
1. Select a version from the dropdown under "Checkout Snapshot Version"
2. Review the version details shown (F1, Precision, Recall, Commit)
3. Click **"🔄 Checkout This Version"** button
4. The selected version will be marked as the new "current" version
5. The dashboard will automatically refresh to show the checked-out version

**Use Cases**:
- **Rollback**: Revert to a better-performing version after a regression
- **Comparison**: Temporarily checkout an old version to compare behavior
- **Testing**: Validate that an older configuration still works
- **Audit**: Inspect historical model states for compliance

### 5. Version Comparison

**Purpose**: Side-by-side comparison of two snapshot versions.

**How to Use**:
1. Select **Version A** from the first dropdown
2. Select **Version B** from the second dropdown
3. Click **"Compare"** button
4. View the comparison table showing:
   - Metric name
   - Version A value
   - Version B value
   - Delta (absolute change)
   - Percent change

**Highlights**:
- Improvements are automatically highlighted
- Shows metrics like F1, Precision, Recall, Latency
- Helps identify regressions or improvements

## Example Workflows

### Workflow 1: Investigate a Regression

1. Go to "Snapshot History" tab
2. Select the affected model
3. Review the version history table - sort by F1 to find the drop
4. Compare the regressed version with the previous version
5. Checkout the previous version if rollback is needed
6. Review commit SHA to identify code changes

### Workflow 2: Compare Recent Changes

1. Select your model
2. Use Version Comparison to compare latest two versions
3. Review delta and percent change
4. Determine if the change is significant

### Workflow 3: Baseline Comparison

1. Select a model with multiple versions
2. Compare current version (e.g., v4) with baseline (v1)
3. Review overall progress/improvement
4. Verify against business metrics

## Database Behavior

### What Happens During Checkout

When you checkout a version:
1. The `is_current` flag is updated in the database
2. The selected version is marked as `is_current = TRUE`
3. All other versions for that model/config are marked as `is_current = FALSE`
4. Historical data is preserved (no deletion)
5. Dashboard queries now show the checked-out version as "current"

### Versioning Strategy

- **Sequential Versioning**: v1, v2, v3, etc.
- **Immutable History**: Old versions are never deleted
- **One Current Version**: Only one version is current per model configuration
- **Baseline Tracking**: v1 is typically marked as baseline for comparison

## Testing the Feature

### Sample Data Populated

The system has been pre-populated with test data:

| Model | Versions | Current | Baseline |
|-------|----------|---------|----------|
| openai-gpt4-v1.0 | 4 | v4 | v1 |
| gemini-pro-v1.5 | 3 | v3 | v1 |
| claude-3-opus | 2 | v2 | v1 |
| medgemma-v1.2 | 3 | v3 | v1 |
| baseline-v1.0 | 1 | v1 | v1 |

### Try It Out

1. **View History**:
   ```
   Select "openai-gpt4-v1.0" → See 4 versions with v4 marked as CURRENT
   ```

2. **Checkout Old Version**:
   ```
   Select v2 from dropdown → Click "Checkout This Version"
   Dashboard refreshes → v2 is now CURRENT
   ```

3. **Compare Versions**:
   ```
   Version A: v1 (baseline)
   Version B: v4 (latest)
   Click "Compare" → See performance improvement
   ```

## Troubleshooting

### Issue: "No snapshot history found"
**Solution**: The selected model has no snapshots. Run benchmarks to create snapshots.

### Issue: Checkout button does nothing
**Solution**: Check browser console for errors. Verify Supabase connection in `.env` file.

### Issue: Version comparison shows no data
**Solution**: Ensure both versions exist for the selected model. Check data in database.

### Issue: Dashboard doesn't refresh after checkout
**Solution**: Manually refresh the page or use the "Refresh Data" button.

## Best Practices

1. **Baseline Management**: Always keep v1 as your baseline for long-term comparisons
2. **Frequent Snapshots**: Create snapshots after significant changes
3. **Document Checkouts**: Add notes in git commits when checking out older versions
4. **Version Limit**: Consider archiving very old versions (>50) to keep the interface clean
5. **Testing Before Checkout**: Review version details before checking out in production

## Related Documentation

- [Snapshot Versioning Guide](SNAPSHOT_VERSIONING_GUIDE.md) - Backend architecture
- [Benchmark Monitoring Setup](BENCHMARK_MONITORING_SETUP.md) - Initial setup
- [Benchmark Persistence Architecture](BENCHMARK_PERSISTENCE_ARCHITECTURE.md) - Database design

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Review logs: `scripts/check_snapshots.py` to query current database state
3. Validate database connection: Check `.env` file credentials
4. Contact the MLOps team for assistance

---

**Last Updated**: 2026-02-03  
**Version**: 1.0  
**Dashboard Version**: Benchmark Monitoring Dashboard v1.0
