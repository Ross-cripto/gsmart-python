"""Reset command - clear all configuration."""

import click
from rich.console import Console
from questionary import confirm
import keyring
from utils import config


console = Console()


@click.command()
@click.option(
    "-f", "--force",
    is_flag=True,
    default=False,
    help="Force reset without confirmation"
)
def reset(force: bool) -> None:
    """Reset all API keys and remove configuration."""
    
    # Confirm if not forced
    if not force:
        confirmed = confirm(
            "Are you sure you want to reset the configuration?"
        ).ask()
        
        if not confirmed:
            console.print("[red]Operation cancelled[/red]")
            return
    
    # Clear configuration
    config.clear()
    console.print("[green]✓ Configuration reset successfully[/green]")
