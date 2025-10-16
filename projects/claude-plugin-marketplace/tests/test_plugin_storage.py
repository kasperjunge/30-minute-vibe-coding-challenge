"""Tests for plugin storage logic."""
import pytest
import zipfile
import json
import tempfile
import shutil
from pathlib import Path
from app.services.plugin.storage import (
    get_plugin_directory,
    store_plugin_zip,
    extract_plugin_metadata,
    count_components,
    delete_plugin_files,
    get_plugin_zip_path,
    PLUGINS_DIR
)


@pytest.fixture
def temp_plugins_dir(monkeypatch, tmp_path):
    """Create a temporary plugins directory and patch the global PLUGINS_DIR."""
    temp_dir = tmp_path / "plugins"
    temp_dir.mkdir()
    
    # Patch the module-level PLUGINS_DIR
    import app.services.plugin.storage as storage_module
    monkeypatch.setattr(storage_module, 'PLUGINS_DIR', temp_dir)
    
    yield temp_dir
    
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_plugin_zip(tmp_path):
    """Create a sample plugin zip file."""
    zip_path = tmp_path / "test_plugin.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        # Add plugin.json
        plugin_json = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "author": "Test Author"
        }
        zf.writestr(".claude-plugin/plugin.json", json.dumps(plugin_json))
        
        # Add README
        zf.writestr("README.md", "# Test Plugin\n\nThis is a test plugin.")
        
        # Add some component files
        zf.writestr("commands/test_command.py", "# Test command")
        zf.writestr("commands/another_command.py", "# Another command")
        zf.writestr("agents/test_agent.py", "# Test agent")
        zf.writestr("hooks/test_hook.py", "# Test hook")
    
    return zip_path


class TestPluginDirectory:
    """Tests for plugin directory management."""
    
    def test_get_plugin_directory(self, temp_plugins_dir):
        """Test that get_plugin_directory creates the directory."""
        plugin_dir = get_plugin_directory("testuser", "test-plugin")
        
        assert plugin_dir.exists()
        assert plugin_dir.is_dir()
        assert str(plugin_dir).endswith("testuser/test-plugin")
    
    def test_get_plugin_directory_creates_parents(self, temp_plugins_dir):
        """Test that parent directories are created."""
        plugin_dir = get_plugin_directory("newuser", "new-plugin")
        
        assert plugin_dir.exists()
        assert plugin_dir.parent.exists()  # username directory
        assert plugin_dir.parent.parent.exists()  # plugins directory
    
    def test_get_plugin_directory_idempotent(self, temp_plugins_dir):
        """Test that calling get_plugin_directory multiple times is safe."""
        dir1 = get_plugin_directory("testuser", "test-plugin")
        dir2 = get_plugin_directory("testuser", "test-plugin")
        
        assert dir1 == dir2
        assert dir1.exists()


class TestStorePluginZip:
    """Tests for storing plugin zip files."""
    
    def test_store_plugin_zip(self, temp_plugins_dir, sample_plugin_zip):
        """Test that plugin zip is stored correctly."""
        dest_path = store_plugin_zip(sample_plugin_zip, "testuser", "test-plugin", "1.0.0")
        
        assert dest_path.exists()
        assert dest_path.name == "1.0.0.zip"
        assert "testuser/test-plugin" in str(dest_path)
        assert zipfile.is_zipfile(dest_path)
    
    def test_store_multiple_versions(self, temp_plugins_dir, sample_plugin_zip):
        """Test that multiple versions can be stored."""
        v1_path = store_plugin_zip(sample_plugin_zip, "testuser", "test-plugin", "1.0.0")
        v2_path = store_plugin_zip(sample_plugin_zip, "testuser", "test-plugin", "1.0.1")
        
        assert v1_path.exists()
        assert v2_path.exists()
        assert v1_path != v2_path
        assert v1_path.parent == v2_path.parent


class TestExtractMetadata:
    """Tests for metadata extraction."""
    
    def test_extract_plugin_metadata(self, temp_plugins_dir, sample_plugin_zip):
        """Test that metadata is extracted correctly."""
        metadata = extract_plugin_metadata(
            sample_plugin_zip,
            "testuser",
            "test-plugin",
            "1.0.0"
        )
        
        assert metadata["plugin_json"] is not None
        assert metadata["plugin_json"]["name"] == "test-plugin"
        assert metadata["plugin_json"]["version"] == "1.0.0"
        assert metadata["readme_content"] is not None
        assert "Test Plugin" in metadata["readme_content"]
        assert metadata["components"] is not None
    
    def test_metadata_files_created(self, temp_plugins_dir, sample_plugin_zip):
        """Test that metadata files are written to disk."""
        extract_plugin_metadata(
            sample_plugin_zip,
            "testuser",
            "test-plugin",
            "1.0.0"
        )
        
        metadata_dir = temp_plugins_dir / "testuser" / "test-plugin" / "metadata" / "1.0.0"
        assert metadata_dir.exists()
        assert (metadata_dir / "plugin.json").exists()
        assert (metadata_dir / "README.md").exists()
    
    def test_extract_without_readme(self, temp_plugins_dir, tmp_path):
        """Test extraction when README.md is not present."""
        zip_path = tmp_path / "no_readme.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            plugin_json = {"name": "test", "version": "1.0.0", "description": "Test"}
            zf.writestr(".claude-plugin/plugin.json", json.dumps(plugin_json))
        
        metadata = extract_plugin_metadata(zip_path, "testuser", "test-plugin", "1.0.0")
        
        assert metadata["plugin_json"] is not None
        assert metadata["readme_content"] is None
    
    def test_component_counts(self, temp_plugins_dir, sample_plugin_zip):
        """Test that component counts are correct."""
        metadata = extract_plugin_metadata(
            sample_plugin_zip,
            "testuser",
            "test-plugin",
            "1.0.0"
        )
        
        components = metadata["components"]
        assert components["commands"] == 2  # test_command.py and another_command.py
        assert components["agents"] == 1    # test_agent.py
        assert components["skills"] == 0    # None
        assert components["hooks"] == 1     # test_hook.py
        assert components["mcp_servers"] == 0  # None


class TestCountComponents:
    """Tests for component counting."""
    
    def test_count_components_empty_zip(self, tmp_path):
        """Test counting components in an empty zip."""
        zip_path = tmp_path / "empty.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            plugin_json = {"name": "test", "version": "1.0.0", "description": "Test"}
            zf.writestr(".claude-plugin/plugin.json", json.dumps(plugin_json))
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            counts = count_components(zf)
        
        assert all(count == 0 for count in counts.values())
    
    def test_count_components_nested_files(self, tmp_path):
        """Test that nested files are not counted."""
        zip_path = tmp_path / "nested.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("commands/test.py", "# Command")
            zf.writestr("commands/subdir/nested.py", "# Nested file")
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            counts = count_components(zf)
        
        # Should only count direct children
        assert counts["commands"] == 1


class TestDeletePluginFiles:
    """Tests for plugin file deletion."""
    
    def test_delete_plugin_files(self, temp_plugins_dir, sample_plugin_zip):
        """Test that plugin files are deleted."""
        # First store a plugin
        store_plugin_zip(sample_plugin_zip, "testuser", "test-plugin", "1.0.0")
        extract_plugin_metadata(sample_plugin_zip, "testuser", "test-plugin", "1.0.0")
        
        plugin_dir = temp_plugins_dir / "testuser" / "test-plugin"
        assert plugin_dir.exists()
        
        # Delete it
        delete_plugin_files("testuser", "test-plugin")
        
        assert not plugin_dir.exists()
    
    def test_delete_nonexistent_plugin(self, temp_plugins_dir):
        """Test that deleting a nonexistent plugin doesn't error."""
        # Should not raise an exception
        delete_plugin_files("testuser", "nonexistent-plugin")


class TestGetPluginZipPath:
    """Tests for getting plugin zip paths."""
    
    def test_get_existing_zip_path(self, temp_plugins_dir, sample_plugin_zip):
        """Test getting path to an existing zip."""
        store_plugin_zip(sample_plugin_zip, "testuser", "test-plugin", "1.0.0")
        
        zip_path = get_plugin_zip_path("testuser", "test-plugin", "1.0.0")
        
        assert zip_path is not None
        assert zip_path.exists()
        assert zip_path.name == "1.0.0.zip"
    
    def test_get_nonexistent_zip_path(self, temp_plugins_dir):
        """Test getting path to a nonexistent zip."""
        zip_path = get_plugin_zip_path("testuser", "nonexistent-plugin", "1.0.0")
        
        assert zip_path is None

