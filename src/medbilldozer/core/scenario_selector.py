"""
Scenario Selector for MedBillDozer Challenge
Intelligently selects scenarios with weighted randomization and anti-repetition
"""

import random
from typing import List, Optional
from pathlib import Path
from medbilldozer.data.challenge_scenarios import ChallengeScenario, load_all_scenarios


class ScenarioSelector:
    """Intelligent scenario selection with anti-repetition"""

    # Category weights for random selection
    CATEGORY_WEIGHTS = {
        "billing_only": 0.40,
        "clinical_validation": 0.25,
        "combined": 0.20,
        "clean_case": 0.10,
        "malpractice": 0.05
    }

    def __init__(self, data_source: str = "json", scenarios_dir: Optional[Path] = None):
        """
        Initialize scenario selector

        Args:
            data_source: "json" or "supabase"
            scenarios_dir: Path to scenarios directory (for JSON source)
        """
        self.data_source = data_source
        self.scenarios_dir = scenarios_dir
        self.scenarios_cache: List[ChallengeScenario] = []
        self.played_scenarios: List[str] = []  # Session history of scenario IDs

        # Load scenarios on initialization
        if data_source == "json" and scenarios_dir:
            self._load_scenarios_from_json()

    def _load_scenarios_from_json(self):
        """Load all scenarios from JSON files"""
        if self.scenarios_dir and self.scenarios_dir.exists():
            self.scenarios_cache = load_all_scenarios(self.scenarios_dir)
            print(f"Loaded {len(self.scenarios_cache)} scenarios from {self.scenarios_dir}")
        else:
            print(f"Warning: Scenarios directory {self.scenarios_dir} not found")

    def _load_scenarios_from_supabase(self):
        """Load scenarios from Supabase (placeholder for future implementation)"""
        # TODO: Implement Supabase loading
        raise NotImplementedError("Supabase loading not yet implemented")

    def select_scenario(
        self,
        difficulty: Optional[str] = None,
        category: Optional[str] = None,
        avoid_recent: int = 5
    ) -> Optional[ChallengeScenario]:
        """
        Select next scenario with intelligent weighting

        Args:
            difficulty: Filter by difficulty (easy, medium, hard, expert)
            category: Filter by category
            avoid_recent: Don't repeat last N scenarios

        Returns:
            Selected ChallengeScenario or None if no scenarios available
        """
        available = self._get_available_scenarios(difficulty, category)

        if not available:
            print("Warning: No scenarios available")
            return None

        # Filter out recently played scenarios
        if len(self.played_scenarios) > 0:
            recent_ids = set(self.played_scenarios[-avoid_recent:])
            available = [s for s in available if s.scenario_id not in recent_ids]

        # If all scenarios were recently played, allow repeats
        if not available:
            print(f"All scenarios played recently, allowing repeats")
            available = self._get_available_scenarios(difficulty, category)

        # Weighted random selection
        weights = self._calculate_weights(available)
        selected = random.choices(available, weights=weights, k=1)[0]

        # Track played scenario
        self.played_scenarios.append(selected.scenario_id)

        return selected

    def _get_available_scenarios(
        self,
        difficulty: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[ChallengeScenario]:
        """Get filtered list of available scenarios"""
        available = self.scenarios_cache.copy()

        # Apply difficulty filter
        if difficulty:
            available = [s for s in available if s.difficulty == difficulty]

        # Apply category filter
        if category:
            available = [s for s in available if s.category == category]

        return available

    def _calculate_weights(self, scenarios: List[ChallengeScenario]) -> List[float]:
        """
        Calculate selection weights based on category distribution

        Weighting strategy:
        - 40% billing errors
        - 25% clinical validation
        - 20% combined (billing + clinical)
        - 10% clean cases (no errors)
        - 5% malpractice cases
        """
        weights = []
        for scenario in scenarios:
            weight = self.CATEGORY_WEIGHTS.get(scenario.category, 0.10)
            weights.append(weight)
        return weights

    def get_scenario_by_id(self, scenario_id: str) -> Optional[ChallengeScenario]:
        """Get specific scenario by ID"""
        for scenario in self.scenarios_cache:
            if scenario.scenario_id == scenario_id:
                return scenario
        return None

    def get_statistics(self) -> dict:
        """Get statistics about available scenarios"""
        stats = {
            "total": len(self.scenarios_cache),
            "by_category": {},
            "by_difficulty": {},
            "played_count": len(self.played_scenarios)
        }

        for scenario in self.scenarios_cache:
            # Count by category
            stats["by_category"][scenario.category] = stats["by_category"].get(scenario.category, 0) + 1

            # Count by difficulty
            stats["by_difficulty"][scenario.difficulty] = stats["by_difficulty"].get(scenario.difficulty, 0) + 1

        return stats

    def reset_history(self):
        """Reset played scenarios history"""
        self.played_scenarios = []

    def reload_scenarios(self):
        """Reload scenarios from source"""
        if self.data_source == "json":
            self._load_scenarios_from_json()
        elif self.data_source == "supabase":
            self._load_scenarios_from_supabase()
