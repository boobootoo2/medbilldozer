# MedBillDozer Makefile
# Convenience commands for development

.PHONY: help docs docs-view run test clean install-hooks

help:
	@echo "MedBillDozer Development Commands"
	@echo "=================================="
	@echo ""
	@echo "  make docs          - Generate automatic documentation"
	@echo "  make docs-view     - Generate docs and open in browser"
	@echo "  make install-hooks - Install git hooks (auto-docs on commit)"
	@echo "  make run           - Run the Streamlit app"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean up generated files"
	@echo ""

docs:
	@echo "📚 Generating documentation from codebase..."
	@python3 scripts/generate_docs.py
	@echo ""
	@echo "✅ Documentation generated in docs/"

docs-view: docs
	@echo "🌐 Opening documentation..."
	@open docs/README.md || xdg-open docs/README.md || echo "Please open docs/README.md manually"

install-hooks:
	@echo "🔧 Installing git hooks..."
	@bash scripts/install-hooks.sh

run:
	@echo "🚀 Starting MedBillDozer..."
	@streamlit run app.py

test:
	@echo "🧪 Running tests..."
	@python3 -m pytest tests/ -v

clean:
	@echo "🧹 Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✓ Cleaned up Python cache files"
