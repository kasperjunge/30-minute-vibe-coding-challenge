#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: python new.py <project_name>")
        sys.exit(1)
    
    project_name = sys.argv[1]
    
    # Get the script's directory
    script_dir = Path(__file__).parent
    
    # Define paths
    projects_dir = script_dir / "projects"
    commands_dir = script_dir / "commands"
    new_project_dir = projects_dir / project_name
    
    # Check if commands directory exists
    if not commands_dir.exists():
        print(f"Error: commands directory not found at {commands_dir}")
        sys.exit(1)
    
    # Check if project already exists
    if new_project_dir.exists():
        print(f"Error: Project '{project_name}' already exists in projects/")
        sys.exit(1)
    
    # Create the new project directory
    new_project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create .claude/commands and .cursor/commands directories
    claude_commands_dir = new_project_dir / ".claude" / "commands"
    cursor_commands_dir = new_project_dir / ".cursor" / "commands"
    
    claude_commands_dir.mkdir(parents=True, exist_ok=True)
    cursor_commands_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy commands into both directories
    for item in commands_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, claude_commands_dir / item.name)
            shutil.copy2(item, cursor_commands_dir / item.name)
    
    print(f"✓ Created project: {project_name}")
    print(f"✓ Copied commands to .claude/commands/ and .cursor/commands/")
    
    # Open the project in a new Cursor window
    try:
        subprocess.run(["cursor", "-n", str(new_project_dir)], check=True)
        print(f"✓ Opened project in Cursor")
    except subprocess.CalledProcessError:
        print(f"⚠ Warning: Failed to open Cursor. Please open {new_project_dir} manually.")
    except FileNotFoundError:
        print(f"⚠ Warning: 'cursor' command not found. Please open {new_project_dir} manually.")


if __name__ == "__main__":
    main()

