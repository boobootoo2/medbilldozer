"""
Achievements and Scoring System for MedBillDozer Challenge
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Achievement:
    """Achievement definition"""
    id: str
    name: str
    description: str
    icon: str
    points: int
    category: str  # gameplay, accuracy, speed, expertise


class AchievementTracker:
    """Track and award player achievements"""

    ACHIEVEMENTS = {
        "first_victory": Achievement(
            id="first_victory",
            name="First Victory",
            description="Complete your first challenge",
            icon="🏆",
            points=100,
            category="gameplay"
        ),
        "eagle_eye": Achievement(
            id="eagle_eye",
            name="Eagle Eye",
            description="Find all issues with 100% accuracy",
            icon="🦅",
            points=500,
            category="accuracy"
        ),
        "clean_sweep": Achievement(
            id="clean_sweep",
            name="Clean Sweep",
            description="Correctly identify a clean case (no false positives)",
            icon="✨",
            points=300,
            category="accuracy"
        ),
        "speed_demon": Achievement(
            id="speed_demon",
            name="Speed Demon",
            description="Complete a challenge in under 3 minutes",
            icon="⚡",
            points=200,
            category="speed"
        ),
        "malpractice_detective": Achievement(
            id="malpractice_detective",
            name="Malpractice Detective",
            description="Correctly identify a malpractice case",
            icon="🔍",
            points=1000,
            category="expertise"
        ),
        "radiologist": Achievement(
            id="radiologist",
            name="Radiologist",
            description="Correctly validate 10 imaging studies",
            icon="🩻",
            points=500,
            category="expertise"
        ),
        "perfect_streak": Achievement(
            id="perfect_streak",
            name="Perfect Streak",
            description="Complete 5 challenges in a row with 100% accuracy",
            icon="🔥",
            points=1500,
            category="accuracy"
        ),
        "billing_expert": Achievement(
            id="billing_expert",
            name="Billing Expert",
            description="Catch 50 billing errors across all challenges",
            icon="💰",
            points=800,
            category="expertise"
        ),
        "no_mistakes": Achievement(
            id="no_mistakes",
            name="No Mistakes",
            description="Complete 10 challenges with zero false positives",
            icon="💯",
            points=1000,
            category="accuracy"
        )
    }

    @staticmethod
    def check_achievements(session_stats: Dict, challenge_result: Dict) -> List[str]:
        """
        Check which achievements were earned

        Args:
            session_stats: Overall session statistics
            challenge_result: Current challenge results

        Returns:
            List of achievement IDs earned
        """
        earned = []

        # First Victory
        if session_stats.get("scenarios_completed", 0) == 1:
            earned.append("first_victory")

        # Eagle Eye - 100% accuracy
        if challenge_result.get("accuracy", 0) == 100.0:
            earned.append("eagle_eye")

        # Clean Sweep - clean case with no false positives
        if challenge_result.get("scenario_category") == "clean_case" and challenge_result.get("false_positives", 0) == 0:
            earned.append("clean_sweep")

        # Speed Demon - under 3 minutes (180 seconds)
        if challenge_result.get("completion_time", 999) < 180:
            earned.append("speed_demon")

        # Malpractice Detective
        if challenge_result.get("malpractice_identified", False):
            earned.append("malpractice_detective")

        # Radiologist - 10 imaging studies validated
        if session_stats.get("images_validated", 0) >= 10:
            earned.append("radiologist")

        # Perfect Streak - 5 consecutive 100% accuracy
        if session_stats.get("perfect_streak", 0) >= 5:
            earned.append("perfect_streak")

        # Billing Expert - 50 billing errors caught
        if session_stats.get("billing_errors_caught", 0) >= 50:
            earned.append("billing_expert")

        # No Mistakes - 10 challenges with zero false positives
        if session_stats.get("zero_fp_challenges", 0) >= 10:
            earned.append("no_mistakes")

        return earned

    @staticmethod
    def get_achievement(achievement_id: str) -> Optional[Achievement]:
        """Get achievement by ID"""
        return AchievementTracker.ACHIEVEMENTS.get(achievement_id)


class ScoringEngine:
    """Calculate scores for challenge completion"""

    # Point values
    POINTS_PER_ISSUE = 100
    FALSE_POSITIVE_PENALTY = -50
    CLEAN_CASE_BONUS = 500
    CLINICAL_VALIDATION_POINTS = 150

    # Difficulty multipliers
    DIFFICULTY_MULTIPLIERS = {
        "easy": 1.0,
        "medium": 1.5,
        "hard": 2.0,
        "expert": 3.0
    }

    # Accuracy bonus tiers
    ACCURACY_BONUSES = {
        100: 500,
        90: 300,
        80: 100
    }

    @staticmethod
    def calculate_score(
        issues_found: List[str],
        issues_expected: List[str],
        false_positives: int,
        clinical_validations_correct: int,
        clinical_validations_total: int,
        is_clean_case: bool,
        difficulty: str,
        completion_time: int,  # seconds
        time_bonus_threshold: int = 300  # 5 minutes
    ) -> Dict:
        """
        Calculate comprehensive score for challenge completion

        Args:
            issues_found: List of issue IDs found by player
            issues_expected: List of expected issue IDs
            false_positives: Number of false positive issues flagged
            clinical_validations_correct: Number of correct clinical validations
            clinical_validations_total: Total clinical validations
            is_clean_case: Whether this is a clean case scenario
            difficulty: Difficulty level
            completion_time: Time taken in seconds
            time_bonus_threshold: Threshold for speed bonus

        Returns:
            Dictionary with score breakdown
        """
        # Calculate base score
        correct_issues = len(set(issues_found) & set(issues_expected))
        base_score = correct_issues * ScoringEngine.POINTS_PER_ISSUE

        # False positive penalty
        fp_penalty = false_positives * ScoringEngine.FALSE_POSITIVE_PENALTY

        # Clinical validation points
        clinical_points = clinical_validations_correct * ScoringEngine.CLINICAL_VALIDATION_POINTS

        # Clean case bonus
        clean_bonus = 0
        if is_clean_case and false_positives == 0:
            clean_bonus = ScoringEngine.CLEAN_CASE_BONUS
        elif is_clean_case and false_positives <= 2:
            clean_bonus = 200

        # Calculate accuracy
        total_expected = len(issues_expected) if issues_expected else 1
        true_positives = correct_issues
        false_negatives = len(issues_expected) - correct_issues

        if is_clean_case:
            # For clean cases, accuracy is based on avoiding false positives
            accuracy = 100.0 if false_positives == 0 else max(0, 100 - (false_positives * 25))
        else:
            # For regular cases, accuracy is based on finding issues correctly
            accuracy = (true_positives / total_expected * 100) if total_expected > 0 else 0
            # Penalize for false positives
            if false_positives > 0:
                accuracy = max(0, accuracy - (false_positives * 10))

        # Accuracy bonus
        accuracy_bonus = 0
        for threshold, bonus in sorted(ScoringEngine.ACCURACY_BONUSES.items(), reverse=True):
            if accuracy >= threshold:
                accuracy_bonus = bonus
                break

        # Speed bonus
        speed_bonus = 0
        if completion_time < time_bonus_threshold:
            # Linear scale: 50 points at 0 seconds, 0 points at threshold
            speed_bonus = int(50 * (1 - completion_time / time_bonus_threshold))

        # Calculate subtotal before multiplier
        subtotal = base_score + fp_penalty + clinical_points + clean_bonus + accuracy_bonus + speed_bonus

        # Apply difficulty multiplier
        difficulty_multiplier = ScoringEngine.DIFFICULTY_MULTIPLIERS.get(difficulty, 1.0)
        final_score = int(subtotal * difficulty_multiplier)

        return {
            "final_score": max(0, final_score),  # Never negative
            "base_score": base_score,
            "fp_penalty": fp_penalty,
            "clinical_points": clinical_points,
            "clean_bonus": clean_bonus,
            "accuracy_bonus": accuracy_bonus,
            "speed_bonus": speed_bonus,
            "difficulty_multiplier": difficulty_multiplier,
            "accuracy": round(accuracy, 1),
            "correct_issues": correct_issues,
            "false_positives": false_positives,
            "false_negatives": false_negatives
        }

    @staticmethod
    def format_score_summary(score_breakdown: Dict, achievements: List[str]) -> str:
        """
        Format score breakdown as readable text

        Args:
            score_breakdown: Score calculation result
            achievements: List of achievement IDs earned

        Returns:
            Formatted summary string
        """
        summary = f"""**Score Breakdown:**

Base Score: {score_breakdown['base_score']} pts ({score_breakdown['correct_issues']} issues found)
False Positive Penalty: {score_breakdown['fp_penalty']} pts ({score_breakdown['false_positives']} FPs)
Clinical Validation: +{score_breakdown['clinical_points']} pts
Clean Case Bonus: +{score_breakdown['clean_bonus']} pts
Accuracy Bonus: +{score_breakdown['accuracy_bonus']} pts
Speed Bonus: +{score_breakdown['speed_bonus']} pts

Subtotal: {score_breakdown['base_score'] + score_breakdown['fp_penalty'] + score_breakdown['clinical_points'] + score_breakdown['clean_bonus'] + score_breakdown['accuracy_bonus'] + score_breakdown['speed_bonus']} pts
Difficulty Multiplier: {score_breakdown['difficulty_multiplier']}x

**Final Score: {score_breakdown['final_score']} points**
**Accuracy: {score_breakdown['accuracy']}%**
"""

        if achievements:
            summary += "\n**Achievements Unlocked:**\n"
            for achievement_id in achievements:
                ach = AchievementTracker.get_achievement(achievement_id)
                if ach:
                    summary += f"{ach.icon} **{ach.name}** - {ach.description} (+{ach.points} pts)\n"

        return summary
