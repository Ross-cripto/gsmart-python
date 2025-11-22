# GSmart - Git Smart CLI

```
 _____  _____                          _
|  __ \/  ___|                        | |
| |  \/\ `--.  _ __ ___    __ _  _ __ | |_
| | __  `--. \| '_ ` _ \  / _` || '__|| __|
| |_\ \/\__/ /| | | | | || (_| || |   | |_
 \____/\____/ |_| |_| |_| \__,_||_|    \__| CLI
```

**AI-powered Git commit message generator** that helps you create meaningful, conventional commit messages using various AI providers.

## 🌟 Features

- ✨ **AI-Powered Commit Messages**: Generate conventional commit messages using state-of-the-art AI models
- 🔄 **Multiple AI Providers**: Support for OpenAI, Anthropic, Google AI, Mistral, Fireworks AI, and PlataformIA
- 📝 **Conventional Commits**: Follows the [Conventional Commits](https://www.conventionalcommits.org/) specification
- 🎯 **Interactive File Selection**: Choose which files to stage before generating the commit message
- 📋 **Clipboard Support**: Copy generated messages to clipboard
- ⚡ **Automation Mode**: Auto-commit with `--yes` flag for CI/CD pipelines
- 🎨 **Beautiful CLI**: Rich terminal output with colors and spinners
- 🔐 **Secure Configuration**: API keys stored securely in system keyring (macOS Keychain, Windows Credential Manager, Linux Secret Service)
- 🔄 **Automatic Retries**: Up to 3 retry attempts with exponential backoff for API failures
- ✅ **Input Validation**: Validates changes before sending to API (saves costs and prevents errors)
- 📝 **Comprehensive Logging**: Debug mode with detailed logging for troubleshooting

## 📦 Installation

### Using pip

```bash
pip install gsmart
```

### From Source

```bash
git clone https://github.com/Ross-cripto/gsmart-python.git
cd gsmart
pip install -e .
```

### Requirements

- Python 3.10 or higher
- Git installed and configured
- API key from at least one supported provider

## 🚀 Quick Start

### 1. Login to Your AI Provider

```bash
gsmart login
```

Select your preferred AI provider and enter your API key. The key will be stored securely in your system's keyring.

### 2. Generate a Commit Message

```bash
# Make some changes in your git repository
echo "print('Hello World')" > hello.py

# Run gsmart to generate and commit
gsmart
```

The CLI will:
1. Show you the modified files
2. Let you select which files to stage
3. Validate the changes (token limit)
4. Generate a commit message using AI (with automatic retries if needed)
5. Ask if you want to commit, copy to clipboard, regenerate, or do nothing

### 3. Advanced Usage

```bash
# Use a specific provider
gsmart generate --provider openai

# Add custom instructions
gsmart generate --prompt "use emojis in the commit message"

# Enable debug mode for detailed logging
gsmart --debug

# Set custom token limit
gsmart generate --max-tokens 9000

# Auto-commit without prompts (useful for automation)
gsmart --yes

# Combine options
gsmart generate --debug --provider openai --prompt "keep it concise" --max-tokens 6000 --yes
```

## 🎮 Commands

### `gsmart generate`

Generate a commit message based on staged changes.

**Options:**
- `-p, --prompt TEXT`: Additional instructions for the AI
- `-P, --provider TEXT`: Specify AI provider (openai, anthropic, google, mistral, fireworks, plataformia)
- `-y, --yes`: Auto-commit without prompting
- `-t, --max-tokens INTEGER`: Maximum tokens for input validation (default: 8000)
- `--debug`: Enable debug logging
- `--help`: Show help message

**Examples:**

```bash
# Basic usage
gsmart

# With custom prompt
gsmart generate -p "use present tense"

# Specify provider
gsmart -P anthropic

# Debug mode
gsmart --debug

# Custom token limit
gsmart --max-tokens 5000

# Automation mode
gsmart generate -y

# All options combined
gsmart generate --debug -P openai -p "be concise" -t 6000 -y
```

### `gsmart login`

Add or update API keys for AI providers.

```bash
gsmart login
```

This will:
1. Show a list of available providers
2. Prompt for your API key
3. Store it securely in your system's keyring (not in plaintext)

### `gsmart reset`

Clear all stored configuration and API keys.

**Options:**
- `-f, --force`: Skip confirmation prompt

**Examples:**

```bash
# With confirmation
gsmart reset

# Force reset
gsmart reset --force
```

## 🔑 Supported AI Providers

### OpenAI
- **Models**: GPT-4o-mini
- **Get API Key**: https://platform.openai.com/api-keys

### Anthropic (Claude)
- **Models**: Claude 3.5 Haiku
- **Get API Key**: https://console.anthropic.com/

### Google AI (Gemini)
- **Models**: Gemini 2.0 Flash
- **Get API Key**: https://makersuite.google.com/app/apikey

### Mistral
- **Models**: Mistral Large
- **Get API Key**: https://console.mistral.ai/

### Fireworks AI
- **Models**: Llama 3.1 70B
- **Get API Key**: https://fireworks.ai/

### PlataformIA
- **Models**: Radiance
- **Get API Key**: https://plataformia.com/

## 🔧 Configuration

### Secure API Key Storage

API keys are now stored securely using your system's keyring:
- **macOS**: Keychain Access
- **Windows**: Credential Manager
- **Linux**: Secret Service (GNOME Keyring, KDE Wallet)

No more plaintext API keys in config files!

### Token Limits

By default, GSmart validates that your changes don't exceed 8000 tokens before sending to the API. You can customize this:

```bash
# For large commits
gsmart generate --max-tokens 12000

# For small, frequent commits
gsmart generate --max-tokens 4000
```

### Debug Mode

When troubleshooting, enable debug mode for detailed logging:

```bash
gsmart --debug
```

This shows:
- Detailed operation logs
- API call information
- Validation steps
- Error stack traces

## 🎯 Commit Message Format

GSmart generates commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>
```

### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Other changes (maintenance, etc.)
- `revert`: Revert previous commit

### Examples

```
feat(auth): add OAuth2 login functionality
fix(api): resolve undefined response in user endpoint
docs(readme): update installation instructions
style(components): format code according to style guide
refactor(utils): simplify error handling logic
perf(database): optimize query performance
test(auth): add unit tests for login flow
build(deps): upgrade Django to 4.2
ci(github): add automated testing workflow
chore(release): bump version to 2.0.0
revert: remove experimental feature flag
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/Ross-cripto/gsmart-python.git
cd gsmart

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Development Dependencies

```bash
pip install pytest pytest-cov black ruff mypy
```

### Run Tests

```bash
pytest
pytest --cov=gsmart
```

### Code Formatting

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy gsmart_cli.py commands/ utils/
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes using gsmart! (`gsmart`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for all public functions
- Add tests for new features
- Update README if needed

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👨‍💻 Authors

- **Reinier Hernández** - Original Node.js version
- **Miguel** - Python implementation

## 🙏 Acknowledgments

- Inspired by the original [gsmart](https://github.com/ragnarok22/gsmart) Node.js CLI
- AI SDK providers: OpenAI, Anthropic, Google, Mistral, Fireworks, PlataformIA
- [Conventional Commits](https://www.conventionalcommits.org/) specification
- Python community for excellent libraries: Click, Rich, Questionary, Tenacity, Keyring

## 📊 Changelog

### Version .1.1 
- 🔐 **Secure API Keys**: Now using system keyring instead of plaintext config files
- 🔄 **Automatic Retries**: Up to 3 retry attempts with exponential backoff for API failures
- ✅ **Input Validation**: Validates token limits before API calls (saves costs)
- 📝 **Logging System**: Comprehensive logging with `--debug` flag
- ⚙️ **Configurable Limits**: New `--max-tokens` option to customize validation limits

### Version 0.1.0 
- Initial Python implementation
- Support for 6 AI providers
- Interactive file selection
- Conventional Commits format
- Clipboard support
- Auto-commit mode
- Configuration management
- Update checker

## 🐛 Known Issues

- None currently reported

## 💡 Future Enhancements

- [ ] Add support for commit message templates
- [ ] Multi-line commit messages with body and footer
- [ ] Git hooks integration
- [ ] Custom commit type definitions
- [ ] Batch commit mode for multiple commits
- [ ] Commit message history and favorites
- [ ] Integration with GitHub/GitLab APIs
- [ ] Response caching to avoid duplicate API calls

## 📬 Support

- **Issues**: https://github.com/Ross-cripto/gsmart-python/issues
- **Discussions**: https://github.com/Ross-cripto/gsmart-python/discussions

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

Made with ❤️ by developers, for developers.