"""Helper utilities for the CLI."""

import pyperclip
from typing import List, Optional, Set
from pathlib import Path

from rich.console import Console
from questionary import checkbox, Choice

from utils.git import GitStatus, get_git_changes, get_git_status, stage_file


console = Console()


def copy_to_clipboard(text: str) -> None:
    """
    Copy text to clipboard.
    
    Args:
        text: Text to copy
    """
    try:
        pyperclip.copy(text)
    except Exception:
        console.print("[red]Failed to copy to clipboard[/red]")


def normalize_status(status: str) -> str:
    """Normalize git status code by removing whitespace."""
    return status.replace(" ", "")


def format_file_label(file: GitStatus) -> str:
    """
    Format file label for display.
    
    Args:
        file: Git status object
        
    Returns:
        Formatted file label
    """
    if file.original_path:
        return f"{file.original_path} → {file.file_path}"
    return file.file_name


def format_choice_title(file: GitStatus) -> str:
    """
    Format choice title with color based on status.
    
    Args:
        file: Git status object
        
    Returns:
        Formatted choice title
    """
    label = format_file_label(file)
    normalized = normalize_status(file.status)
    
    if normalized == "??":
        return f"[green]{label}[/green]"
    elif "D" in normalized:
        return f"[red]{label}[/red]"
    elif normalized.startswith("A"):
        return f"[green]{label}[/green]"
    elif normalized.startswith("R"):
        return f"[cyan]{label}[/cyan]"
    else:
        return f"[yellow]{label}[/yellow]"


def collect_paths_to_stage(files: List[GitStatus]) -> List[str]:
    """
    Collect all file paths that need to be staged.
    
    Args:
        files: List of GitStatus objects
        
    Returns:
        List of unique file paths
    """
    paths: Set[str] = set()
    for file in files:
        paths.add(file.file_path)
        if file.original_path:
            paths.add(file.original_path)
    return list(paths)


def retrieve_files_to_commit(auto_stage: bool = False) -> Optional[str]:
    """
    Retrieve files to commit with optional interactive selection.
    
    Args:
        auto_stage: If True, automatically stage all files
        
    Returns:
        Git diff changes or None if no changes
    """
    # Check if there are already staged changes
    changes = get_git_changes()
    if changes:
        return changes
    
    # Get unstaged files
    status = get_git_status()
    if not status:
        console.print("[red]No changes found. Please make some changes to your code.[/red]")
        return None
    
    # Auto-stage all files or prompt user
    files_to_stage: List[GitStatus] = []
    
    if auto_stage:
        files_to_stage = status
    else:
        # Create choices for interactive selection
        choices = [
            Choice(
                title=format_file_label(file),
                value=file,
                checked=False
            )
            for file in status
        ]
        
        selected = checkbox(
            "Select files to stage:",
            choices=choices
        ).ask()
        
        if not selected:
            console.print("[red]No files selected.[/red]")
            return None
        
        files_to_stage = selected
    
    # Stage selected files
    paths_to_stage = collect_paths_to_stage(files_to_stage)
    result = stage_file(paths_to_stage)
    
    if result:
        console.print("[dim]Files staged successfully[/dim]")
        changes = get_git_changes()
    else:
        console.print("[red]Failed to stage files[/red]")
        return None
    
    return changes
