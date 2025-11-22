"""Generate command - main functionality to generate commit messages."""

import logging
import click
from rich.console import Console
from rich import print as rprint
from questionary import select

from utils import (
    AIBuilder,
    config,
    get_git_branch,
    commit_changes,
    copy_to_clipboard,
    retrieve_files_to_commit,
    get_active_providers,
    get_provider_by_value,
)
from utils.validation import ValidationError
from constants import DEFAULT_MAX_TOKENS

logger = logging.getLogger(__name__)
console = Console()


def get_provider_choice(provider_value: str | None, skip_prompt: bool = False):
    """
    Get the AI provider to use.

    Args:
        provider_value: Provider value from command line
        skip_prompt: Skip interactive prompt

    Returns:
        Selected provider or None
    """
    all_keys = config.get_all_keys()
    active_providers = [p for p in get_active_providers() if p.value in all_keys]

    # Check if specific provider was requested
    if provider_value:
        selected_provider = get_provider_by_value(provider_value)
        if not selected_provider or provider_value not in all_keys:
            return None
        return selected_provider

    # No providers available
    if not active_providers:
        return None

    # Single provider available
    if len(active_providers) == 1:
        return active_providers[0]

    # Skip prompt and use first available
    if skip_prompt:
        return active_providers[0]

    # Interactive selection
    choices = [f"{p.title}" for p in active_providers]

    selection = select("Select an AI provider:", choices=choices).ask()

    if not selection:
        return None

    # Find provider by title
    for provider in active_providers:
        if provider.title == selection:
            return provider

    return None


@click.command()
@click.option(
    "-p",
    "--prompt",
    default="",
    help="Additional prompt instructions for generating the commit message",
)
@click.option(
    "-P",
    "--provider",
    default="",
    help="AI provider to use (openai, anthropic, google, mistral, fireworks, plataformia)",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    default=False,
    help="Automatically commit without prompting (useful for automation)",
)
@click.option(
    "-t",
    "--max-tokens",
    default=DEFAULT_MAX_TOKENS,
    type=int,
    help=f"Maximum tokens for input validation (default: {DEFAULT_MAX_TOKENS})",
)
def generate(prompt: str, provider: str, yes: bool, max_tokens: int) -> None:
    """Generate a commit message based on staged changes."""

    logger.info("Starting commit message generation")
    logger.debug(
        f"Options: provider={provider or 'auto'}, max_tokens={max_tokens}, auto_commit={yes}"
    )

    with console.status("[bold green]Retrieving files...", spinner="dots"):
        try:
            changes = retrieve_files_to_commit(auto_stage=yes)
        except Exception as e:
            logger.error(f"Error retrieving files: {e}")
            console.print(f"[red]Error: {str(e)}[/red]")
            return

    if not changes:
        logger.warning("No changes found to commit")
        return

    branch = get_git_branch()
    logger.debug(f"Current branch: {branch}")

    # Get provider
    selected_provider = get_provider_choice(provider or None, skip_prompt=yes)

    if not selected_provider and not provider:
        logger.error("No API keys found")
        console.print(
            "[red]No API keys found. Please run [bold]gsmart login[/bold] to add your API key.[/red]"
        )
        return
    elif not selected_provider:
        logger.error(f"Provider '{provider}' not found or no API key")
        console.print("[red]No valid provider found. Please check your API keys.[/red]")
        return

    if provider:
        console.print(f"[green]Using provider: {selected_provider.title}[/green]")

    logger.info(f"Using provider: {selected_provider.value}")

    # Generate commit message
    with console.status("[bold green]Generating commit message...", spinner="dots"):
        try:
            ai = AIBuilder(selected_provider.value, prompt, max_tokens)
            message = ai.generate_commit_message(branch, changes)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            console.print(f"[red]Validation Error: {str(e)}[/red]")
            return
        except Exception as e:
            logger.error(f"Unexpected error during generation: {e}", exc_info=True)
            console.print(f"[red]Error: {str(e)}[/red]")
            return

    # Check for errors
    if isinstance(message, dict) and "error" in message:
        logger.error(f"AI provider error: {message['error']}")
        console.print(f"[red]{message['error']}[/red]")
        return

    # Display generated message
    console.print(f"[green]✓[/green] {message}")
    logger.info("Commit message generated successfully")

    # Skip prompt if --yes flag
    if yes:
        action = "commit"
    else:
        # Ask what to do with the message
        action = select(
            "What would you like to do?",
            choices=["Commit", "Copy message to clipboard", "Regenerate message", "Do nothing"],
        ).ask()

    if not action:
        logger.info("User cancelled action")
        console.print("[red]No action selected. Doing nothing.[/red]")
        return

    logger.debug(f"User selected action: {action}")

    # Handle action
    if action.lower() == "commit":
        result = commit_changes(message)
        if result:
            logger.info("Changes committed successfully")
            console.print("[green]✓ Changes committed successfully[/green]")
        else:
            logger.warning("Commit failed, copying to clipboard")
            console.print("[red]Failed to commit changes.[/red]")
            copy_to_clipboard(message)
            console.print("[green]✓ Message copied to clipboard[/green]")

    elif action.lower() == "copy message to clipboard":
        copy_to_clipboard(message)
        logger.info("Message copied to clipboard")
        console.print("[green]✓ Message copied to clipboard[/green]")

    elif action.lower() == "regenerate message":
        logger.info("Regenerating message")
        # Recursive call to regenerate
        from click import Context

        ctx = click.get_current_context()
        ctx.invoke(generate, prompt=prompt, provider=provider, yes=yes, max_tokens=max_tokens)

    elif action.lower() == "do nothing":
        logger.info("No action taken")
        console.print("[yellow]No action taken[/yellow]")
