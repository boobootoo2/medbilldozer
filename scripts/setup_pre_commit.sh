#!/bin/bash
# Setup pre-commit hooks for development

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up pre-commit hooks...${NC}"

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo -e "${YELLOW}Installing pre-commit...${NC}"
    pip install pre-commit
fi

# Install the git hook scripts
echo -e "${YELLOW}Installing git hooks...${NC}"
pre-commit install

# Install commit-msg hook (optional, for conventional commits)
pre-commit install --hook-type commit-msg 2>/dev/null || true

echo -e "${GREEN}✅ Pre-commit hooks installed!${NC}"

# Run hooks on all files to test
echo -e "${YELLOW}Running hooks on all files (this may take a moment)...${NC}"
pre-commit run --all-files || {
    echo -e "${YELLOW}⚠️  Some hooks failed. This is normal on first run.${NC}"
    echo -e "${YELLOW}The hooks will auto-fix issues when you commit.${NC}"
}

echo ""
echo -e "${GREEN}Done! Your pre-commit hooks are set up.${NC}"
echo ""
echo -e "What happens now:"
echo -e "  • Every commit will automatically run code quality checks"
echo -e "  • CORS configuration will be validated to prevent upload issues"
echo -e "  • Code formatting will be applied automatically"
echo -e "  • Security issues will be detected"
echo ""
echo -e "To run hooks manually:"
echo -e "  ${YELLOW}pre-commit run --all-files${NC}"
echo ""
echo -e "To skip hooks (not recommended):"
echo -e "  ${YELLOW}git commit --no-verify${NC}"
