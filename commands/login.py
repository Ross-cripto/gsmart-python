"""Login command - add API keys for AI providers."""

import click
from rich.console import Console
from questionary import select, password

from utils import config, get_active_providers


console = Console()


@click.command()
def login() -> None:
    """Login to a provider to use their AI service."""
    
    providers = get_active_providers()
    
    # Select provider
    choices = [p.title for p in providers]
    
    selected = select(
        "Select a provider:",
        choices=choices
    ).ask()
    
    if not selected:
        console.print("[red]No provider selected[/red]")
        return
    
    # Find provider by title
    provider = None
    for p in providers:
        if p.title == selected:
            provider = p
            break
    
    if not provider:
        console.print("[red]Invalid provider[/red]")
        return
    
    # Get API key
    api_key = password(
        "Enter your API key:",
        instruction="This will be stored in your local configuration"
    ).ask()
    
    if not api_key:
        console.print("[red]No API key provided[/red]")
        return
    
    # Save API key
    config.set_key(provider.value, api_key)
    console.print("[green]✓ API key saved successfully[/green]")
