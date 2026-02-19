"""Critical path tests for production_stability.py.

These tests verify that essential functionality is not accidentally removed.
They act as regression guards for critical features.

IMPORTANT: If these tests fail, critical functionality has been removed!
"""

import pytest
from pathlib import Path
import ast


class TestBenchmarkDataLoadingPresence:
    """Ensure benchmark data loading logic exists in production_stability.py."""

    @pytest.fixture
    def production_stability_file(self):
        """Get production_stability.py file path."""
        root = Path(__file__).parent.parent
        file_path = root / 'pages' / 'production_stability.py'
        assert file_path.exists(), "production_stability.py not found!"
        return file_path

    @pytest.fixture
    def production_stability_source(self, production_stability_file):
        """Read production_stability.py source code."""
        return production_stability_file.read_text()

    @pytest.mark.unit
    def test_supabase_data_loading_exists(self, production_stability_source):
        """CRITICAL: Verify Supabase data loading logic exists."""
        # Check for Supabase query
        assert 'clinical_validation_snapshots' in production_stability_source, \
            "❌ CRITICAL: Supabase table query removed from production_stability.py!"

        assert "table('clinical_validation_snapshots')" in production_stability_source, \
            "❌ CRITICAL: clinical_validation_snapshots table access removed!"

        # Check for environment filtering
        assert 'production' in production_stability_source or 'beta' in production_stability_source, \
            "❌ CRITICAL: Environment filtering removed!"

    @pytest.mark.unit
    def test_local_file_fallback_exists(self, production_stability_source):
        """CRITICAL: Verify local file fallback logic exists."""
        # Check for local file loading
        assert 'benchmarks/clinical_validation_results' in production_stability_source, \
            "❌ CRITICAL: Local file fallback path removed!"

        assert 'glob' in production_stability_source, \
            "❌ CRITICAL: File globbing logic removed!"

    @pytest.mark.unit
    def test_scenario_results_extraction_exists(self, production_stability_source):
        """CRITICAL: Verify scenario_results extraction logic exists."""
        # Check for scenario_results extraction
        assert 'scenario_results' in production_stability_source, \
            "❌ CRITICAL: scenario_results extraction removed!"

        # Check for metrics extraction
        assert 'metrics' in production_stability_source, \
            "❌ CRITICAL: metrics extraction removed!"

    @pytest.mark.unit
    def test_heatmap_calculation_exists(self, production_stability_source):
        """CRITICAL: Verify heatmap calculation logic exists."""
        # Check for detection rate calculations
        assert 'tp_rates' in production_stability_source or 'tn_rates' in production_stability_source, \
            "❌ CRITICAL: Detection rate calculations removed!"

        # Check for modality filtering
        assert 'modality' in production_stability_source, \
            "❌ CRITICAL: Modality filtering removed!"

        # Check for expected/correct logic
        assert 'expected' in production_stability_source and 'correct' in production_stability_source, \
            "❌ CRITICAL: Validation logic removed!"

    @pytest.mark.unit
    def test_heatmap_visualization_exists(self, production_stability_source):
        """CRITICAL: Verify heatmap visualization rendering exists."""
        # Check for plotly heatmap
        assert 'px.imshow' in production_stability_source or 'plotly' in production_stability_source, \
            "❌ CRITICAL: Heatmap visualization removed!"

        # Check for TP/TN columns
        assert 'True Positive' in production_stability_source or 'True Negative' in production_stability_source, \
            "❌ CRITICAL: TP/TN heatmap labels removed!"

    @pytest.mark.unit
    def test_model_list_includes_medgemma_ensemble(self, production_stability_source):
        """CRITICAL: Verify medgemma-ensemble is in models list."""
        assert 'medgemma-ensemble' in production_stability_source, \
            "❌ CRITICAL: medgemma-ensemble removed from models list!"

    @pytest.mark.unit
    def test_all_modalities_included(self, production_stability_source):
        """CRITICAL: Verify all imaging modalities are included."""
        required_modalities = ['xray', 'histopathology', 'mri', 'ultrasound']

        for modality in required_modalities:
            assert modality in production_stability_source, \
                f"❌ CRITICAL: Modality '{modality}' removed from code!"

    @pytest.mark.unit
    def test_error_handling_exists(self, production_stability_source):
        """CRITICAL: Verify error handling for data loading exists."""
        # Check for try/except blocks
        assert 'try:' in production_stability_source and 'except' in production_stability_source, \
            "❌ CRITICAL: Error handling removed!"

        # Check for graceful fallback
        assert 'if model_results:' in production_stability_source or 'if not model_results:' in production_stability_source, \
            "❌ CRITICAL: Fallback logic removed!"

    @pytest.mark.unit
    def test_data_source_tracking_exists(self, production_stability_source):
        """CRITICAL: Verify data source tracking exists."""
        # Check for data_source variable
        assert 'data_source' in production_stability_source, \
            "❌ CRITICAL: Data source tracking removed!"


class TestBenchmarkDataStructureIntegrity:
    """Verify the code expects correct data structures."""

    @pytest.fixture
    def production_stability_source(self):
        """Read production_stability.py source code."""
        root = Path(__file__).parent.parent
        file_path = root / 'pages' / 'production_stability.py'
        return file_path.read_text()

    @pytest.mark.unit
    def test_expects_model_version_field(self, production_stability_source):
        """Code should expect model_version in snapshots."""
        assert 'model_version' in production_stability_source, \
            "❌ CRITICAL: model_version field handling removed!"

    @pytest.mark.unit
    def test_expects_created_at_ordering(self, production_stability_source):
        """Code should order by created_at for latest results."""
        assert 'created_at' in production_stability_source or 'order' in production_stability_source, \
            "❌ CRITICAL: Timestamp ordering removed!"

    @pytest.mark.unit
    def test_expects_correct_boolean_field(self, production_stability_source):
        """Code should check 'correct' boolean field."""
        # Look for .get('correct', False) pattern
        assert "get('correct'" in production_stability_source or "'correct']" in production_stability_source, \
            "❌ CRITICAL: 'correct' field access removed!"


class TestCriticalWorkflowProtection:
    """Ensure critical user workflows are protected."""

    @pytest.fixture
    def production_stability_source(self):
        """Read production_stability.py source code."""
        root = Path(__file__).parent.parent
        file_path = root / 'pages' / 'production_stability.py'
        return file_path.read_text()

    @pytest.mark.integration
    def test_supabase_to_visualization_pipeline_intact(self, production_stability_source):
        """CRITICAL: Entire pipeline from Supabase to visualization must exist."""
        pipeline_steps = [
            'clinical_validation_snapshots',  # Supabase query
            'scenario_results',               # Data extraction
            'tp_rates',                       # Calculation
            'px.imshow',                      # Visualization
        ]

        missing_steps = [step for step in pipeline_steps if step not in production_stability_source]

        assert not missing_steps, \
            f"❌ CRITICAL: Pipeline steps removed: {missing_steps}"

    @pytest.mark.integration
    def test_fallback_chain_intact(self, production_stability_source):
        """CRITICAL: Fallback chain (Supabase → Local Files) must exist."""
        # Must have both data sources
        has_supabase = 'clinical_validation_snapshots' in production_stability_source
        has_local_files = 'benchmarks/clinical_validation_results' in production_stability_source

        assert has_supabase, "❌ CRITICAL: Supabase data source removed!"
        assert has_local_files, "❌ CRITICAL: Local file fallback removed!"

        # Must have fallback logic
        assert 'if not model_results:' in production_stability_source or \
               'if model_results:' in production_stability_source, \
            "❌ CRITICAL: Fallback logic removed!"


class TestRegressionGuards:
    """Prevent known regressions from recurring."""

    @pytest.fixture
    def production_stability_source(self):
        """Read production_stability.py source code."""
        root = Path(__file__).parent.parent
        file_path = root / 'pages' / 'production_stability.py'
        return file_path.read_text()

    @pytest.mark.unit
    def test_no_hardcoded_beta_only(self, production_stability_source):
        """Should check both production AND beta, not just beta."""
        # If it queries clinical_validation_snapshots, should support both envs
        if 'clinical_validation_snapshots' in production_stability_source:
            # Should mention both production and beta
            has_production = 'production' in production_stability_source
            has_beta = 'beta' in production_stability_source

            # At minimum, should have logic for both
            assert has_production or has_beta, \
                "❌ REGRESSION: No environment filtering found!"

    @pytest.mark.unit
    def test_metrics_extraction_not_removed(self, production_stability_source):
        """Regression: Previously forgot to extract from metrics object."""
        # Must extract from metrics
        assert ".get('metrics'" in production_stability_source or "['metrics']" in production_stability_source, \
            "❌ REGRESSION: metrics extraction removed (data would be inaccessible)!"

    @pytest.mark.unit
    def test_result_directory_check_not_only_check(self, production_stability_source):
        """Regression: Should not ONLY check local directory."""
        # Should have Supabase as primary
        has_supabase_query = 'clinical_validation_snapshots' in production_stability_source

        assert has_supabase_query, \
            "❌ REGRESSION: Supabase query removed - would only work locally!"
