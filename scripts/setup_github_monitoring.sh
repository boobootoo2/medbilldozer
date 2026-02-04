#!/bin/bash
# Setup script for GitHub Actions monitoring integration

set -e

echo "🔧 GitHub Actions Monitoring Setup"
echo "=================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "   Install from: https://cli.github.com/"
    echo "   Or run: brew install gh"
    exit 1
fi

# Check if logged in
if ! gh auth status &> /dev/null; then
    echo "❌ Not logged into GitHub CLI."
    echo "   Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI detected"
echo ""

# Prompt for Supabase credentials
echo "📝 Please provide your Supabase credentials:"
echo ""

read -p "Supabase URL (https://xxx.supabase.co): " SUPABASE_URL
read -sp "Supabase Service Role Key: " SUPABASE_SERVICE_ROLE_KEY
echo ""
echo ""

# Validate inputs
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo "❌ Both URL and key are required"
    exit 1
fi

# Set secrets
echo "🔐 Setting GitHub secrets..."
echo ""

gh secret set SUPABASE_URL --body "$SUPABASE_URL"
gh secret set SUPABASE_SERVICE_ROLE_KEY --body "$SUPABASE_SERVICE_ROLE_KEY"

echo ""
echo "✅ Secrets configured successfully!"
echo ""

# Check if workflows exist
if [ ! -f ".github/workflows/run_benchmarks.yml" ]; then
    echo "⚠️  Warning: run_benchmarks.yml not found"
fi

if [ ! -f ".github/workflows/benchmark-persist.yml" ]; then
    echo "⚠️  Warning: benchmark-persist.yml not found"
fi

echo "📋 Next Steps:"
echo ""
echo "1. Verify secrets in GitHub:"
echo "   https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/settings/secrets/actions"
echo ""
echo "2. Test the workflow:"
echo "   gh workflow run run_benchmarks.yml"
echo ""
echo "3. Monitor workflow runs:"
echo "   gh run list --workflow=run_benchmarks.yml"
echo ""
echo "4. View results in dashboard:"
echo "   make monitoring-dashboard"
echo ""
echo "🎉 Setup complete!"
