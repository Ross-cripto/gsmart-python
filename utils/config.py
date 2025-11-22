"""Configuration manager for API keys and settings."""

import os
from pathlib import Path
from typing import Dict, Optional
import configparser

import keyring

from utils.providers import ProviderType, PROVIDERS


class Config:
    """Manages application configuration."""

    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = self._resolve_config_directory()
        self.config_file = self.config_dir / "config.ini"
        self.config = configparser.ConfigParser()

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load existing configuration
        if self.config_file.exists():
            self.config.read(self.config_file)

    def _resolve_config_directory(self) -> Path:
        """Resolve the configuration directory."""
        # Check for environment variable override
        override = os.getenv("GSMART_CONFIG_DIR")
        if override:
            return Path(override)

        # Use default XDG config directory or user home
        xdg_config = os.getenv("XDG_CONFIG_HOME")
        if xdg_config:
            return Path(xdg_config) / "gsmart"

        return Path.home() / ".config" / "gsmart"

    def _save(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, "w") as f:
            self.config.write(f)

    def set_key(self, provider: ProviderType, key: str) -> None:
        """
        Set API key for a provider.

        Args:
            provider: Provider name
            key: API key
        """
        if not self.config.has_section(provider):
            self.config.add_section(provider)

        self.config.set(provider, "key", key)
        self._save()

    def get_key(self, provider: ProviderType) -> str:
        """
        Get API key for a provider.

        Args:
            provider: Provider name

        Returns:
            API key or empty string if not found
        """
        try:
            return self.config.get(provider, "key")
        except (configparser.NoSectionError, configparser.NoOptionError):
            return ""

    def clear_key(self, provider: ProviderType) -> None:
        """
        Clear API key for a provider.

        Args:
            provider: Provider name
        """
        try:
            keyring.delete_password("gsmart", provider)
        except keyring.errors.PasswordDeleteError:
            # Key doesn't exist, that's fine
            pass

    def get_all_keys(self) -> Dict[str, str]:
        """
        Get all API keys.

        Returns:
            Dictionary of provider names to API keys
        """
        keys: Dict[str, str] = {}
        for provider in PROVIDERS:
            key = self.get_key(provider.value)
            if key:
                keys[provider.value] = key
        return keys

    def clear(self) -> None:
        """Clear all configuration."""
        # Clear all API keys from keyring
        for provider in PROVIDERS:
            self.clear_key(provider.value)

        # Clear config file
        if self.config_file.exists():
            self.config_file.unlink()
        self.config = configparser.ConfigParser()


# Singleton instance
config = Config()
