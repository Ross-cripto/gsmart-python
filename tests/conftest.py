"""Pytest configuration and fixtures."""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    # Create temporary config directory for tests
    with tempfile.TemporaryDirectory(prefix="gsmart-tests-") as temp_dir:
        original_config_dir = os.environ.get("GSMART_CONFIG_DIR")
        os.environ["GSMART_CONFIG_DIR"] = temp_dir

        yield temp_dir

        # Restore original config dir
        if original_config_dir:
            os.environ["GSMART_CONFIG_DIR"] = original_config_dir
        else:
            os.environ.pop("GSMART_CONFIG_DIR", None)


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository for testing."""
    import subprocess

    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init", "-b", "main"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=repo_path, check=True)

    # Change to repo directory
    original_cwd = os.getcwd()
    os.chdir(repo_path)

    yield repo_path

    # Restore original directory
    os.chdir(original_cwd)
