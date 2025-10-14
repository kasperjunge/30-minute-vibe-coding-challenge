#!/usr/bin/env python3
"""CLI tool for bootstrapping 30 Minute Vibe Coding Challenge projects."""
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

app = typer.Typer(
    name="vibe",
    help="🎵 Create new projects for the 30 Minute Vibe Coding Challenge",
    add_completion=False,
)
console = Console()


def copy_tree(src: Path, dst: Path, ignore_patterns: list[str] | None = None) -> None:
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


def get_templates_dir() -> Path:
    """Get the templates directory path."""
    return Path(__file__).parent / "templates"


def list_available_templates() -> list[str]:
    """List available templates."""
    templates_dir = get_templates_dir()
    if not templates_dir.exists():
        return []
    return [d.name for d in templates_dir.iterdir() if d.is_dir()]


def get_projects_dir() -> Path:
    """Get the projects directory path."""
    return Path(__file__).parent / "projects"


def list_existing_projects() -> list[str]:
    """List existing projects."""
    projects_dir = get_projects_dir()
    if not projects_dir.exists():
        return []
    return [d.name for d in projects_dir.iterdir() if d.is_dir()]


@app.command("list")
def list_templates():
    """📋 List all available project templates."""
    templates = list_available_templates()
    
    if not templates:
        console.print("[yellow]No templates found in templates/[/yellow]")
        return
    
    table = Table(title="Available Templates", show_header=True)
    table.add_column("Template Name", style="cyan")
    
    for template in templates:
        table.add_row(template)
    
    console.print(table)


@app.command("new")
def create_project(
    project_name: str = typer.Argument(..., help="Name of the project to create"),
    template: Optional[str] = typer.Option(
        None,
        "--template",
        "-t",
        help="Template to use (optional, will prompt if not provided)",
        autocompletion=list_available_templates,
    ),
    no_open: bool = typer.Option(
        False,
        "--no-open",
        help="Don't open the project in Cursor automatically",
    ),
):
    """🚀 Create a new project for the 30 Minute Vibe Coding Challenge."""
    # Get the script's directory
    script_dir = Path(__file__).parent
    
    # Define paths
    projects_dir = script_dir / "projects"
    commands_dir = script_dir / "context-engineering" / "commands"
    templates_dir = get_templates_dir()
    
    new_project_dir = projects_dir / project_name
    
    # Check if commands directory exists
    if not commands_dir.exists():
        console.print(f"[red]✗[/red] Error: commands directory not found at {commands_dir}")
        raise typer.Exit(1)
    
    # Check if project already exists
    if new_project_dir.exists():
        console.print(f"[red]✗[/red] Project '{project_name}' already exists in projects/")
        raise typer.Exit(1)
    
    # Interactive template selection if not provided
    if template is None:
        available_templates = list_available_templates()
        
        if available_templates:
            console.print("\n[bold cyan]Available templates:[/bold cyan]")
            console.print("[dim]0.[/dim] No template (empty project)")
            for idx, tmpl in enumerate(available_templates, 1):
                console.print(f"[dim]{idx}.[/dim] {tmpl}")
            
            choice = Prompt.ask(
                "\n[bold]Choose a template[/bold]",
                choices=[str(i) for i in range(len(available_templates) + 1)],
                default="0"
            )
            
            if choice != "0":
                template = available_templates[int(choice) - 1]
    
    # Create the new project directory
    new_project_dir.mkdir(parents=True, exist_ok=True)
    
    # If template is specified, copy it
    if template:
        template_dir = templates_dir / template
        if not template_dir.exists():
            console.print(f"[red]✗[/red] Template '{template}' not found in templates/")
            console.print("[yellow]💡 Use 'vibe list' to see available templates[/yellow]")
            shutil.rmtree(new_project_dir)  # Clean up
            raise typer.Exit(1)
        
        # Copy template contents (excluding __pycache__, .pyc, data/, etc.)
        ignore_patterns = ['__pycache__', '.pyc', '.pyo', 'data/', '.db']
        copy_tree(template_dir, new_project_dir, ignore_patterns)
        console.print(f"[green]✓[/green] Created project from template: [cyan]{template}[/cyan]")
    else:
        console.print(f"[green]✓[/green] Created project: [cyan]{project_name}[/cyan]")
    
    # Create .claude/commands and .cursor/commands directories
    claude_commands_dir = new_project_dir / ".claude" / "commands"
    cursor_commands_dir = new_project_dir / ".cursor" / "commands"
    
    claude_commands_dir.mkdir(parents=True, exist_ok=True)
    cursor_commands_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy command workflows (sdd/ and rpi/) into both directories
    for workflow_dir in ['sdd', 'rpi']:
        src_workflow = commands_dir / workflow_dir
        if src_workflow.exists():
            claude_workflow = claude_commands_dir / workflow_dir
            cursor_workflow = cursor_commands_dir / workflow_dir
            
            claude_workflow.mkdir(parents=True, exist_ok=True)
            cursor_workflow.mkdir(parents=True, exist_ok=True)
            
            copy_tree(src_workflow, claude_workflow)
            copy_tree(src_workflow, cursor_workflow)
    
    console.print("[green]✓[/green] Copied commands (sdd + rpi workflows) to .claude/commands/ and .cursor/commands/")
    
    # Open the project in a new Cursor window
    if not no_open:
        try:
            subprocess.run(["cursor", "-n", str(new_project_dir)], check=True)
            console.print("[green]✓[/green] Opened project in Cursor")
        except subprocess.CalledProcessError:
            console.print(f"[yellow]⚠[/yellow] Warning: Failed to open Cursor. Please open {new_project_dir} manually.")
        except FileNotFoundError:
            console.print(f"[yellow]⚠[/yellow] Warning: 'cursor' command not found. Please open {new_project_dir} manually.")
    
    console.print(f"\n[bold green]🎵 Happy coding![/bold green]")


@app.command("open")
def open_project(
    project_name: Optional[str] = typer.Argument(
        None,
        help="Name of the project to open (optional, will list projects if not provided)"
    ),
):
    """📂 Open an existing project in Cursor."""
    projects_dir = get_projects_dir()
    
    # If no project name provided, list all projects
    if project_name is None:
        existing_projects = list_existing_projects()
        
        if not existing_projects:
            console.print("[yellow]No projects found in projects/[/yellow]")
            console.print("[dim]Create a new project with:[/dim] [cyan]vibe new <project-name>[/cyan]")
            raise typer.Exit(0)
        
        table = Table(title="Existing Projects", show_header=True)
        table.add_column("Project Name", style="cyan")
        
        for project in existing_projects:
            table.add_row(project)
        
        console.print(table)
        console.print("\n[dim]Open a project with:[/dim] [cyan]vibe open <project-name>[/cyan]")
        raise typer.Exit(0)
    
    # Open specific project
    project_dir = projects_dir / project_name
    
    if not project_dir.exists():
        console.print(f"[red]✗[/red] Project '{project_name}' not found in projects/")
        console.print("[yellow]💡 Use 'vibe open' to see all projects[/yellow]")
        raise typer.Exit(1)
    
    try:
        subprocess.run(["cursor", "-n", str(project_dir)], check=True)
        console.print(f"[green]✓[/green] Opened project [cyan]{project_name}[/cyan] in Cursor")
    except subprocess.CalledProcessError:
        console.print(f"[yellow]⚠[/yellow] Warning: Failed to open Cursor. Please open {project_dir} manually.")
    except FileNotFoundError:
        console.print(f"[yellow]⚠[/yellow] Warning: 'cursor' command not found. Please open {project_dir} manually.")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
    ),
):
    """🎵 30 Minute Vibe Coding Challenge - Project Bootstrap Tool"""
    if version:
        console.print("[cyan]30-minute-vibe[/cyan] version [bold]0.1.0[/bold]")
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()

