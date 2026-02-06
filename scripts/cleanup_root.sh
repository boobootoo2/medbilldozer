#!/bin/bash

# Root Directory Cleanup Script
# Organizes root-level files into logical subdirectories

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          Root Directory Cleanup Script                        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes."
    echo "   This script will use 'git mv' to preserve history."
    echo ""
    read -p "Continue? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

echo "Creating new directory structure..."
echo ""

# Step 1: Create new directories
echo "📁 Creating directories..."
mkdir -p .artifacts
mkdir -p examples
mkdir -p config/examples

echo "✓ Directories created"
echo ""

# Step 2: Move build artifacts
echo "📦 Moving build artifacts..."

if [ -f "bandit-report.json" ]; then
    git mv bandit-report.json .artifacts/ 2>/dev/null || mv bandit-report.json .artifacts/
    echo "  ✓ bandit-report.json → .artifacts/"
fi

if [ -f "error_type_performance.csv" ]; then
    git mv error_type_performance.csv .artifacts/ 2>/dev/null || mv error_type_performance.csv .artifacts/
    echo "  ✓ error_type_performance.csv → .artifacts/"
fi

if [ -f "COMMIT_MESSAGE.txt" ]; then
    git mv COMMIT_MESSAGE.txt .artifacts/ 2>/dev/null || mv COMMIT_MESSAGE.txt .artifacts/
    echo "  ✓ COMMIT_MESSAGE.txt → .artifacts/"
fi

echo ""

# Step 3: Move example files
echo "📚 Moving example files..."

if [ -f "profile_integration_example.py" ]; then
    git mv profile_integration_example.py examples/ 2>/dev/null || mv profile_integration_example.py examples/
    echo "  ✓ profile_integration_example.py → examples/"
fi

if [ -f "fix_linting.py" ]; then
    git mv fix_linting.py examples/ 2>/dev/null || mv fix_linting.py examples/
    echo "  ✓ fix_linting.py → examples/"
fi

# Create examples README
cat > examples/README.md << 'EOF'
# Examples

Example code and utility scripts for medBillDozer.

## Files

### profile_integration_example.py

Patient profile integration examples showing how to:
- Load patient profiles
- Generate benchmark test cases
- Integrate with the analysis pipeline

**Usage**:
```bash
python examples/profile_integration_example.py
```

### fix_linting.py

Utility script for automatically fixing common linting issues.

**Usage**:
```bash
python examples/fix_linting.py <file_or_directory>
```

## Related Documentation

- [Development Setup](../docs/development/setup.md)
- [Package Structure](../docs/development/package_structure.md)
- [Testing Guide](../docs/development/testing.md)
EOF

git add examples/README.md 2>/dev/null || true
echo "  ✓ examples/README.md created"
echo ""

# Step 4: Move config example
echo "⚙️  Moving configuration examples..."

if [ -f "app_config.example.yaml" ]; then
    git mv app_config.example.yaml config/examples/ 2>/dev/null || mv app_config.example.yaml config/examples/
    echo "  ✓ app_config.example.yaml → config/examples/"
    
    # Create symlink for backward compatibility
    ln -sf config/examples/app_config.example.yaml app_config.example.yaml
    echo "  ✓ Created symlink for backward compatibility"
fi

echo ""

# Step 5: Move old README to archive
echo "📄 Archiving old documentation..."

if [ -f "README_OLD.md" ]; then
    # Ensure archive directory exists
    mkdir -p docs_archive_20260205/root_markdown/
    
    git mv README_OLD.md docs_archive_20260205/root_markdown/ 2>/dev/null || mv README_OLD.md docs_archive_20260205/root_markdown/
    echo "  ✓ README_OLD.md → docs_archive_20260205/root_markdown/"
fi

echo ""

# Step 6: Update .gitignore
echo "🔒 Updating .gitignore..."

if ! grep -q ".artifacts/" .gitignore; then
    cat >> .gitignore << 'EOF'

# Build artifacts directory
.artifacts/
*.json.bak
*.csv.bak

# Example outputs
examples/output/
examples/*.log
EOF
    echo "  ✓ Added .artifacts/ and examples/ patterns"
    git add .gitignore 2>/dev/null || true
fi

echo ""

# Step 7: Update documentation references
echo "📝 Updating documentation references..."

# Update PROFILE_EDITOR_QUICKSTART.md
if [ -f "docs/PROFILE_EDITOR_QUICKSTART.md" ]; then
    sed -i.bak 's|(\./profile_integration_example\.py)|(../examples/profile_integration_example.py)|g' docs/PROFILE_EDITOR_QUICKSTART.md
    rm -f docs/PROFILE_EDITOR_QUICKSTART.md.bak
    echo "  ✓ Updated docs/PROFILE_EDITOR_QUICKSTART.md"
fi

# Update PROFILE_EDITOR_CHANGELOG.md
if [ -f "docs/PROFILE_EDITOR_CHANGELOG.md" ]; then
    sed -i.bak 's|profile_integration_example\.py|examples/profile_integration_example.py|g' docs/PROFILE_EDITOR_CHANGELOG.md
    sed -i.bak 's|(\./profile_integration_example\.py)|(../examples/profile_integration_example.py)|g' docs/PROFILE_EDITOR_CHANGELOG.md
    rm -f docs/PROFILE_EDITOR_CHANGELOG.md.bak
    echo "  ✓ Updated docs/PROFILE_EDITOR_CHANGELOG.md"
fi

# Update export_error_type_performance.py
if [ -f "scripts/export_error_type_performance.py" ]; then
    sed -i.bak "s|output_file='error_type_performance.csv'|output_file='.artifacts/error_type_performance.csv'|g" scripts/export_error_type_performance.py
    sed -i.bak "s|default='error_type_performance.csv'|default='.artifacts/error_type_performance.csv'|g" scripts/export_error_type_performance.py
    rm -f scripts/export_error_type_performance.py.bak
    echo "  ✓ Updated scripts/export_error_type_performance.py"
fi

echo ""

# Show final structure
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                  Cleanup Complete! ✅                         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo "New directory structure:"
echo ""
echo "Root directory:"
ls -1 | grep -E "^[^.]" | grep -v -E "(src|tests|pages|scripts|docs|benchmarks|data|images|audio|static|sql|config|_modules|examples|\.artifacts)" | head -20
echo ""

echo ".artifacts/ (NEW):"
ls -1 .artifacts/ 2>/dev/null | head -5 || echo "  (empty)"
echo ""

echo "examples/ (NEW):"
ls -1 examples/ 2>/dev/null | head -5 || echo "  (empty)"
echo ""

echo "config/examples/ (NEW):"
ls -1 config/examples/ 2>/dev/null | head -5 || echo "  (empty)"
echo ""

echo "Files moved:"
echo "  • 3 build artifacts → .artifacts/"
echo "  • 2 example files → examples/"
echo "  • 1 config example → config/examples/"
echo "  • 1 old README → docs_archive_20260205/"
echo ""
echo "Total: 7 files organized, root directory cleaned"
echo ""

echo "Next steps:"
echo ""
echo "1. Test the application:"
echo "   streamlit run medBillDozer.py"
echo ""
echo "2. Run tests:"
echo "   pytest"
echo ""
echo "3. Check examples work:"
echo "   python examples/profile_integration_example.py"
echo ""
echo "4. Review changes:"
echo "   git status"
echo "   git diff"
echo ""
echo "5. Commit if everything looks good:"
echo "   git commit -m 'chore: Clean up root directory structure"
echo ""
echo "   - Move build artifacts to .artifacts/"
echo "   - Move examples to examples/"
echo "   - Move config example to config/examples/"
echo "   - Archive old README"
echo "   - Update documentation references"
echo "   '"
echo ""
echo "To rollback: git reset --hard HEAD"
echo ""
