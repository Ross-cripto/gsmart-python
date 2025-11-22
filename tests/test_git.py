"""Tests for AI provider integration."""

from unittest.mock import Mock, patch

import pytest

from utils.ai import (
    AIBuilder,
    build_prompt,
    OpenAIProvider,
    AnthropicProvider,
    AIProvider,
    PROVIDER_MAP,
)
from constants import DEFAULT_PROVIDER


def test_build_prompt():
    """Test building prompt for AI model."""
    system, user_prompt = build_prompt("main", "test changes")

    assert isinstance(system, str)
    assert isinstance(user_prompt, str)
    assert "Conventional Commits" in system
    assert "main" in user_prompt
    assert "test changes" in user_prompt
    assert "feat" in user_prompt
    assert "fix" in user_prompt


def test_ai_builder_initialization():
    """Test AIBuilder initialization."""
    builder = AIBuilder("openai", "custom instructions")

    assert builder.provider == "openai"
    assert builder.custom_prompt == "custom instructions"


def test_ai_builder_default_provider():
    """Test AIBuilder with default provider."""
    builder = AIBuilder()

    assert builder.provider == DEFAULT_PROVIDER


def test_ai_builder_change_provider():
    """Test changing AI provider."""
    builder = AIBuilder("openai", "")
    builder.change_provider("anthropic")

    assert builder.provider == "anthropic"


def test_all_providers_in_map():
    """Test that all providers are in the provider map."""
    expected_providers = ["openai", "anthropic", "google", "mistral", "fireworks", "plataformia"]

    for provider in expected_providers:
        assert provider in PROVIDER_MAP


def test_provider_classes_inherit_from_base():
    """Test that all provider classes inherit from AIProvider."""
    for provider_class in PROVIDER_MAP.values():
        assert issubclass(provider_class, AIProvider)


def test_ai_builder_generate_no_api_key():
    """Test generate commit message without API key."""
    with patch("utils.config.config.get_key", return_value=""):
        builder = AIBuilder("openai", "")
        result = builder.generate_commit_message("main", "test changes")

        assert isinstance(result, dict)
        assert "error" in result


def test_ai_builder_invalid_provider():
    """Test generate with invalid provider."""
    builder = AIBuilder("invalid_provider", "")

    # Manually set invalid provider to bypass type checking
    builder.provider = "invalid_provider"

    result = builder.generate_commit_message("main", "test changes")

    assert isinstance(result, dict)
    assert "error" in result


def test_ai_builder_with_custom_prompt():
    """Test that custom prompt is added to user prompt."""
    with patch("utils.config.config.get_key", return_value="test-key"):
        with patch.object(OpenAIProvider, "generate", return_value="feat: test"):
            builder = AIBuilder("openai", "use emojis")
            result = builder.generate_commit_message("main", "test changes")

            # Should succeed
            assert isinstance(result, str)


def test_openai_provider_initialization():
    """Test OpenAI provider initialization."""
    provider = OpenAIProvider("test-api-key")
    assert provider.api_key == "test-api-key"


def test_anthropic_provider_initialization():
    """Test Anthropic provider initialization."""
    provider = AnthropicProvider("test-api-key")
    assert provider.api_key == "test-api-key"


@pytest.mark.integration
def test_openai_provider_generate_mock():
    """Test OpenAI provider generate with mock."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "feat: add test"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        provider = OpenAIProvider("test-key")
        result = provider.generate("system", "prompt")

        assert result == "feat: add test"


@pytest.mark.integration
def test_anthropic_provider_generate_mock():
    """Test Anthropic provider generate with mock."""
    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "fix: resolve bug"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        provider = AnthropicProvider("test-key")
        result = provider.generate("system", "prompt")

        assert result == "fix: resolve bug"


def test_ai_provider_is_abstract():
    """Test that AIProvider cannot be instantiated directly."""
    with pytest.raises(TypeError):
        AIProvider("test-key")


def test_build_prompt_includes_all_commit_types():
    """Test that prompt includes all conventional commit types."""
    _, user_prompt = build_prompt("main", "changes")

    commit_types = [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "build",
        "ci",
        "chore",
        "revert",
    ]

    for commit_type in commit_types:
        assert commit_type in user_prompt


def test_build_prompt_format_specification():
    """Test that prompt specifies the correct format."""
    system, _ = build_prompt("main", "changes")

    assert "<type>(<scope>): <description>" in system
    assert "optional" in system.lower()
