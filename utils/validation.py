"""Input validation utilities."""

import logging
from typing import Optional

from constants import DEFAULT_MAX_TOKENS, CHARS_PER_TOKEN, MIN_CHANGES_LENGTH

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


def validate_changes(changes: str, max_tokens: Optional[int] = None) -> bool:
    """
    Validate that changes are within acceptable limits.

    Args:
        changes: Git diff changes to validate
        max_tokens: Maximum number of tokens allowed (default: DEFAULT_MAX_TOKENS)

    Returns:
        True if validation passes

    Raises:
        ValidationError: If validation fails
    """
    max_tokens = max_tokens or DEFAULT_MAX_TOKENS

    # Check if changes are empty
    if not changes or not changes.strip():
        logger.error("Validation failed: No changes provided")
        raise ValidationError("No changes to commit. Please stage some changes first.")

    # Check minimum length
    if len(changes.strip()) < MIN_CHANGES_LENGTH:
        logger.error(f"Validation failed: Changes too short ({len(changes)} chars)")
        raise ValidationError(
            f"Changes are too short ({len(changes)} characters). "
            f"Please make more substantial changes."
        )

    # Estimate token count
    estimated_tokens = len(changes) / CHARS_PER_TOKEN

    if estimated_tokens > max_tokens:
        logger.error(
            f"Validation failed: Changes too large ({estimated_tokens:.0f} tokens, "
            f"max: {max_tokens})"
        )
        raise ValidationError(
            f"Changes are too large (approximately {estimated_tokens:.0f} tokens). "
            f"Maximum allowed: {max_tokens} tokens.\n"
            f"Please commit in smaller chunks or increase the token limit."
        )

    logger.debug(
        f"Validation passed: {len(changes)} characters, "
        f"~{estimated_tokens:.0f} tokens (max: {max_tokens})"
    )

    return True


def get_token_estimate(text: str) -> int:
    """
    Estimate the number of tokens in a text.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated number of tokens
    """
    return int(len(text) / CHARS_PER_TOKEN)
