"""AI Builder for generating commit messages using different providers."""

import logging
from typing import Dict, Union
from abc import ABC, abstractmethod

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai
from mistralai import Mistral

from utils.config import config
from utils.providers import ProviderType
from utils.validation import validate_changes
from constants import DEFAULT_PROVIDER, MAX_RETRIES, RETRY_MIN_WAIT, RETRY_MAX_WAIT

logger = logging.getLogger(__name__)


class AIError(Exception):
    """Custom exception for AI-related errors."""

    pass


def build_prompt(branch_name: str, changes: str) -> tuple[str, str]:
    """
    Build the prompt for the AI model.

    Args:
        branch_name: Current git branch name
        changes: Git diff changes

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    system = """Role and Objective
Produce commit messages that strictly adhere to the Conventional Commits specification.

# Instructions
- Generate a commit message that includes:
  - **Type** (required): Choose from `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, or `revert`.
  - **Scope** (optional): Specify additional context about the affected code area.
  - **Description** (required): Provide a succinct summary of the changes.
- Format: `<type>(<scope>): <description>`
  - `<scope>` is optional and may be omitted.
- Ensure the commit message fully meets all structure and content criteria before outputting.

# Output Format
- Output only the commit message after it successfully passes all structure and content validation checks. Do not include any validation explanation or checklist.

# Stop Conditions
- Output only the commit message after it successfully passes all structure and content validation checks. No additional text or explanations should be included."""

    user_prompt = f"""Generate a commit message for these changes on branch {branch_name}:

Changes:
{changes}

Format: <type>(<scope>): <description>
Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

Examples:
- feat(auth): add login functionality with OAuth
- fix(api): resolve undefined response in user endpoint
- docs(readme): update installation instructions
- style(components): format code according to style guide
- refactor(utils): simplify error handling logic
- perf(queries): optimize database lookups
- test(auth): add unit tests for authentication flow
- build(deps): update dependency versions
- ci(github): add workflow for automated testing
- chore(release): prepare v1.2.0 release
- revert: remove feature flag for beta functionality

Return ONLY the commit message. No explanations or additional text."""

    return system, user_prompt


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, api_key: str):
        """Initialize the AI provider."""
        self.api_key = api_key
        logger.debug(f"Initialized {self.__class__.__name__}")

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        retry=retry_if_exception_type((Exception,)),
        reraise=True,
    )
    @abstractmethod
    def generate(self, system: str, prompt: str) -> str:
        """
        Generate text using the AI model.

        Automatically retries up to MAX_RETRIES times with exponential backoff.

        Args:
            system: System prompt
            prompt: User prompt

        Returns:
            Generated text

        Raises:
            Exception: If all retry attempts fail
        """
        pass


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""

    def generate(self, system: str, prompt: str) -> str:
        """Generate text using OpenAI."""
        logger.info("Calling OpenAI API (model: gpt-4o-mini)")
        try:
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            result = response.choices[0].message.content or ""
            logger.info(f"OpenAI API call successful (response length: {len(result)} chars)")
            return result
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise


class AnthropicProvider(AIProvider):
    """Anthropic provider implementation."""

    def generate(self, system: str, prompt: str) -> str:
        """Generate text using Anthropic."""
        logger.info("Calling Anthropic API (model: claude-3-5-haiku-20241022)")
        try:
            client = Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            result = response.content[0].text if response.content else ""
            logger.info(f"Anthropic API call successful (response length: {len(result)} chars)")
            return result
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise


class GoogleProvider(AIProvider):
    """Google AI provider implementation."""

    def generate(self, system: str, prompt: str) -> str:
        """Generate text using Google AI."""
        logger.info("Calling Google AI API (model: gemini-2.0-flash-exp)")
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp", system_instruction=system
            )
            response = model.generate_content(prompt)
            result = response.text
            logger.info(f"Google AI API call successful (response length: {len(result)} chars)")
            return result
        except Exception as e:
            logger.error(f"Google AI API error: {str(e)}")
            raise


class MistralProvider(AIProvider):
    """Mistral provider implementation."""

    def generate(self, system: str, prompt: str) -> str:
        """Generate text using Mistral."""
        logger.info("Calling Mistral API (model: mistral-large-latest)")
        try:
            client = Mistral(api_key=self.api_key)
            response = client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            )
            result = response.choices[0].message.content or ""
            logger.info(f"Mistral API call successful (response length: {len(result)} chars)")
            return result
        except Exception as e:
            logger.error(f"Mistral API error: {str(e)}")
            raise


class FireworksProvider(AIProvider):
    """Fireworks AI provider implementation."""

    def generate(self, system: str, prompt: str) -> str:
        """Generate text using Fireworks AI."""
        logger.info("Calling Fireworks AI API (model: llama-v3p1-70b-instruct)")
        try:
            client = OpenAI(api_key=self.api_key, base_url="https://api.fireworks.ai/inference/v1")
            response = client.chat.completions.create(
                model="accounts/fireworks/models/llama-v3p1-70b-instruct",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            )
            result = response.choices[0].message.content or ""
            logger.info(f"Fireworks AI API call successful (response length: {len(result)} chars)")
            return result
        except Exception as e:
            logger.error(f"Fireworks AI API error: {str(e)}")
            raise


class PlataformIAProvider(AIProvider):
    """PlataformIA provider implementation."""

    def generate(self, system: str, prompt: str) -> str:
        """Generate text using PlataformIA."""
        logger.info("Calling PlataformIA API (model: radiance)")
        try:
            client = OpenAI(api_key=self.api_key, base_url="https://apigateway.avangenio.net")
            response = client.chat.completions.create(
                model="radiance",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            )
            result = response.choices[0].message.content or ""
            logger.info(f"PlataformIA API call successful (response length: {len(result)} chars)")
            return result
        except Exception as e:
            logger.error(f"PlataformIA API error: {str(e)}")
            raise


PROVIDER_MAP: Dict[ProviderType, type[AIProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
    "mistral": MistralProvider,
    "fireworks": FireworksProvider,
    "plataformia": PlataformIAProvider,
}


class AIBuilder:
    """AI builder for generating commit messages."""

    def __init__(
        self,
        provider: ProviderType = DEFAULT_PROVIDER,
        custom_prompt: str = "",
        max_tokens: int = None,
    ):
        """
        Initialize AI builder.

        Args:
            provider: AI provider to use
            custom_prompt: Additional custom instructions
            max_tokens: Maximum tokens for input validation (uses DEFAULT_MAX_TOKENS if None)
        """
        self.provider = provider
        self.custom_prompt = custom_prompt
        self.max_tokens = max_tokens
        logger.info(f"AIBuilder initialized with provider: {provider}")

    def change_provider(self, provider: ProviderType) -> None:
        """Change the AI provider."""
        logger.info(f"Changing provider from {self.provider} to {provider}")
        self.provider = provider

    def generate_commit_message(self, branch_name: str, changes: str) -> Union[str, Dict[str, str]]:
        """
        Generate a commit message using the AI model.

        Args:
            branch_name: Current git branch name
            changes: Git diff changes

        Returns:
            Generated commit message or error dict
        """
        logger.info(f"Generating commit message for branch '{branch_name}'")
        logger.debug(f"Changes length: {len(changes)} characters")

        try:
            # Validate input
            logger.debug("Validating changes...")
            validate_changes(changes, self.max_tokens)

            api_key = config.get_key(self.provider)
            if not api_key:
                error_msg = f"No API key found for {self.provider}"
                logger.error(error_msg)
                return {"error": error_msg}

            provider_class = PROVIDER_MAP.get(self.provider)
            if not provider_class:
                error_msg = f"Invalid provider: {self.provider}"
                logger.error(error_msg)
                return {"error": error_msg}

            provider_instance = provider_class(api_key)
            system, prompt = build_prompt(branch_name, changes)

            # Add custom prompt if provided
            if self.custom_prompt:
                logger.debug(f"Adding custom prompt: {self.custom_prompt}")
                prompt = f"{prompt}\n\nAdditional instructions:\n{self.custom_prompt}"

            logger.info("Calling AI provider...")
            message = provider_instance.generate(system, prompt)

            result = message.strip()
            logger.info(f"Commit message generated successfully ({len(result)} chars)")
            logger.debug(f"Generated message: {result}")

            return result

        except Exception as e:
            error_message = (
                str(e) if str(e) else "An error occurred while generating the commit message"
            )
            logger.error(f"Error generating commit message: {error_message}", exc_info=True)
            return {"error": f"{self.provider} - {error_message}"}
