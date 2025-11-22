"""Version checker for package updates."""

import json
import time
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

import requests
from rich.console import Console
from rich.panel import Panel

from constants import UPDATE_CHECK_INTERVAL


console = Console()


def get_cache_file() -> Path:
    """Get the cache file path."""
    cache_dir = Path.home() / ".cache" / "gsmart"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "update_check.json"


def should_check_for_updates() -> bool:
    """Check if enough time has passed since last update check."""
    cache_file = get_cache_file()
    
    if not cache_file.exists():
        return True
    
    try:
        with open(cache_file, "r") as f:
            data = json.load(f)
            last_check = datetime.fromisoformat(data.get("last_check", ""))
            
            # Check if interval has passed
            if datetime.now() - last_check < timedelta(seconds=UPDATE_CHECK_INTERVAL):
                return False
    except (json.JSONDecodeError, ValueError, KeyError):
        pass
    
    return True


def save_check_timestamp() -> None:
    """Save the current timestamp for update check."""
    cache_file = get_cache_file()
    
    data = {
        "last_check": datetime.now().isoformat()
    }
    
    with open(cache_file, "w") as f:
        json.dump(data, f)


def get_latest_version(package_name: str) -> Optional[str]:
    """
    Get the latest version from PyPI.
    
    Args:
        package_name: Name of the package
        
    Returns:
        Latest version string or None if not found
    """
    try:
        response = requests.get(
            f"https://pypi.org/pypi/{package_name}/json",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["info"]["version"]
    except Exception:
        pass
    
    return None


def compare_versions(current: str, latest: str) -> bool:
    """
    Compare version strings.
    
    Args:
        current: Current version
        latest: Latest version
        
    Returns:
        True if latest is newer than current
    """
    def parse_version(v: str) -> tuple:
        """Parse version string to tuple of integers."""
        try:
            return tuple(map(int, v.split(".")))
        except ValueError:
            return (0, 0, 0)
    
    return parse_version(latest) > parse_version(current)


def check_for_updates(package_name: str, current_version: str) -> None:
    """
    Check for package updates and display notification.
    
    Args:
        package_name: Name of the package
        current_version: Current version
    """
    # Skip if checked recently
    if not should_check_for_updates():
        return
    
    try:
        latest_version = get_latest_version(package_name)
        
        # Save check timestamp
        save_check_timestamp()
        
        if not latest_version:
            return
        
        # Compare versions
        if compare_versions(current_version, latest_version):
            # Display update notification
            message = (
                f"[bold]Update available:[/bold] [dim]{current_version}[/dim] → [bold green]{latest_version}[/bold green]\n"
                f"[dim]Changelog:[/dim] https://github.com/ragnarok22/gsmart/releases\n"
                f"[cyan]Run[/cyan] [bold cyan]pip install --upgrade {package_name}[/bold cyan] [cyan]to update[/cyan]"
            )
            
            console.print(Panel(
                message,
                border_style="yellow",
                padding=(1, 2)
            ))
            console.print()
    
    except Exception:
        # Silently fail - don't interrupt user experience
        pass
