"""Tests for configuration management."""

import os
import tempfile
from pathlib import Path

import pytest


def test_set_get_clear_key():
    """Test setting, getting, and clearing API keys."""
    # Create isolated config for this test
    with tempfile.TemporaryDirectory(prefix="gsmart-config-") as config_dir:
        previous_dir = os.environ.get("GSMART_CONFIG_DIR")
        os.environ["GSMART_CONFIG_DIR"] = config_dir

        # Import config after setting env var
        from utils.config import Config

        config = Config()

        try:
            # Set key
            config.set_key("openai", "test-api-key-123")

            # Get key
            assert config.get_key("openai") == "test-api-key-123"

            # Get all keys
            all_keys = config.get_all_keys()
            assert all_keys["openai"] == "test-api-key-123"

            # Clear specific key
            config.clear_key("openai")
            assert config.get_key("openai") == ""

            # Set multiple keys
            config.set_key("openai", "key1")
            config.set_key("anthropic", "key2")
            all_keys = config.get_all_keys()
            assert all_keys["openai"] == "key1"
            assert all_keys["anthropic"] == "key2"

            # Clear all
            config.clear()
            assert config.get_key("openai") == ""
            assert config.get_key("anthropic") == ""

        finally:
            # Restore env
            if previous_dir:
                os.environ["GSMART_CONFIG_DIR"] = previous_dir
            else:
                os.environ.pop("GSMART_CONFIG_DIR", None)


def test_config_file_creation():
    """Test that config file is created in correct location."""
    with tempfile.TemporaryDirectory(prefix="gsmart-config-") as config_dir:
        os.environ["GSMART_CONFIG_DIR"] = config_dir

        from utils.config import Config

        config = Config()

        config.set_key("openai", "test")

        # Check that config file exists
        config_file = Path(config_dir) / "config.ini"
        assert config_file.exists()


def test_config_persistence():
    """Test that configuration persists across instances."""
    with tempfile.TemporaryDirectory(prefix="gsmart-config-") as config_dir:
        os.environ["GSMART_CONFIG_DIR"] = config_dir

        # First instance
        from utils.config import Config

        config1 = Config()
        config1.set_key("openai", "persistent-key")

        # Second instance (should load from file)
        config2 = Config()
        assert config2.get_key("openai") == "persistent-key"


def test_config_handles_missing_key():
    """Test that getting non-existent key returns empty string."""
    with tempfile.TemporaryDirectory(prefix="gsmart-config-") as config_dir:
        os.environ["GSMART_CONFIG_DIR"] = config_dir

        from utils.config import Config

        config = Config()

        assert config.get_key("nonexistent") == ""


def test_config_get_all_keys_empty():
    """Test getting all keys when none are set."""
    with tempfile.TemporaryDirectory(prefix="gsmart-config-") as config_dir:
        os.environ["GSMART_CONFIG_DIR"] = config_dir

        from utils.config import Config

        config = Config()

        all_keys = config.get_all_keys()
        assert isinstance(all_keys, dict)
        # Should have no keys set
        assert all(not value for value in all_keys.values())
