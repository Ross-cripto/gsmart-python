# 🚀 Quick Installation & Usage Guide

## Installation Steps

### Option 1: Install from Source (Recommended for Development)

```bash
# 1. Navigate to the gsmart directory
cd gsmart

# 2. Create a virtual environment (recommended)
python -m venv venv

# 3. Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install the package in editable mode
pip install -e .
```

### Option 2: Install as a Package

```bash
# 1. Navigate to the gsmart directory
cd gsmart

# 2. Build the package
pip install build
python -m build

# 3. Install the built package
pip install dist/gsmart-1.1.0-py3-none-any.whl
```

### Option 3: Install Dependencies Only

```bash
# If you just want to run the script directly
pip install -r requirements.txt

# Then run with:
python gsmart_cli.py
```

## First-Time Setup

### 1. Login to an AI Provider

```bash
# Run the login command
gsmart login

# Select your provider (e.g., OpenAI)
# Enter your API key when prompted
```

**🔐 Security Note**: API keys are now stored securely in your system's keyring (macOS Keychain, Windows Credential Manager, Linux Secret Service) instead of plaintext config files.

### 2. Get Your API Keys

**OpenAI:**
- Go to: https://platform.openai.com/api-keys
- Create a new secret key
- Copy and paste when prompted

**Anthropic (Claude):**
- Go to: https://console.anthropic.com/
- Navigate to API Keys
- Create a new key

**Google AI (Gemini):**
- Go to: https://makersuite.google.com/app/apikey
- Create an API key

**Other Providers:**
- See README.md for links to all supported providers

## Usage Examples

### Basic Usage

```bash
# 1. Make some changes in your git repository
echo "print('Hello World')" > test.py

# 2. Run gsmart
gsmart

# 3. The CLI will:
#    - Show you modified files
#    - Let you select files to stage
#    - Validate changes (token limit check)
#    - Generate a commit message (with automatic retries if API fails)
#    - Ask what you want to do (commit/copy/regenerate/nothing)
```

### Advanced Examples

```bash
# Use a specific provider
gsmart generate --provider anthropic

# Add custom instructions
gsmart generate --prompt "use emojis and keep it under 50 characters"

# Enable debug mode for detailed logging
gsmart generate --debug

# Set custom token limit (default: 8000)
gsmart generate --max-tokens 5000

# Auto-commit mode (skip all prompts)
gsmart generate --yes

# Combine all options
gsmart generate --debug --provider openai --prompt "be concise" --max-tokens 6000 --yes
```

## Common Commands

```bash
# Generate commit message (default command)
gsmart
gsmart generate

# Login to add/update API keys
gsmart login

# Reset all configuration
gsmart reset

# Show help
gsmart --help

# Show version
gsmart --version
```

## New Features in v1.1.0

### 1. Debug Mode
Enable detailed logging for troubleshooting:
```bash
gsmart --debug
```

### 2. Token Validation
Customize maximum tokens for validation (saves API costs):
```bash
# For large commits
gsmart generate --max-tokens 12000

# For small commits
gsmart generate --max-tokens 4000
```

### 3. Automatic Retries
API calls automatically retry up to 3 times with exponential backoff (4s → 7s → 10s) if they fail.

### 4. Secure Key Storage
API keys are stored in your system's keyring, not in plaintext files.

## Troubleshooting

### "No API keys found"
Run `gsmart login` to add your API key first. Your key will be securely stored in the system keyring.

### "No changes found"
Make sure you have:
1. Made changes to files in a git repository
2. Either staged files with `git add` or let gsmart stage them for you

### "Changes too large"
Your changes exceed the token limit. Try:
```bash
# Increase the limit
gsmart generate --max-tokens 12000

# Or commit in smaller chunks
git add file1.py
gsmart
git add file2.py
gsmart
```

### "Invalid provider"
Make sure you spelled the provider name correctly:
- openai
- anthropic
- google
- mistral
- fireworks
- plataformia

### Import Errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Debug a Problem
Use debug mode to see detailed logs:
```bash
gsmart --debug
```

## File Structure

```
gsmart/
├── gsmart_cli.py          # Main entry point with logging setup
├── constants.py           # Configuration constants (new: token limits, retry config)
├── commands/              # CLI commands
│   ├── __init__.py
│   ├── generate.py        # Generate (new: --max-tokens, --debug, logging)
│   ├── login.py           # Login to providers
│   └── reset.py           # Reset configuration
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── ai.py              # AI integrations (new: retry mechanism, logging)
│   ├── config.py          # Config management (new: keyring storage)
│   ├── git.py             # Git operations
│   ├── helpers.py         # Helper functions
│   ├── providers.py       # Provider definitions
│   ├── validation.py      # NEW: Input validation module
│   └── version_check.py   # Update checker
├── setup.py               # Setup script
├── pyproject.toml         # Project metadata
├── requirements.txt       # Dependencies (new: tenacity, keyring)
├── README.md              # Full documentation
├── CHANGELOG.md           # NEW: Detailed changelog
├── LICENSE                # MIT License
├── .gitignore            # Git ignore rules
└── MANIFEST.in           # Package manifest
```

## What's New in v1.1.0

### 🔐 Secure API Keys
- API keys stored in system keyring (no more plaintext!)
- macOS: Keychain Access
- Windows: Credential Manager  
- Linux: Secret Service

### 🔄 Automatic Retries
- Up to 3 retry attempts
- Exponential backoff (4s → 7s → 10s)
- Handles temporary API failures gracefully

### ✅ Input Validation
- Validates token limits before API calls
- Saves costs by preventing oversized requests
- Customizable with `--max-tokens`

### 📝 Logging System
- Debug mode with `--debug` flag
- Detailed operation logs
- Beautiful Rich output with colors
- Complete error stack traces

## Next Steps

1. ✅ Install the package
2. ✅ Run `gsmart login` and add your API key (stored securely in keyring)
3. ✅ Make some changes in a git repository
4. ✅ Run `gsmart` to generate your first AI-powered commit!
5. ✅ Try `gsmart --debug` to see how it works under the hood

## Support

- Report issues: https://github.com/ragnarok22/gsmart/issues
- Read full docs: See README.md in this directory
- See changelog: See CHANGELOG.md for detailed changes

---

Happy committing! 🎉