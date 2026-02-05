#!/bin/bash
# Archive old documentation to docs_archive_20260205/
# Execute from repository root: bash scripts/archive_old_docs.sh

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════"
echo "📦 Documentation Archival Script"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Create archive directory structure
echo "📁 Creating archive directories..."
mkdir -p docs_archive_20260205/{root_markdown,docs_old,benchmarks_old}

# Count files before archival
root_count=$(ls -1 *.md 2>/dev/null | grep -v "README.md" | grep -v "README_NEW.md" | grep -v "LICENSE" | wc -l | tr -d ' ')
docs_count=$(find docs -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
bench_count=$(find benchmarks -name "*.md" -o -name "*.txt" 2>/dev/null | wc -l | tr -d ' ')

echo "   Found $root_count markdown files in root"
echo "   Found $docs_count markdown files in docs/"
echo "   Found $bench_count doc files in benchmarks/"
echo ""

# Archive root-level markdown (excluding README.md and LICENSE)
echo "📋 Archiving root-level documentation..."
for file in *_COMPLETE.md *_SUMMARY.md *_QUICKSTART.md *_FIX.md *_STATUS.md *_GUIDE.md *_OVERVIEW.md *_CERTIFICATE.md *_REPORT.md *_README.md *_DELIVERABLES.md *_DEPLOYMENT.md *_QUICKREF.md *_COMPARISON.md; do
    if [ -f "$file" ]; then
        git mv "$file" docs_archive_20260205/root_markdown/ 2>/dev/null || mv "$file" docs_archive_20260205/root_markdown/
        echo "   ✓ $file"
    fi
done

# Archive specific legacy docs
legacy_docs=(
    "ANNOTATION_SYSTEM_OVERVIEW.md"
    "ANNOTATION_SYSTEM_SUMMARY.md"
    "API_KEYS_QUICKSTART.md"
    "DOCUMENTATION_INDEX.md"
    "ENHANCED_PATIENT_BENCHMARKS.md"
    "PARENT_CATEGORY_SUMMARY.md"
    "PARENT_CATEGORY_AGGREGATION.md"
    "CROSS_DOCUMENT_BENCHMARK_QUICKSTART.md"
    "MIGRATION_GUIDE.md"
    "MIGRATION_QUICK_START.md"
    "SOLUTION_SUMMARY.md"
    "TRIGGERED_BY_FEATURE.md"
)

for file in "${legacy_docs[@]}"; do
    if [ -f "$file" ]; then
        git mv "$file" docs_archive_20260205/root_markdown/ 2>/dev/null || mv "$file" docs_archive_20260205/root_markdown/
        echo "   ✓ $file"
    fi
done

echo ""

# Archive docs/ subdirectory files
echo "📚 Archiving docs/ summaries and delivery logs..."

# Archive by pattern
for pattern in "*_SUMMARY.md" "*_DELIVERY.md" "*_COMPLETE.md" "*_FIX.md" "*_IMPLEMENTATION*.md" "CHANGELOG_*.md" "*-SUMMARY.md" "*-FIX.md" "KAGGLE_SUBMISSION_*.md"; do
    find docs -name "$pattern" -type f -exec sh -c '
        for file; do
            if [ -f "$file" ]; then
                dest="docs_archive_20260205/docs_old/$(basename "$file")"
                git mv "$file" "$dest" 2>/dev/null || mv "$file" "$dest"
                echo "   ✓ $(basename $file)"
            fi
        done
    ' sh {} +
done

# Archive specific docs files
docs_to_archive=(
    "docs/COMMIT-CHECKLIST.md"
    "docs/PRE-COMMIT-HOOKS.md"
    "docs/PROJECT_DESCRIPTION_SHORT.md"
    "docs/PROJECT_DESCRIPTION_2026.md"
    "docs/PROJECT_UPDATES_SUMMARY.md"
    "docs/GITHUB-ACTIONS-SUMMARY.md"
    "docs/WORKFLOW-FIX-SUMMARY.md"
    "docs/FINAL-FIX-SUMMARY.md"
    "docs/STREAMLIT-MOCK-FIX.md"
    "docs/competitive_landscape.md"
    "docs/pitch.md"
)

for file in "${docs_to_archive[@]}"; do
    if [ -f "$file" ]; then
        git mv "$file" docs_archive_20260205/docs_old/ 2>/dev/null || mv "$file" docs_archive_20260205/docs_old/
        echo "   ✓ $(basename $file)"
    fi
done

echo ""

# Archive benchmarks/ documentation (preserve ANNOTATION_GUIDE.md and GROUND_TRUTH_SCHEMA.md)
echo "🎯 Archiving benchmarks/ documentation..."

benchmark_docs_to_archive=(
    "benchmarks/COMPLETE_SUMMARY.md"
    "benchmarks/DELIVERABLES.md"
    "benchmarks/EXPANDED_PATIENT_BENCHMARKS.md"
    "benchmarks/IMPLEMENTATION_COMPLETE.txt"
    "benchmarks/IMPLEMENTATION_NOTES.md"
    "benchmarks/IMPLEMENTATION_SUMMARY.md"
    "benchmarks/INDEX.md"
    "benchmarks/PATIENT_BENCHMARKS_README.md"
    "benchmarks/PATIENT_BENCHMARK_SUMMARY.md"
    "benchmarks/QUICKSTART.md"
    "benchmarks/QUICK_REFERENCE.md"
    "benchmarks/README_ANNOTATION_SYSTEM.md"
    "benchmarks/VISUAL_GUIDE.txt"
)

for file in "${benchmark_docs_to_archive[@]}"; do
    if [ -f "$file" ]; then
        git mv "$file" docs_archive_20260205/benchmarks_old/ 2>/dev/null || mv "$file" docs_archive_20260205/benchmarks_old/
        echo "   ✓ $(basename $file)"
    fi
done

echo ""

# Count archived files
archived_count=$(find docs_archive_20260205 -type f | wc -l | tr -d ' ')

echo "═══════════════════════════════════════════════════════════"
echo "✅ Archival Complete"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📊 Summary:"
echo "   • Archived $archived_count documentation files"
echo "   • Location: docs_archive_20260205/"
echo "   • Preserved: README.md, LICENSE, ANNOTATION_GUIDE.md, GROUND_TRUTH_SCHEMA.md"
echo ""
echo "📝 Next Steps:"
echo "   1. Review archived files: ls docs_archive_20260205/*/"
echo "   2. Replace README.md: mv README_NEW.md README.md"
echo "   3. Commit changes: git commit -am 'docs: restructure documentation'"
echo ""
echo "═══════════════════════════════════════════════════════════"
