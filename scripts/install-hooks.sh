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
# Pre-commit hook: Auto-generate documentation
#
# This ensures documentation is always up-to-date with the code.
# Documentation is derived from code-owned facts, not written by hand.

set -e

echo "🔄 Pre-commit hook: Generating documentation..."

# Generate documentation
make docs

# Check if docs were modified
if git diff --name-only | grep -q "^docs/"; then
    echo "📝 Documentation updated. Adding to commit..."
    git add docs/
    echo "✅ Documentation changes staged"
else
    echo "✓ Documentation already up-to-date"
fi

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
echo "  • pre-commit: Auto-generates documentation"
echo ""
echo "To bypass hooks temporarily, use:"
echo "  git commit --no-verify"
echo ""
