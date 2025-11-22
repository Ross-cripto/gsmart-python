#!/usr/bin/env python3
"""
 _____  _____                          _
|  __ \\/  ___|                        | |
| |  \\/\\ `--.  _ __ ___    __ _  _ __ | |_
| | __  `--. \\| '_ ` _ \\  / _` || '__|| __|
| |_\\ \\/\\__/ /| | | | | || (_| || |   | |_
 \\____/\\____/ |_| |_| |_| \\__,_||_|    \\__| CLI

Git Smart - AI-powered commit message generator
Created by: Reinier Hernández
Python version by: Miguel
"""

import sys
import signal
import logging
from typing import NoReturn

import click
from rich.console import Console
from rich.logging import RichHandler

from commands.generate import generate
from commands.login import login
from commands.reset import reset
from utils.version_check import check_for_updates
from constants import APP_NAME, APP_VERSION, APP_DESCRIPTION, LOG_FORMAT, LOG_DATE_FORMAT

console = Console()


def setup_logging(debug: bool = False) -> None:
    """
    Setup logging configuration.

    Args:
        debug: Enable debug logging if True
    """
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[RichHandler(rich_tracebacks=True, show_time=False, show_path=debug)],
    )

    # Set level for gsmart logger
    logger = logging.getLogger("gsmart")
    logger.setLevel(level)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def handle_sigterm(signum: int, frame) -> NoReturn:
    """Handle SIGINT and SIGTERM signals gracefully."""
    console.print("\n[yellow]Operation cancelled by user[/yellow]")
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, handle_sigterm)
signal.signal(signal.SIGTERM, handle_sigterm)


@click.group(invoke_without_command=True)
@click.version_option(version=APP_VERSION, prog_name=APP_NAME)
@click.option("--debug", is_flag=True, default=False, help="Enable debug logging")
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    """Git Smart - AI-powered commit message generator."""
    # Setup logging
    setup_logging(debug)

    logger = logging.getLogger(__name__)
    if debug:
        logger.debug("Debug mode enabled")

    # Check for updates on startup
    check_for_updates(APP_NAME, APP_VERSION)

    # If no command is specified, run the generate command (default behavior)
    if ctx.invoked_subcommand is None:
        ctx.invoke(generate)


# Register commands
cli.add_command(generate, name="generate")
cli.add_command(login, name="login")
cli.add_command(reset, name="reset")


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

