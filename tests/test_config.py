"""Tests for configuration management (_modules/utils/config.py).

Tests verify:
- Default configuration loading
- YAML file loading and merging
- Deep merge logic
- Dot-notation path retrieval
- Feature flag checks
- Error handling for missing/invalid config files
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
import yaml
from _modules.utils.config import (
    AppConfig,
    get_config,
    reload_config,
    is_assistant_enabled,
    is_dag_enabled,
    is_debug_enabled,
    is_privacy_ui_enabled,
    is_coverage_matrix_enabled,
)


class TestAppConfig:
    """Test AppConfig class behavior."""
    
    def test_default_config_structure(self):
        """Verify DEFAULT_CONFIG contains all required top-level keys."""
        expected_keys = {
            "features", "ui", "demo", "ai_providers", "limits", "developer"
        }
        assert set(AppConfig.DEFAULT_CONFIG.keys()) == expected_keys
    
    def test_default_config_features(self):
        """Verify default feature flags are set correctly."""
        config = AppConfig.DEFAULT_CONFIG
        
        # Check feature structure
        assert "assistant" in config["features"]
        assert "dag" in config["features"]
        assert "debug" in config["features"]
        
        # Check default values
        assert config["features"]["assistant"]["enabled"] is True
        assert config["features"]["dag"]["enabled"] is True
        assert config["features"]["debug"]["enabled"] is False
    
    def test_init_with_missing_file(self, tmp_path):
        """When config file doesn't exist, should use defaults."""
        missing_file = tmp_path / "nonexistent.yaml"
        
        with patch('builtins.print') as mock_print:
            config = AppConfig(config_path=missing_file)
        
        # Should print warning
        mock_print.assert_called_once()
        assert "Config file not found" in str(mock_print.call_args)
        
        # Should use defaults
        assert config.config == AppConfig.DEFAULT_CONFIG
    
    def test_init_with_valid_yaml_file(self, tmp_path):
        """When valid YAML exists, should load and merge with defaults."""
        config_file = tmp_path / "test_config.yaml"
        
        # Create minimal config that overrides some defaults
        test_config = {
            "features": {
                "assistant": {
                    "enabled": False,
                    "default_provider": "gemini"
                }
            },
            "ui": {
                "page_title": "Custom Title"
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(test_config, f)
        
        config = AppConfig(config_path=config_file)
        
        # Should merge: overrides take precedence
        assert config.config["features"]["assistant"]["enabled"] is False
        assert config.config["features"]["assistant"]["default_provider"] == "gemini"
        assert config.config["ui"]["page_title"] == "Custom Title"
        
        # Should keep defaults for unspecified values
        assert config.config["features"]["dag"]["enabled"] is True
        assert config.config["ui"]["layout"] == "wide"
    
    def test_init_with_invalid_yaml(self, tmp_path):
        """When YAML is malformed, should fall back to defaults."""
        config_file = tmp_path / "invalid.yaml"
        
        # Create invalid YAML
        with open(config_file, 'w') as f:
            f.write("invalid: yaml: content: [[[")
        
        with patch('builtins.print') as mock_print:
            config = AppConfig(config_path=config_file)
        
        # Should print error
        mock_print.assert_called_once()
        assert "Error loading config file" in str(mock_print.call_args)
        
        # Should use defaults
        assert config.config == AppConfig.DEFAULT_CONFIG
    
    def test_init_with_empty_yaml(self, tmp_path):
        """When YAML is empty, should use defaults."""
        config_file = tmp_path / "empty.yaml"
        
        # Create empty file
        with open(config_file, 'w') as f:
            f.write("")
        
        config = AppConfig(config_path=config_file)
        
        # Should use defaults
        assert config.config == AppConfig.DEFAULT_CONFIG
    
    def test_deep_merge_simple(self):
        """Deep merge should handle simple key-value pairs."""
        config = AppConfig.__new__(AppConfig)
        
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        
        result = config._deep_merge(base, override)
        
        assert result == {"a": 1, "b": 3, "c": 4}
    
    def test_deep_merge_nested_dicts(self):
        """Deep merge should recursively merge nested dictionaries."""
        config = AppConfig.__new__(AppConfig)
        
        base = {
            "features": {
                "assistant": {"enabled": True, "provider": "openai"},
                "dag": {"enabled": True}
            }
        }
        
        override = {
            "features": {
                "assistant": {"enabled": False},
                "debug": {"enabled": True}
            }
        }
        
        result = config._deep_merge(base, override)
        
        # Assistant.enabled overridden, provider preserved
        assert result["features"]["assistant"]["enabled"] is False
        assert result["features"]["assistant"]["provider"] == "openai"
        
        # DAG preserved from base
        assert result["features"]["dag"]["enabled"] is True
        
        # Debug added from override
        assert result["features"]["debug"]["enabled"] is True
    
    def test_deep_merge_override_with_non_dict(self):
        """When override value is not a dict, it should replace base value."""
        config = AppConfig.__new__(AppConfig)
        
        base = {"features": {"assistant": {"enabled": True}}}
        override = {"features": {"assistant": "disabled"}}
        
        result = config._deep_merge(base, override)
        
        # String should replace dict
        assert result["features"]["assistant"] == "disabled"
    
    def test_get_simple_key(self, tmp_path):
        """get() should retrieve top-level keys."""
        config_file = tmp_path / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({"custom_key": "custom_value"}, f)
        
        config = AppConfig(config_path=config_file)
        
        assert config.get("custom_key") == "custom_value"
    
    def test_get_nested_key_with_dot_notation(self):
        """get() should retrieve nested keys using dot notation."""
        config = AppConfig.__new__(AppConfig)
        config.config = {
            "features": {
                "assistant": {
                    "enabled": True,
                    "default_provider": "openai"
                }
            }
        }
        
        assert config.get("features.assistant.enabled") is True
        assert config.get("features.assistant.default_provider") == "openai"
    
    def test_get_missing_key_returns_default(self):
        """get() should return default when key doesn't exist."""
        config = AppConfig.__new__(AppConfig)
        config.config = {"features": {}}
        
        assert config.get("features.nonexistent") is None
        assert config.get("features.nonexistent", "default") == "default"
    
    def test_get_partial_path_returns_default(self):
        """get() should return default when path traversal fails."""
        config = AppConfig.__new__(AppConfig)
        config.config = {"features": {"assistant": "string_not_dict"}}
        
        # Can't traverse into string
        result = config.get("features.assistant.enabled", False)
        assert result is False
    
    def test_is_feature_enabled_true(self):
        """is_feature_enabled() should return True when feature enabled."""
        config = AppConfig.__new__(AppConfig)
        config.config = {
            "features": {
                "assistant": {"enabled": True}
            }
        }
        
        assert config.is_feature_enabled("assistant") is True
    
    def test_is_feature_enabled_false(self):
        """is_feature_enabled() should return False when feature disabled."""
        config = AppConfig.__new__(AppConfig)
        config.config = {
            "features": {
                "assistant": {"enabled": False}
            }
        }
        
        assert config.is_feature_enabled("assistant") is False
    
    def test_is_feature_enabled_missing_feature(self):
        """is_feature_enabled() should return False for missing features."""
        config = AppConfig.__new__(AppConfig)
        config.config = {"features": {}}
        
        assert config.is_feature_enabled("nonexistent") is False
    
    def test_reload_reloads_from_file(self, tmp_path):
        """reload() should re-read config file."""
        config_file = tmp_path / "config.yaml"
        
        # Initial config
        with open(config_file, 'w') as f:
            yaml.dump({"ui": {"page_title": "Initial"}}, f)
        
        config = AppConfig(config_path=config_file)
        assert config.get("ui.page_title") == "Initial"
        
        # Modify file
        with open(config_file, 'w') as f:
            yaml.dump({"ui": {"page_title": "Updated"}}, f)
        
        # Reload
        config.reload()
        assert config.get("ui.page_title") == "Updated"


class TestGlobalConfigFunctions:
    """Test module-level convenience functions."""
    
    def test_get_config_returns_singleton(self):
        """get_config() should return the same instance."""
        # Clear global instance
        import _modules.utils.config as config_module
        config_module._config_instance = None
        
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
    
    def test_reload_config_creates_new_instance(self):
        """reload_config() should create a fresh instance."""
        import _modules.utils.config as config_module
        
        config1 = get_config()
        config2 = reload_config()
        
        # Should be a new instance
        assert config1 is not config2
    
    def test_is_assistant_enabled_with_default_config(self):
        """is_assistant_enabled() should use global config instance."""
        import _modules.utils.config as config_module
        
        # Reset to defaults
        config_module._config_instance = None
        
        # Default has assistant enabled
        assert is_assistant_enabled() is True
    
    def test_is_dag_enabled_with_default_config(self):
        """is_dag_enabled() should use global config instance."""
        import _modules.utils.config as config_module
        config_module._config_instance = None
        
        assert is_dag_enabled() is True
    
    def test_is_debug_enabled_with_default_config(self):
        """is_debug_enabled() should use global config instance."""
        import _modules.utils.config as config_module
        config_module._config_instance = None
        
        # Default has debug disabled
        assert is_debug_enabled() is False
    
    def test_is_privacy_ui_enabled_with_default_config(self):
        """is_privacy_ui_enabled() should use global config instance."""
        import _modules.utils.config as config_module
        config_module._config_instance = None
        
        assert is_privacy_ui_enabled() is True
    
    def test_is_coverage_matrix_enabled_with_default_config(self):
        """is_coverage_matrix_enabled() should use global config instance."""
        import _modules.utils.config as config_module
        config_module._config_instance = None
        
        assert is_coverage_matrix_enabled() is True


class TestConfigEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_config_with_null_values(self, tmp_path):
        """Config should handle null/None values in YAML."""
        config_file = tmp_path / "config.yaml"
        
        with open(config_file, 'w') as f:
            f.write("features:\n  assistant:\n    enabled: null\n")
        
        config = AppConfig(config_path=config_file)
        
        # Null should override default
        assert config.get("features.assistant.enabled") is None
    
    def test_config_with_list_values(self, tmp_path):
        """Config should preserve list values."""
        config_file = tmp_path / "config.yaml"
        
        test_config = {
            "demo": {
                "available_demos": ["demo1.html", "demo2.html"]
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(test_config, f)
        
        config = AppConfig(config_path=config_file)
        
        demos = config.get("demo.available_demos")
        assert isinstance(demos, list)
        assert len(demos) == 2
        assert "demo1.html" in demos
    
    def test_get_with_empty_key_path(self):
        """get() with empty string should return config root."""
        config = AppConfig.__new__(AppConfig)
        config.config = {"test": "value"}
        
        # Empty path returns None (no valid traversal)
        result = config.get("")
        assert result is None
    
    def test_deep_merge_does_not_mutate_inputs(self):
        """_deep_merge should not modify original dictionaries."""
        config = AppConfig.__new__(AppConfig)
        
        base = {"a": {"b": 1}}
        override = {"a": {"c": 2}}
        
        base_copy = {"a": {"b": 1}}
        override_copy = {"a": {"c": 2}}
        
        result = config._deep_merge(base, override)
        
        # Originals unchanged
        assert base == base_copy
        assert override == override_copy
        
        # Result has merged values
        assert result == {"a": {"b": 1, "c": 2}}
