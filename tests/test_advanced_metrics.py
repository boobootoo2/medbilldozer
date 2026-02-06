"""
Unit Tests for Advanced Metrics Computation
============================================

Tests risk-weighted recall, conservatism index, ROI, P95 latency,
and hybrid model complementarity calculations.

Author: Senior ML Infrastructure Engineer
Date: 2026-02-05
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.advanced_metrics import (
    calculate_risk_weighted_recall,
    calculate_conservatism_index,
    calculate_p95_latency,
    calculate_roi_ratio,
    calculate_hybrid_complementarity,
    compute_advanced_metrics,
    CategoryPerformance,
    RISK_WEIGHTS
)


class TestRiskWeightedRecall(unittest.TestCase):
    """Test risk-weighted recall calculation."""
    
    def test_basic_calculation(self):
        """Test basic risk-weighted recall with mixed weights."""
        categories = [
            CategoryPerformance('gender_mismatch', total=10, detected=8, detection_rate=0.8, risk_weight=1),
            CategoryPerformance('surgical_history_contradiction', total=5, detected=2, detection_rate=0.4, risk_weight=3),
        ]
        
        # Expected: (1*8 + 3*2) / (1*10 + 3*5) = 14 / 25 = 0.56
        result = calculate_risk_weighted_recall(categories)
        self.assertAlmostEqual(result, 0.56, places=2)
    
    def test_all_detected(self):
        """Test when all issues are detected."""
        categories = [
            CategoryPerformance('upcoding', total=5, detected=5, detection_rate=1.0, risk_weight=2),
        ]
        
        result = calculate_risk_weighted_recall(categories)
        self.assertEqual(result, 1.0)
    
    def test_none_detected(self):
        """Test when no issues are detected."""
        categories = [
            CategoryPerformance('age_inappropriate', total=10, detected=0, detection_rate=0.0, risk_weight=1),
        ]
        
        result = calculate_risk_weighted_recall(categories)
        self.assertEqual(result, 0.0)
    
    def test_empty_input(self):
        """Test with empty category list."""
        result = calculate_risk_weighted_recall([])
        self.assertEqual(result, 0.0)
    
    def test_high_priority_categories(self):
        """Test that high-risk categories dominate the metric."""
        categories = [
            # Low-risk category with high performance
            CategoryPerformance('duplicate_charge', total=10, detected=10, detection_rate=1.0, risk_weight=1),
            # High-risk category with low performance
            CategoryPerformance('surgical_history_contradiction', total=10, detected=2, detection_rate=0.2, risk_weight=3),
        ]
        
        # Expected: (1*10 + 3*2) / (1*10 + 3*10) = 16 / 40 = 0.4
        result = calculate_risk_weighted_recall(categories)
        self.assertAlmostEqual(result, 0.4, places=2)
        
        # Verify it's lower than standard recall
        standard_recall = (10 + 2) / (10 + 10)  # 0.6
        self.assertLess(result, standard_recall)


class TestConservatismIndex(unittest.TestCase):
    """Test conservatism index calculation."""
    
    def test_extremely_conservative(self):
        """Test when all errors are false negatives (missed detections)."""
        result = calculate_conservatism_index(false_negatives=10, false_positives=0)
        self.assertEqual(result, 1.0)
    
    def test_extremely_aggressive(self):
        """Test when all errors are false positives (false alarms)."""
        result = calculate_conservatism_index(false_negatives=0, false_positives=10)
        self.assertEqual(result, 0.0)
    
    def test_balanced(self):
        """Test when errors are evenly split."""
        result = calculate_conservatism_index(false_negatives=5, false_positives=5)
        self.assertEqual(result, 0.5)
    
    def test_no_errors(self):
        """Test when there are no errors."""
        result = calculate_conservatism_index(false_negatives=0, false_positives=0)
        self.assertEqual(result, 0.5)  # Neutral
    
    def test_conservative_bias(self):
        """Test slightly conservative model."""
        result = calculate_conservatism_index(false_negatives=7, false_positives=3)
        self.assertEqual(result, 0.7)


class TestP95Latency(unittest.TestCase):
    """Test P95 latency calculation."""
    
    def test_basic_calculation(self):
        """Test P95 with typical distribution."""
        latencies = [100, 150, 200, 250, 300, 350, 400, 450, 500, 5000]
        result = calculate_p95_latency(latencies)
        
        # 95th percentile should be high due to outlier
        self.assertGreater(result, 500)
        self.assertLess(result, 5000)
    
    def test_uniform_distribution(self):
        """Test with uniform latencies."""
        latencies = [100] * 100
        result = calculate_p95_latency(latencies)
        self.assertEqual(result, 100.0)
    
    def test_empty_input(self):
        """Test with empty latency list."""
        result = calculate_p95_latency([])
        self.assertEqual(result, 0.0)
    
    def test_single_value(self):
        """Test with single latency value."""
        result = calculate_p95_latency([250])
        self.assertEqual(result, 250.0)


class TestROIRatio(unittest.TestCase):
    """Test ROI ratio calculation."""
    
    def test_basic_calculation(self):
        """Test ROI with typical values."""
        roi_ratio, inference_cost = calculate_roi_ratio(
            total_potential_savings=1000.0,
            avg_latency_ms=500.0,
            cost_per_second=0.0005
        )
        
        # Expected inference cost: 0.5 seconds * $0.0005 = $0.00025
        self.assertAlmostEqual(inference_cost, 0.00025, places=5)
        
        # Expected ROI: $1000 / $0.00025 = 4,000,000
        self.assertAlmostEqual(roi_ratio, 4000000.0, places=0)
    
    def test_high_latency_lower_roi(self):
        """Test that higher latency reduces ROI."""
        roi_low_latency, cost_low = calculate_roi_ratio(
            total_potential_savings=1000.0,
            avg_latency_ms=100.0
        )
        
        roi_high_latency, cost_high = calculate_roi_ratio(
            total_potential_savings=1000.0,
            avg_latency_ms=1000.0
        )
        
        self.assertLess(roi_high_latency, roi_low_latency)
        self.assertGreater(cost_high, cost_low)
    
    def test_zero_latency(self):
        """Test with zero latency."""
        roi_ratio, inference_cost = calculate_roi_ratio(
            total_potential_savings=1000.0,
            avg_latency_ms=0.0
        )
        
        self.assertEqual(roi_ratio, 0.0)
        self.assertEqual(inference_cost, 0.0)
    
    def test_expensive_model(self):
        """Test with expensive model (higher cost per second)."""
        roi_cheap, cost_cheap = calculate_roi_ratio(
            total_potential_savings=1000.0,
            avg_latency_ms=500.0,
            cost_per_second=0.0001  # Cheap model
        )
        
        roi_expensive, cost_expensive = calculate_roi_ratio(
            total_potential_savings=1000.0,
            avg_latency_ms=500.0,
            cost_per_second=0.001  # Expensive model
        )
        
        self.assertLess(roi_expensive, roi_cheap)
        self.assertGreater(cost_expensive, cost_cheap)


class TestHybridComplementarity(unittest.TestCase):
    """Test hybrid model complementarity calculation."""
    
    def test_no_overlap(self):
        """Test when models detect completely different issues."""
        model_a = {1, 2, 3}
        model_b = {4, 5, 6}
        
        unique_a, unique_b, overlap, gain = calculate_hybrid_complementarity(
            model_a, model_b,
            model_a_recall=0.3,
            model_b_recall=0.3,
            total_issues=10
        )
        
        self.assertEqual(unique_a, 3)
        self.assertEqual(unique_b, 3)
        self.assertEqual(overlap, 0)
        self.assertGreater(gain, 0)  # Should have positive complementarity
    
    def test_complete_overlap(self):
        """Test when models detect identical issues."""
        model_a = {1, 2, 3}
        model_b = {1, 2, 3}
        
        unique_a, unique_b, overlap, gain = calculate_hybrid_complementarity(
            model_a, model_b,
            model_a_recall=0.3,
            model_b_recall=0.3,
            total_issues=10
        )
        
        self.assertEqual(unique_a, 0)
        self.assertEqual(unique_b, 0)
        self.assertEqual(overlap, 3)
        self.assertEqual(gain, 0.0)  # No complementarity
    
    def test_partial_overlap(self):
        """Test with partial overlap between models."""
        model_a = {1, 2, 3, 4}
        model_b = {3, 4, 5, 6}
        
        unique_a, unique_b, overlap, gain = calculate_hybrid_complementarity(
            model_a, model_b,
            model_a_recall=0.4,
            model_b_recall=0.4,
            total_issues=10
        )
        
        self.assertEqual(unique_a, 2)  # {1, 2}
        self.assertEqual(unique_b, 2)  # {5, 6}
        self.assertEqual(overlap, 2)    # {3, 4}


class TestAdvancedMetricsIntegration(unittest.TestCase):
    """Test complete advanced metrics computation."""
    
    def setUp(self):
        """Set up test data."""
        self.patient_results = [
            {'true_positives': 2, 'false_positives': 1, 'false_negatives': 0, 'latency_ms': 500},
            {'true_positives': 1, 'false_positives': 0, 'false_negatives': 2, 'latency_ms': 600},
            {'true_positives': 3, 'false_positives': 2, 'false_negatives': 1, 'latency_ms': 1500},
        ]
        
        self.error_type_performance = {
            'gender_mismatch': {'total': 10, 'detected': 8, 'detection_rate': 0.8},
            'surgical_history_contradiction': {'total': 5, 'detected': 2, 'detection_rate': 0.4},
            'duplicate_charge': {'total': 3, 'detected': 3, 'detection_rate': 1.0},
        }
    
    def test_compute_all_metrics(self):
        """Test that all metrics are computed successfully."""
        metrics = compute_advanced_metrics(
            patient_results=self.patient_results,
            error_type_performance=self.error_type_performance,
            total_potential_savings=5000.0
        )
        
        # Verify all required fields are present
        self.assertIsNotNone(metrics.risk_weighted_recall)
        self.assertIsNotNone(metrics.conservatism_index)
        self.assertIsNotNone(metrics.p95_latency_ms)
        self.assertIsNotNone(metrics.roi_ratio)
        self.assertIsNotNone(metrics.inference_cost_usd)
        
        # Verify confusion matrix
        self.assertEqual(metrics.true_positives, 6)
        self.assertEqual(metrics.false_positives, 3)
        self.assertEqual(metrics.false_negatives, 3)
    
    def test_metrics_in_valid_ranges(self):
        """Test that computed metrics are in valid ranges."""
        metrics = compute_advanced_metrics(
            patient_results=self.patient_results,
            error_type_performance=self.error_type_performance,
            total_potential_savings=5000.0
        )
        
        # Risk-weighted recall should be 0-1
        self.assertGreaterEqual(metrics.risk_weighted_recall, 0.0)
        self.assertLessEqual(metrics.risk_weighted_recall, 1.0)
        
        # Conservatism index should be 0-1
        self.assertGreaterEqual(metrics.conservatism_index, 0.0)
        self.assertLessEqual(metrics.conservatism_index, 1.0)
        
        # P95 latency should be positive
        self.assertGreaterEqual(metrics.p95_latency_ms, 0.0)
        
        # ROI should be positive
        self.assertGreaterEqual(metrics.roi_ratio, 0.0)
    
    def test_backward_compatibility(self):
        """Test that metrics computation works with minimal input."""
        minimal_results = [
            {'true_positives': 1, 'false_positives': 0, 'false_negatives': 1, 'latency_ms': 100}
        ]
        
        minimal_performance = {
            'gender_mismatch': {'total': 2, 'detected': 1, 'detection_rate': 0.5}
        }
        
        metrics = compute_advanced_metrics(
            patient_results=minimal_results,
            error_type_performance=minimal_performance
        )
        
        # Should complete without errors
        self.assertIsNotNone(metrics)


class TestRiskWeights(unittest.TestCase):
    """Test that risk weights are properly configured."""
    
    def test_critical_categories_have_high_weights(self):
        """Test that critical error categories have weight of 3."""
        critical_categories = [
            'surgical_history_contradiction',
            'diagnosis_procedure_mismatch'
        ]
        
        for category in critical_categories:
            self.assertEqual(RISK_WEIGHTS[category], 3)
    
    def test_high_impact_categories_have_medium_weights(self):
        """Test that high-impact categories have weight of 2."""
        high_impact_categories = [
            'medical_necessity',
            'upcoding'
        ]
        
        for category in high_impact_categories:
            self.assertEqual(RISK_WEIGHTS[category], 2)
    
    def test_standard_categories_have_default_weight(self):
        """Test that standard categories have weight of 1."""
        standard_categories = [
            'duplicate_charge',
            'gender_mismatch',
            'age_inappropriate'
        ]
        
        for category in standard_categories:
            self.assertEqual(RISK_WEIGHTS[category], 1)


if __name__ == '__main__':
    unittest.main()
