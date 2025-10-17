"""Simplified comprehensive tests for cli.py - tests core functionality."""
import subprocess
import uuid
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from cli import (
    app, 
    get_templates_dir, 
    get_projects_dir, 
    list_available_templates, 
    list_existing_projects, 
    copy_tree
)


@pytest.fixture
def unique_name():
    """Generate unique project name for test isolation."""
    return f"testproj-{uuid.uuid4().hex[:8]}"


@pytest.fixture(autouse=True)
def cleanup_test_projects():
    """Cleanup any test projects after each test."""
    yield
    # Cleanup any projects that start with 'testproj-'
    projects_dir = get_projects_dir()
    if projects_dir.exists():
        for project in projects_dir.iterdir():
            if project.is_dir() and project.name.startswith("testproj-"):
                import shutil
                shutil.rmtree(project)


class TestHelperFunctions:
    """Test utility functions."""
    
    def test_get_templates_dir(self):
        """Test that get_templates_dir returns correct path."""
        templates_dir = get_templates_dir()
        assert templates_dir.name == "templates"
    
    def test_get_projects_dir(self):
        """Test that get_projects_dir returns correct path."""
        projects_dir = get_projects_dir()
        assert projects_dir.name == "projects"
    
    def test_list_available_templates(self):
        """Test listing available templates."""
        templates = list_available_templates()
        assert isinstance(templates, list)
        # Should include the fastapi template
        assert "fastapi-sqlite-jinja2" in templates
    
    def test_list_existing_projects(self):
        """Test listing existing projects."""
        projects = list_existing_projects()
        assert isinstance(projects, list)
    
    def test_copy_tree_simple(self, tmp_path):
        """Test basic directory copying."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "file1.txt").write_text("content1")
        (src / "file2.txt").write_text("content2")
        
        dst = tmp_path / "dst"
        dst.mkdir()
        
        copy_tree(src, dst)
        
        assert (dst / "file1.txt").read_text() == "content1"
        assert (dst / "file2.txt").read_text() == "content2"
    
    def test_copy_tree_with_ignore_patterns(self, tmp_path):
        """Test copying with ignore patterns."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "keep.txt").write_text("keep")
        (src / "ignore.pyc").write_text("ignore")
        (src / "__pycache__").mkdir()
        
        dst = tmp_path / "dst"
        dst.mkdir()
        
        copy_tree(src, dst, ignore_patterns=['__pycache__', '.pyc'])
        
        assert (dst / "keep.txt").exists()
        assert not (dst / "ignore.pyc").exists()
        assert not (dst / "__pycache__").exists()


class TestListCommand:
    """Test the 'list' command."""
    
    def test_list_templates(self):
        """Test listing templates."""
        runner = CliRunner()
        result = runner.invoke(app, ["list"])
        
        assert result.exit_code == 0
        assert "fastapi-sqlite-jinja2" in result.stdout


class TestNewCommand:
    """Test the 'new' command."""
    
    def test_new_project_no_template(self, unique_name):
        """Test creating a new project without a template."""
        runner = CliRunner()
        
        with patch("cli.subprocess.run"):
            # Provide "0" input to select "no template"
            result = runner.invoke(app, ["new", unique_name, "--no-open"], input="0\n")
        
        assert result.exit_code == 0
        assert f"Created project: {unique_name}" in result.stdout or "Created project" in result.stdout
        
        # Verify project was created
        project_dir = get_projects_dir() / unique_name
        assert project_dir.exists()
        assert (project_dir / ".claude").exists()
    
    def test_new_project_with_template(self, unique_name):
        """Test creating a project with a template."""
        runner = CliRunner()
        
        with patch("cli.subprocess.run"):
            result = runner.invoke(
                app,
                ["new", unique_name, "--template", "fastapi-sqlite-jinja2", "--no-open"]
            )
        
        assert result.exit_code == 0
        
        # Verify project and template files exist
        project_dir = get_projects_dir() / unique_name
        assert project_dir.exists()
        # Template should have been copied
        assert (project_dir / "pyproject.toml").exists() or (project_dir / "README.md").exists()
    
    def test_new_project_already_exists(self, unique_name):
        """Test creating a project that already exists."""
        runner = CliRunner()
        
        # Create the project first
        with patch("cli.subprocess.run"):
            runner.invoke(app, ["new", unique_name, "--no-open"], input="0\n")
        
        # Try to create it again
        result = runner.invoke(app, ["new", unique_name, "--no-open"], input="0\n")
        
        assert result.exit_code == 1
        assert "already exists" in result.stdout
    
    def test_new_project_invalid_template(self, unique_name):
        """Test creating a project with non-existent template."""
        runner = CliRunner()
        
        result = runner.invoke(
            app,
            ["new", unique_name, "--template", "nonexistent-template-xyz", "--no-open"]
        )
        
        assert result.exit_code == 1
        assert "not found" in result.stdout
    
    def test_new_project_opens_cursor(self, unique_name):
        """Test that project opens in Cursor by default."""
        runner = CliRunner()
        
        with patch("cli.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock()
            result = runner.invoke(app, ["new", unique_name], input="0\n")
        
        assert result.exit_code == 0
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "cursor" in args
    
    def test_new_project_no_open_flag(self, unique_name):
        """Test that --no-open prevents opening Cursor."""
        runner = CliRunner()
        
        with patch("cli.subprocess.run") as mock_run:
            result = runner.invoke(app, ["new", unique_name, "--no-open"], input="0\n")
        
        assert result.exit_code == 0
        mock_run.assert_not_called()
    
    def test_new_project_cursor_not_found(self, unique_name):
        """Test graceful handling when cursor command not found."""
        runner = CliRunner()
        
        with patch("cli.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            result = runner.invoke(app, ["new", unique_name], input="0\n")
        
        # Should still exit 0 with a warning
        assert result.exit_code == 0
        assert "cursor" in result.stdout.lower() or "warning" in result.stdout.lower()


class TestOpenCommand:
    """Test the 'open' command."""
    
    def test_open_lists_projects(self):
        """Test that open without arguments lists projects."""
        runner = CliRunner()
        result = runner.invoke(app, ["open"])
        
        assert result.exit_code == 0
        # Should show existing projects or a message
        assert "project" in result.stdout.lower() or "vibe open" in result.stdout
    
    def test_open_specific_project(self):
        """Test opening a specific existing project."""
        runner = CliRunner()
        
        # Use an existing project
        existing_projects = list_existing_projects()
        if existing_projects:
            project_name = existing_projects[0]
            
            with patch("cli.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock()
                result = runner.invoke(app, ["open", project_name])
            
            assert result.exit_code == 0
            mock_run.assert_called_once()
    
    def test_open_nonexistent_project(self):
        """Test opening a project that doesn't exist."""
        runner = CliRunner()
        result = runner.invoke(app, ["open", "nonexistent-project-xyz-123"])
        
        assert result.exit_code == 1
        assert "not found" in result.stdout


class TestMainCallback:
    """Test the main entry point."""
    
    def test_no_command_shows_help(self):
        """Test that running without command shows help."""
        runner = CliRunner()
        result = runner.invoke(app, [])
        
        assert result.exit_code == 0
        # Should show ASCII art or help
        assert "30" in result.stdout or "Vibe" in result.stdout or "Commands" in result.stdout
    
    def test_version_flag(self):
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])
        
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout
    
    def test_help_flag(self):
        """Test --help flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "30 Minute Vibe" in result.stdout or "Commands" in result.stdout


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_project_with_special_characters(self, cleanup_test_projects):
        """Test creating project with dashes and underscores."""
        runner = CliRunner()
        project_name = f"my-cool_project-{uuid.uuid4().hex[:6]}"
        
        with patch("cli.subprocess.run"):
            result = runner.invoke(app, ["new", project_name, "--no-open"], input="0\n")
        
        assert result.exit_code == 0
        assert (get_projects_dir() / project_name).exists()
        
        # Cleanup
        import shutil
        shutil.rmtree(get_projects_dir() / project_name, ignore_errors=True)
    
    def test_copy_tree_preserves_structure(self, tmp_path):
        """Test that nested directories are preserved."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "dir1" / "dir2").mkdir(parents=True)
        (src / "dir1" / "dir2" / "file.txt").write_text("nested")
        
        dst = tmp_path / "dst"
        dst.mkdir()
        
        copy_tree(src, dst)
        
        assert (dst / "dir1" / "dir2" / "file.txt").read_text() == "nested"

