"""Application constants and configuration."""

from typing import Final

# Application metadata
APP_NAME: Final[str] = "gsmart"
APP_VERSION: Final[str] = "1.1.0"
APP_DESCRIPTION: Final[str] = "Git Smart - AI-powered commit message generator"

# Default provider
DEFAULT_PROVIDER: Final[str] = "openai"

# Configuration
UPDATE_CHECK_INTERVAL: Final[int] = 86400  # 24 hours in seconds

# Token limits and validation
DEFAULT_MAX_TOKENS: Final[int] = 8000  # Default maximum tokens for changes
CHARS_PER_TOKEN: Final[int] = 4  # Approximate characters per token
MIN_CHANGES_LENGTH: Final[int] = 10  # Minimum characters in changes

# Retry configuration
MAX_RETRIES: Final[int] = 3  # Maximum number of API retry attempts
RETRY_MIN_WAIT: Final[int] = 4  # Minimum wait time in seconds (exponential backoff)
RETRY_MAX_WAIT: Final[int] = 10  # Maximum wait time in seconds

# Logging configuration
LOG_FORMAT: Final[str] = "%(message)s"
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
