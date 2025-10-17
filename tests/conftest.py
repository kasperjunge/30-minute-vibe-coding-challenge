"""Pytest fixtures for CLI tests."""
import pytest
import uuid
from pathlib import Path
from typer.testing import CliRunner


@pytest.fixture
def runner():
    """Typer CLI test runner."""
    return CliRunner(mix_stderr=False)


@pytest.fixture
def unique_project_name():
    """Generate a unique project name for each test."""
    return f"test-project-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def mock_workspace(tmp_path):
    """
    Create a mock workspace with templates, projects, and command directories.
    
    Returns a dict with paths to different workspace components.
    """
    # Create directory structure
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    
    commands_dir = tmp_path / ".claude"
    commands_dir.mkdir()
    
    rules_dir = tmp_path / ".cursor"
    rules_dir.mkdir()
    
    # Create sample template
    sample_template = templates_dir / "sample-template"
    sample_template.mkdir()
    (sample_template / "README.md").write_text("# Sample Template")
    (sample_template / "main.py").write_text("print('hello')")
    
    # Create another template
    fastapi_template = templates_dir / "fastapi-sqlite-jinja2"
    fastapi_template.mkdir()
    (fastapi_template / "README.md").write_text("# FastAPI Template")
    (fastapi_template / "pyproject.toml").write_text("[project]\nname='test'")
    
    # Create command workflows
    for workflow in ["sdd", "rpi", "humanlayer"]:
        workflow_dir = commands_dir / workflow
        workflow_dir.mkdir()
        (workflow_dir / "command.md").write_text(f"# {workflow} command")
    
    # Create rules
    (rules_dir / "rules.md").write_text("# Cursor Rules")
    
    # Create existing project
    existing_project = projects_dir / "existing-project"
    existing_project.mkdir()
    (existing_project / "README.md").write_text("# Existing Project")
    
    return {
        "root": tmp_path,
        "templates": templates_dir,
        "projects": projects_dir,
        "commands": commands_dir,
        "rules": rules_dir,
    }


@pytest.fixture
def mock_cli_script(tmp_path, mock_workspace):
    """
    Create a mock cli.py file in the workspace.
    This allows us to test path resolution.
    """
    cli_file = mock_workspace["root"] / "cli.py"
    cli_file.write_text("# Mock CLI file")
    return cli_file

