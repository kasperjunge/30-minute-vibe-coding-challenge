#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path


def copy_tree(src, dst, ignore_patterns=None):
    """Copy directory tree, excluding specified patterns."""
    ignore_patterns = ignore_patterns or []
    
    for item in src.iterdir():
        # Skip ignored patterns
        if any(pattern in str(item) for pattern in ignore_patterns):
            continue
            
        dst_path = dst / item.name
        
        if item.is_dir():
            dst_path.mkdir(parents=True, exist_ok=True)
            copy_tree(item, dst_path, ignore_patterns)
        else:
            shutil.copy2(item, dst_path)


def list_templates(templates_dir):
    """List available templates."""
    if not templates_dir.exists():
        return []
    return [d.name for d in templates_dir.iterdir() if d.is_dir()]


def main():
    parser = argparse.ArgumentParser(description="Create a new project")
    parser.add_argument("project_name", nargs='?', help="Name of the project to create")
    parser.add_argument("--template", "-t", help="Template to use (optional)")
    parser.add_argument("--list-templates", "-l", action="store_true", 
                       help="List available templates")
    
    args = parser.parse_args()
    
    # Get the script's directory
    script_dir = Path(__file__).parent
    
    # Define paths
    projects_dir = script_dir / "projects"
    commands_dir = script_dir / "commands"
    templates_dir = script_dir / "templates"
    
    # List templates if requested
    if args.list_templates:
        templates = list_templates(templates_dir)
        if templates:
            print("Available templates:")
            for template in templates:
                print(f"  - {template}")
        else:
            print("No templates found in templates/")
        sys.exit(0)
    
    # Validate project_name is provided
    if not args.project_name:
        parser.print_help()
        sys.exit(1)
    
    project_name = args.project_name
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
    
    # If template is specified, copy it
    if args.template:
        template_dir = templates_dir / args.template
        if not template_dir.exists():
            print(f"Error: Template '{args.template}' not found in templates/")
            print("Use --list-templates to see available templates")
            shutil.rmtree(new_project_dir)  # Clean up
            sys.exit(1)
        
        # Copy template contents (excluding __pycache__, .pyc, data/, etc.)
        ignore_patterns = ['__pycache__', '.pyc', '.pyo', 'data/', '.db']
        copy_tree(template_dir, new_project_dir, ignore_patterns)
        print(f"✓ Created project from template: {args.template}")
    
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
    
    if not args.template:
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

