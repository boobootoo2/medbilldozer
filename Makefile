# MedBillDozer Makefile
# Convenience commands for development

.PHONY: help docs docs-view run test clean install-hooks monitoring-setup monitoring-test monitoring-dashboard

help:
	@echo "MedBillDozer Development Commands"
	@echo "=================================="
	@echo ""
	@echo "  make docs                - Generate automatic documentation"
	@echo "  make docs-view           - Generate docs and open in browser"
	@echo "  make install-hooks       - Install git hooks (auto-docs on commit)"
	@echo "  make run                 - Run the Streamlit app"
	@echo "  make test                - Run tests"
	@echo "  make clean               - Clean up generated files"
	@echo ""
	@echo "Benchmark Monitoring:"
	@echo "  make monitoring-setup    - Install monitoring dependencies"
	@echo "  make monitoring-test     - Test benchmark persistence"
	@echo "  make monitoring-dashboard - Launch monitoring dashboard"
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

# Benchmark Monitoring Commands
monitoring-setup:
	@echo "📊 Installing benchmark monitoring dependencies..."
	@pip install -r requirements-monitoring.txt
	@echo "✅ Monitoring dependencies installed"
	@echo ""
	@echo "Next steps:"
	@echo "1. Set up Supabase: https://supabase.com"
	@echo "2. Run SQL schema: sql/schema_benchmark_monitoring.sql"
	@echo "3. Set environment variables:"
	@echo "   export SUPABASE_URL='https://xxxxx.supabase.co'"
	@echo "   export SUPABASE_SERVICE_ROLE_KEY='your-key'"
	@echo "4. Test: make monitoring-test"
	@echo ""
	@echo "See docs/BENCHMARK_MONITORING_SETUP.md for details"

monitoring-test:
	@echo "🧪 Testing benchmark persistence..."
	@if [ -z "$$SUPABASE_URL" ] || [ -z "$$SUPABASE_SERVICE_ROLE_KEY" ]; then \
		echo "❌ Error: Environment variables not set"; \
		echo "Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY"; \
		exit 1; \
	fi
	@python3 scripts/push_to_supabase.py \
		--input benchmarks/sample_benchmark_results.json \
		--environment local \
		--commit-sha $$(git rev-parse HEAD 2>/dev/null || echo "no-git") \
		--triggered-by $$(whoami) \
		--verify
	@echo ""
	@echo "✅ Test completed! Check your Supabase dashboard"

monitoring-dashboard:
	@echo "🚀 Launching benchmark monitoring dashboard..."
	@if [ ! -f .env ]; then \
		echo "⚠️  Warning: .env file not found"; \
		echo "Please create .env from .env.example and add your Supabase credentials"; \
		exit 1; \
	fi
	@/usr/local/bin/python3 -m streamlit run pages/benchmark_monitoring.py
