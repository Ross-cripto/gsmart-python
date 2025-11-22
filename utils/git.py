"""Git operations utilities."""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class GitStatus:
    """Represents a git file status."""
    status: str
    file_name: str
    file_path: str
    original_path: Optional[str] = None


def run_git(args: List[str], trim: bool = True, cwd: Optional[str] = None) -> str:
    """
    Run a git command.
    
    Args:
        args: Git command arguments
        trim: Whether to trim the output
        cwd: Working directory
        
    Returns:
        Command output
        
    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
        output = result.stdout
        return output.strip() if trim else output
    except subprocess.CalledProcessError as e:
        raise Exception(f"Git command failed: {e.stderr.strip()}")


def get_git_branch() -> str:
    """
    Get current git branch name.
    
    Returns:
        Branch name or empty string if not in a git repository
    """
    try:
        return run_git(["branch", "--show-current"])
    except Exception:
        return ""


def get_git_changes() -> str:
    """
    Get staged changes.
    
    Returns:
        Git diff output or empty string if no changes
    """
    try:
        return run_git(["diff", "--cached"])
    except Exception:
        return ""


def commit_changes(message: str) -> bool:
    """
    Commit staged changes with a message.
    
    Args:
        message: Commit message
        
    Returns:
        True if successful, False otherwise
    """
    try:
        run_git(["commit", "-m", message])
        return True
    except Exception:
        return False


def needs_secondary_path(status_code: str) -> bool:
    """Check if status code requires a secondary path (renamed/copied files)."""
    normalized = status_code.strip()
    return normalized.startswith("R") or normalized.startswith("C")


def get_git_status() -> List[GitStatus]:
    """
    Get git status of all files.
    
    Returns:
        List of GitStatus objects
    """
    try:
        status_output = run_git(["status", "--porcelain", "-z"], trim=False)
        
        if not status_output:
            return []
        
        entries = [line for line in status_output.split("\0") if line]
        changed_files: List[GitStatus] = []
        
        index = 0
        while index < len(entries):
            entry = entries[index]
            
            # Parse status and path
            if len(entry) < 3:
                index += 1
                continue
            
            status_code = entry[:2].strip() or entry[:2]
            file_path = entry[3:] if len(entry) > 3 else entry[2:]
            
            current_path = file_path
            original_path = None
            
            # Handle renamed/copied files
            if needs_secondary_path(status_code) and index + 1 < len(entries):
                current_path = file_path
                original_path = entries[index + 1]
                index += 1
            
            changed_files.append(GitStatus(
                status=status_code,
                file_name=Path(current_path).name,
                file_path=current_path,
                original_path=original_path
            ))
            
            index += 1
        
        return changed_files
    
    except Exception as e:
        print(f"Error getting Git status: {e}")
        return []


def stage_file(files: List[str]) -> bool:
    """
    Stage files for commit.
    
    Args:
        files: List of file paths to stage
        
    Returns:
        True if successful, False otherwise
    """
    if not files:
        return True
    
    try:
        repo_root = run_git(["rev-parse", "--show-toplevel"])
        
        # Convert to absolute paths and remove duplicates
        absolute_paths = list(set(
            str(Path(repo_root) / file_path)
            for file_path in files
        ))
        
        run_git(["add", "--"] + absolute_paths, cwd=repo_root)
        return True
    except Exception:
        return False


def get_git_info() -> Tuple[str, str]:
    """
    Get current git branch and staged changes.
    
    Returns:
        Tuple of (branch_name, changes)
    """
    branch = get_git_branch()
    changes = get_git_changes()
    return branch, changes
