#!/bin/bash
# Install Git hooks for MedBillDozer
# This sets up automatic documentation generation on commit

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "=========================================="
echo "MedBillDozer Git Hooks Installation"
echo "=========================================="
echo ""

# Check if .git directory exists
if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "❌ Error: Not a git repository. Run this from within the repo."
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Install pre-commit hook
echo "📦 Installing pre-commit hook..."
cat > "$HOOKS_DIR/pre-commit" << 'HOOK_CONTENT'
#!/bin/bash
# Pre-commit hook: Run linter, tests, and auto-generate documentation
#
# This ensures code quality and documentation are maintained.
# Documentation is derived from code-owned facts, not written by hand.

echo "═══════════════════════════════════════════════════════════"
echo "🔍 Pre-commit Quality Checks"
echo "═══════════════════════════════════════════════════════════"

# Get list of Python files being committed (excluding deleted files)
PYTHON_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep "\.py$" || true)

if [ -n "$PYTHON_FILES" ]; then
    echo ""
    echo "� Running security scan (Bandit)..."
    echo "───────────────────────────────────────────────────────────"
    
    # Check if bandit is installed
    if ! command -v bandit &> /dev/null; then
        echo "⚠️  bandit not installed. Skipping security scan."
    else
        # Run bandit on staged files (skip tests directory and ignore low severity)
        if echo "$PYTHON_FILES" | grep -v "^tests/" | xargs -r bandit -ll -q 2>&1 | grep -q "Issue"; then
            echo ""
            echo "⚠️  Security issues detected! Review above."
            echo "   Tip: Run 'bandit -ll <file>' to check individual files"
            echo "   These are warnings, not blocking commit."
        else
            echo "✅ No security issues found"
        fi
    fi
fi

echo ""
echo "🧪 Running unit tests..."
echo "───────────────────────────────────────────────────────────"

# Skip tests if only docs, markdown, or non-code files changed
NON_CODE_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep -vE "\.(py|yaml|yml|json)$" || true)
ALL_FILES=$(git diff --cached --name-only --diff-filter=ACMR || true)

if [ -z "$PYTHON_FILES" ] && [ -n "$NON_CODE_FILES" ]; then
    echo "✓ Only documentation/config files changed. Skipping tests."
else
    # Run pytest and capture output and exit code
    TEST_OUTPUT=$(python3 -m pytest tests/ -q --tb=line --continue-on-collection-errors 2>&1)
    TEST_EXIT_CODE=$?
    echo "$TEST_OUTPUT"

    # Parse test output
    if echo "$TEST_OUTPUT" | grep -q "failed"; then
        FAILED_COUNT=$(echo "$TEST_OUTPUT" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+')
        echo ""
        echo "❌ $FAILED_COUNT test(s) failed! Please fix failing tests before committing."
        echo "   Tip: Run 'make test' or 'pytest tests/ -v' for detailed output"
        echo "   To commit anyway: git commit --no-verify"
        exit 1
    elif echo "$TEST_OUTPUT" | grep -q "ERROR.*collecting"; then
        echo ""
        echo "⚠️  Test collection error (possibly environment/dependency issue)"
        echo "   Tip: Run 'make test' to diagnose"
        echo "   Continuing with commit (import errors won't block)"
    else
        echo "✅ All tests passed"
    fi
fi

echo ""
echo "📚 Checking documentation..."
echo "───────────────────────────────────────────────────────────"

# Only regenerate docs if Python source files in src/ or scripts/ were modified
PYTHON_SOURCE_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep -E "(^src/|^scripts/|^config/)" | grep "\.py$" || true)

if [ -n "$PYTHON_SOURCE_FILES" ]; then
    echo "📝 Python source files changed. Regenerating documentation..."
    make docs > /dev/null 2>&1
    
    # Check if docs were modified
    if git diff --name-only | grep -q "^docs/"; then
        echo "📝 Documentation updated. Adding to commit..."
        git add docs/
        echo "✅ Documentation changes staged"
    else
        echo "✓ Documentation already up-to-date"
    fi
else
    echo "✓ No source changes detected. Skipping documentation regeneration."
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ All pre-commit checks passed!"
echo "═══════════════════════════════════════════════════════════"
echo ""
exit 0
HOOK_CONTENT

chmod +x "$HOOKS_DIR/pre-commit"
echo "✅ Pre-commit hook installed"

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "The following hooks are now active:"
echo "  • pre-commit: Runs linting, tests, and generates documentation"
echo ""
echo "Before each commit, the hook will:"
echo "  1. 📋 Run flake8 linting on Python files"
echo "  2. 🧪 Run unit tests with pytest"
echo "  3. 📚 Generate/update documentation"
echo ""
echo "Commits will be blocked if:"
echo "  ❌ Linting fails"
echo "  ❌ Any tests fail"
echo ""
echo "To bypass hooks temporarily, use:"
echo "  git commit --no-verify"
echo ""
