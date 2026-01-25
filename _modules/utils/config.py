"""Application Configuration Manager.

Loads and provides access to application configuration from app_config.yaml.
Provides fallback defaults if config file is missing or incomplete.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class AppConfig:
    """Application configuration manager with fallback defaults."""

    # Default configuration (used if YAML file missing or incomplete)
    DEFAULT_CONFIG = {
        "features": {
            "assistant": {
                "enabled": True,
                "default_provider": "openai",
                "default_character": "billy"
            },
            "dag": {
                "enabled": True,
                "expanded_by_default": True,
                "show_comparison_table": True
            },
            "debug": {
                "enabled": False,
                "show_orchestration": True,
                "show_workflow_logs": True,
                "show_raw_analysis": True
            },
            "privacy_ui": {
                "enabled": True
            },
            "coverage_matrix": {
                "enabled": True
            },
            "guided_tour": {
                "enabled": True,
                "auto_launch_for_new_users": True,
                "default_narrator": "billie",
                "widget_position": "top",
                "show_skip_button": True
            }
        },
        "ui": {
            "page_title": "medBillDozer",
            "page_icon": "�",
            "layout": "wide",
            "sidebar": {
                "show_logo": True,
                "show_quick_help_buttons": True,
                "max_conversation_history": 3
            },
            "results": {
                "show_savings_estimate": True,
                "show_line_items": True,
                "show_detailed_facts": True,
                "expand_issues_by_default": True
            }
        },
        "demo": {
            "enabled": True,
            "available_demos": [
                "sample_colonoscopy_bill.html",
                "sample_dental_crown_bill.html",
                "sample_pharmacy_receipt_fsa.html",
                "sample_insurance_claim_history_zero_oop.html",
                "sample_fsa_claim_history.html"
            ]
        },
        "ai_providers": {
            "default_analysis_provider": "openai",
            "available_providers": ["openai", "gemini"],
            "models": {
                "openai": {
                    "analysis": "gpt-4o-mini",
                    "assistant": "gpt-4o-mini"
                },
                "gemini": {
                    "analysis": "gemini-2.0-flash-exp",
                    "assistant": "gemini-2.0-flash-exp"
                }
            }
        },
        "limits": {
            "max_documents_per_batch": 10,
            "max_document_size_chars": 100000,
            "analysis_timeout_seconds": 120
        },
        "developer": {
            "show_technical_errors": False,
            "enable_profiling": False,
            "log_level": "INFO"
        }
    }

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_path: Optional path to config file. Defaults to app_config.yaml in project root.
        """
        if config_path is None:
            # Default to app_config.yaml in project root
            config_path = Path(__file__).parent.parent.parent / "app_config.yaml"

        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file with fallback to defaults.

        Returns:
            Configuration dictionary
        """
        if not self.config_path.exists():
            print(f"⚠️  Config file not found at {self.config_path}, using defaults")
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f) or {}

            # Merge with defaults (defaults provide fallback for missing keys)
            config = self._deep_merge(self.DEFAULT_CONFIG.copy(), loaded_config)
            return config

        except Exception as e:
            print(f"⚠️  Error loading config file: {e}, using defaults")
            return self.DEFAULT_CONFIG.copy()

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries, with override taking precedence.

        Args:
            base: Base dictionary with default values
            override: Dictionary with override values

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation path.

        Examples:
            config.get("features.assistant.enabled")
            config.get("ui.page_title")
            config.get("features.debug.enabled", False)

        Args:
            key_path: Dot-separated path to configuration value
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled.

        Args:
            feature_name: Name of feature (e.g., "assistant", "dag", "debug")

        Returns:
            True if feature is enabled, False otherwise
        """
        return self.get(f"features.{feature_name}.enabled", False)

    def reload(self):
        """Reload configuration from file."""
        self.config = self._load_config()


# Global configuration instance
_config_instance: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance.

    Returns:
        AppConfig instance
    """
    global _config_instance

    if _config_instance is None:
        _config_instance = AppConfig()

    return _config_instance


def reload_config():
    """Reload the global configuration from file."""
    global _config_instance
    _config_instance = None
    return get_config()


# Convenience functions for common checks


def is_assistant_enabled() -> bool:
    """Check if documentation assistant feature is enabled."""
    return get_config().is_feature_enabled("assistant")


def is_dag_enabled() -> bool:
    """Check if pipeline DAG visualization is enabled."""
    return get_config().is_feature_enabled("dag")


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled."""
    return get_config().is_feature_enabled("debug")


def is_guided_tour_enabled() -> bool:
    """Check if guided tour feature is enabled."""
    return get_config().is_feature_enabled("guided_tour")


def is_privacy_ui_enabled() -> bool:
    """Check if privacy UI is enabled."""
    return get_config().is_feature_enabled("privacy_ui")


def is_coverage_matrix_enabled() -> bool:
    """Check if coverage matrix feature is enabled."""
    return get_config().is_feature_enabled("coverage_matrix")

