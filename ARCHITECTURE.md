# 🏗️ Architecture & Developer Guide

## Project Overview

GSmart is a Python CLI tool that generates AI-powered git commit messages. This document explains the architecture, design patterns, and best practices used in the project.

**Version:** 1.1.0

## Architecture

### High-Level Structure

```
┌─────────────────────────────────────────────────────────────┐
│                 CLI Interface (Click + Logging)              │
│                      gsmart_cli.py                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─── Commands Layer
                 │    ├── generate.py  (Main + validation + logging)
                 │    ├── login.py     (Keyring storage)
                 │    └── reset.py     (Clear keyring + config)
                 │
                 └─── Utils Layer
                      ├── ai.py         (AI + retry mechanism)
                      ├── config.py     (Keyring integration)
                      ├── git.py        (Git operations)
                      ├── helpers.py    (UI helpers)
                      ├── providers.py  (Provider definitions)
                      ├── validation.py (Input validation) ✨ NEW
                      └── version_check.py (Update notifications)
```

## Design Patterns

### 1. Command Pattern
Each CLI command is implemented as a separate module with a clear interface.

```python
# commands/generate.py
@click.command()
@click.option("--debug", is_flag=True)  # New in v1.1.0
@click.option("--max-tokens", type=int) # New in v1.1.0
def generate(prompt: str, provider: str, yes: bool, max_tokens: int, debug: bool) -> None:
    """Command implementation with logging"""
    logger.info("Starting commit message generation")
    # ... implementation
```

**Benefits:**
- Easy to add new commands
- Clear separation of concerns
- Testable in isolation
- Comprehensive logging

### 2. Strategy Pattern with Retry Mechanism
Different AI providers implement the same interface with automatic retries.

```python
# utils/ai.py
class AIProvider(ABC):
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    @abstractmethod
    def generate(self, system: str, prompt: str) -> str:
        """Generate with automatic retries (up to 3 attempts)"""
        pass

class OpenAIProvider(AIProvider):
    def generate(self, system: str, prompt: str) -> str:
        logger.info("Calling OpenAI API")
        try:
            # Implementation with logging
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
```

**Benefits:**
- Automatic retry with exponential backoff
- Detailed logging of each attempt
- Graceful error handling
- Consistent interface across providers

### 3. Singleton Pattern with Secure Storage
Configuration uses system keyring instead of plaintext files.

```python
# utils/config.py
import keyring

class Config:
    def set_key(self, provider: str, key: str) -> None:
        """Store API key in system keyring"""
        keyring.set_password("gsmart", provider, key)
    
    def get_key(self, provider: str) -> str:
        """Retrieve API key from system keyring"""
        return keyring.get_password("gsmart", provider) or ""

config = Config()  # Single instance
```

**Benefits:**
- Secure key storage (macOS Keychain, Windows Credential, Linux Secret Service)
- No plaintext API keys
- Single source of truth

### 4. Factory Pattern
Providers are created based on string identifiers.

```python
PROVIDER_MAP: Dict[ProviderType, type[AIProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    # ...
}

provider_class = PROVIDER_MAP.get(self.provider)
provider_instance = provider_class(api_key)
```

**Benefits:**
- Decouples provider creation from usage
- Easy to extend with new providers
- Type-safe provider selection

## New Features in v1.1.0

### 1. Input Validation System

**Module:** `utils/validation.py`

```python
def validate_changes(changes: str, max_tokens: Optional[int] = None) -> bool:
    """
    Validate input before sending to API.
    - Checks if changes are empty
    - Validates minimum length
    - Estimates token count
    - Raises ValidationError if limits exceeded
    """
    pass
```

**Benefits:**
- Saves API costs by validating before calls
- Customizable token limits
- Clear error messages
- Early failure detection

### 2. Retry Mechanism with Tenacity

**Implementation:** Decorator on all AI providers

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def generate(self, system: str, prompt: str) -> str:
    # API call with automatic retries
    pass
```

**Behavior:**
- Attempt 1: Fails → Wait 4 seconds
- Attempt 2: Fails → Wait 7 seconds  
- Attempt 3: Fails → Return error

**Benefits:**
- Handles temporary API failures
- Exponential backoff prevents rate limiting
- Transparent to user
- Logged for debugging

### 3. Comprehensive Logging

**Setup:** `gsmart_cli.py`

```python
from rich.logging import RichHandler

def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        handlers=[RichHandler(rich_tracebacks=True, show_path=debug)]
    )
```

**Usage throughout codebase:**
```python
logger.info("Starting operation")
logger.debug(f"Details: {variable}")
logger.error(f"Error: {e}", exc_info=True)
```

**Benefits:**
- Debug mode for troubleshooting
- Rich formatting with colors
- Complete stack traces
- Operation visibility

### 4. Keyring Integration

**Storage:** System keyring instead of plaintext

```python
import keyring

# Set
keyring.set_password("gsmart", "openai", "sk-...")

# Get
key = keyring.get_password("gsmart", "openai")

# Delete
keyring.delete_password("gsmart", "openai")
```

**Platforms:**
- **macOS**: Keychain Access
- **Windows**: Credential Manager
- **Linux**: Secret Service (GNOME Keyring, KDE Wallet)

**Benefits:**
- Secure storage
- OS-level encryption
- No plaintext files
- Industry standard

## Best Practices Implemented

### 1. Type Hints Everywhere

```python
def get_git_branch() -> str:
    """Get current git branch name."""
    pass

def validate_changes(changes: str, max_tokens: Optional[int] = None) -> bool:
    """Validate with optional token limit."""
    pass
```

### 2. Dataclasses for Structured Data

```python
@dataclass
class GitStatus:
    status: str
    file_name: str
    file_path: str
    original_path: Optional[str] = None
```

### 3. Comprehensive Error Handling

```python
try:
    validate_changes(changes, max_tokens)
    result = provider.generate(system, prompt)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    return {"error": str(e)}
except Exception as e:
    logger.error(f"API error: {e}", exc_info=True)
    raise
```

### 4. Separation of Concerns

Each module has a single responsibility:
- `ai.py`: AI provider integration + retry logic
- `git.py`: Git operations only
- `config.py`: Keyring configuration
- `validation.py`: Input validation only
- `helpers.py`: UI utilities

## Security Considerations

### Enhanced in v1.1.0

1. **Keyring Storage**
   - API keys encrypted by OS
   - No plaintext storage
   - Secure deletion

2. **Input Validation**
   - Validates before API calls
   - Prevents injection attacks
   - Token limit enforcement

3. **Error Handling**
   - No sensitive data in logs
   - Sanitized error messages
   - Safe failure modes

## Code Quality Standards

### 1. Logging Guidelines

```python
# Info: User-facing operations
logger.info("Generating commit message")

# Debug: Internal details
logger.debug(f"Token estimate: {tokens}")

# Error: Failures with context
logger.error(f"API call failed: {e}", exc_info=True)
```

### 2. Validation Pattern

```python
# Validate early
validate_changes(changes, max_tokens)

# Then proceed
result = api_call(changes)
```

### 3. Retry Pattern

```python
# Automatic retries on all providers
@retry(stop=stop_after_attempt(3), wait=wait_exponential(...))
def generate(self, system: str, prompt: str) -> str:
    # API call
    pass
```

## Extension Points

### Adding a New AI Provider

With v1.1.0, providers automatically get retry and logging:

```python
class NewProvider(AIProvider):
    def generate(self, system: str, prompt: str) -> str:
        logger.info("Calling NewProvider API")
        try:
            # Implementation
            logger.info("API call successful")
            return result
        except Exception as e:
            logger.error(f"API error: {e}")
            raise
```

The retry decorator is inherited from `AIProvider` base class.

## Performance Considerations

### 1. Validation Before API Calls
```python
# Check locally first (fast)
validate_changes(changes, max_tokens)

# Then make API call (slow)
result = provider.generate(...)
```

### 2. Retry with Backoff
```python
# Exponential backoff prevents hammering
# 4s → 7s → 10s
@retry(wait=wait_exponential(...))
```

### 3. Efficient Keyring Access
```python
# Cache in memory during session
api_key = config.get_key(provider)
```

## Testing Improvements

### Test Retry Mechanism
```python
def test_retry_on_failure():
    with patch("provider.api_call", side_effect=[Exception, Exception, "success"]):
        result = provider.generate(system, prompt)
        assert result == "success"
```

### Test Validation
```python
def test_validation_rejects_large_input():
    with pytest.raises(ValidationError):
        validate_changes("x" * 50000, max_tokens=1000)
```

### Test Keyring
```python
def test_keyring_storage():
    config.set_key("test", "secret")
    assert config.get_key("test") == "secret"
    config.clear_key("test")
    assert config.get_key("test") == ""
```

## Future Improvements

### High Priority
- [ ] Response caching (avoid duplicate API calls)
- [ ] Configurable model selection per provider
- [ ] Custom retry strategies per provider

### Medium Priority
- [ ] Commit message templates
- [ ] Multi-line commit support
- [ ] Git hooks integration

### Nice to Have
- [ ] Analytics/metrics tracking
- [ ] Team-wide configuration
- [ ] Plugin system

## Resources

### New in v1.1.0
- [Tenacity Docs](https://tenacity.readthedocs.io/) - Retry library
- [Keyring Docs](https://keyring.readthedocs.io/) - Secure storage
- [Rich Logging](https://rich.readthedocs.io/en/stable/logging.html) - Beautiful logs

### Python Best Practices
- [PEP 8](https://peps.python.org/pep-0008/) - Style Guide
- [PEP 484](https://peps.python.org/pep-0484/) - Type Hints

### CLI Development
- [Click Documentation](https://click.palletsprojects.com/)
- [Rich Documentation](https://rich.readthedocs.io/)

---

This architecture enables secure, robust, and maintainable code. The v1.1.0 improvements add retry resilience, input validation, comprehensive logging, and secure key storage without changing the core design patterns.