"""AI Provider configurations."""

from dataclasses import dataclass
from typing import List, Literal


ProviderType = Literal[
    "openai",
    "anthropic",
    "google",
    "mistral",
    "fireworks",
    "plataformia"
]


@dataclass
class Provider:
    """Provider configuration."""
    title: str
    value: ProviderType
    description: str
    active: bool = True


PROVIDERS: List[Provider] = [
    Provider(
        title="OpenAI",
        value="openai",
        description="OpenAI is an artificial intelligence research laboratory consisting "
                   "of the for-profit OpenAI LP and the non-profit OpenAI Inc.",
        active=True,
    ),
    Provider(
        title="Anthropic",
        value="anthropic",
        description="Anthropic is a research lab building large-scale AI systems "
                   "that are steerable, aligned, and safe.",
        active=True,
    ),
    Provider(
        title="Google AI",
        value="google",
        description="Google AI is a division of Google dedicated to artificial intelligence.",
        active=True,
    ),
    Provider(
        title="Mistral",
        value="mistral",
        description="Mistral is a research lab building large-scale AI systems "
                   "that are steerable, aligned, and safe.",
        active=True,
    ),
    Provider(
        title="Fireworks AI",
        value="fireworks",
        description="Fireworks AI is a research lab building large-scale AI systems "
                   "that are steerable, aligned, and safe.",
        active=True,
    ),
    Provider(
        title="PlataformIA",
        value="plataformia",
        description="PlataformIA is a Cuban AI platform offering tools for app creation, "
                   "workflow automation, and content generation, with APIs for developers.",
        active=True,
    ),
]


def get_active_providers() -> List[Provider]:
    """Get list of active providers."""
    return [provider for provider in PROVIDERS if provider.active]


def get_provider_by_value(value: str) -> Provider | None:
    """Get provider by value."""
    for provider in PROVIDERS:
        if provider.value == value:
            return provider
    return None
