"""Tests for plugin validation logic."""
import pytest
import zipfile
import json
import tempfile
from pathlib import Path
from app.services.plugin.validation import (
    validate_plugin_zip,
    validate_version_format,
    check_forbidden_files,
    ValidationError
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def valid_plugin_zip(temp_dir):
    """Create a valid plugin zip file."""
    zip_path = temp_dir / "valid_plugin.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        # Create plugin.json
        plugin_json = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "author": "Test Author"
        }
        zf.writestr(".claude-plugin/plugin.json", json.dumps(plugin_json))
        
        # Add some dummy files
        zf.writestr("commands/test.py", "# Test command")
        zf.writestr("README.md", "# Test Plugin\n\nThis is a test.")
    
    return zip_path


@pytest.fixture
def invalid_json_zip(temp_dir):
    """Create a plugin zip with invalid JSON."""
    zip_path = temp_dir / "invalid_json.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr(".claude-plugin/plugin.json", "{invalid json content")
    
    return zip_path


@pytest.fixture
def missing_plugin_json_zip(temp_dir):
    """Create a plugin zip without plugin.json."""
    zip_path = temp_dir / "missing_json.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("README.md", "# Test")
    
    return zip_path


@pytest.fixture
def missing_fields_zip(temp_dir):
    """Create a plugin zip with missing required fields."""
    zip_path = temp_dir / "missing_fields.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        plugin_json = {
            "name": "test-plugin"
            # Missing version and description
        }
        zf.writestr(".claude-plugin/plugin.json", json.dumps(plugin_json))
    
    return zip_path


@pytest.fixture
def invalid_version_zip(temp_dir):
    """Create a plugin zip with invalid version format."""
    zip_path = temp_dir / "invalid_version.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        plugin_json = {
            "name": "test-plugin",
            "version": "1.0",  # Invalid - should be x.y.z
            "description": "A test plugin"
        }
        zf.writestr(".claude-plugin/plugin.json", json.dumps(plugin_json))
    
    return zip_path


@pytest.fixture
def forbidden_files_zip(temp_dir):
    """Create a plugin zip with forbidden executable files."""
    zip_path = temp_dir / "forbidden_files.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        plugin_json = {
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "A test plugin"
        }
        zf.writestr(".claude-plugin/plugin.json", json.dumps(plugin_json))
        zf.writestr("malicious.exe", "fake exe content")
    
    return zip_path


class TestPluginValidation:
    """Tests for plugin validation functions."""
    
    def test_validate_valid_plugin(self, valid_plugin_zip):
        """Test that a valid plugin passes validation."""
        metadata = validate_plugin_zip(valid_plugin_zip)
        
        assert metadata["name"] == "test-plugin"
        assert metadata["version"] == "1.0.0"
        assert metadata["description"] == "A test plugin"
    
    def test_validate_invalid_json(self, invalid_json_zip):
        """Test that invalid JSON is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_plugin_zip(invalid_json_zip)
        
        assert "Invalid JSON" in str(exc_info.value)
    
    def test_validate_missing_plugin_json(self, missing_plugin_json_zip):
        """Test that missing plugin.json is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_plugin_zip(missing_plugin_json_zip)
        
        assert "must contain .claude-plugin/plugin.json" in str(exc_info.value)
    
    def test_validate_missing_required_fields(self, missing_fields_zip):
        """Test that missing required fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_plugin_zip(missing_fields_zip)
        
        error_msg = str(exc_info.value)
        assert "Missing required fields" in error_msg
        assert "version" in error_msg
        assert "description" in error_msg
    
    def test_validate_invalid_version_format(self, invalid_version_zip):
        """Test that invalid version format is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_plugin_zip(invalid_version_zip)
        
        assert "Invalid version format" in str(exc_info.value)
    
    def test_validate_forbidden_files(self, forbidden_files_zip):
        """Test that executable files are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            validate_plugin_zip(forbidden_files_zip)
        
        assert "Forbidden file type" in str(exc_info.value)
        assert ".exe" in str(exc_info.value)
    
    def test_validate_non_zip_file(self, temp_dir):
        """Test that non-ZIP files are rejected."""
        non_zip = temp_dir / "not_a_zip.txt"
        non_zip.write_text("This is not a zip file")
        
        with pytest.raises(ValidationError) as exc_info:
            validate_plugin_zip(non_zip)
        
        assert "not a valid ZIP file" in str(exc_info.value)


class TestVersionFormat:
    """Tests for version format validation."""
    
    def test_valid_versions(self):
        """Test that valid semantic versions pass."""
        assert validate_version_format("1.0.0") is True
        assert validate_version_format("0.0.1") is True
        assert validate_version_format("10.20.30") is True
        assert validate_version_format("999.999.999") is True
    
    def test_invalid_versions(self):
        """Test that invalid versions fail."""
        assert validate_version_format("1.0") is False
        assert validate_version_format("1") is False
        assert validate_version_format("1.0.0.0") is False
        assert validate_version_format("v1.0.0") is False
        assert validate_version_format("1.0.a") is False
        assert validate_version_format("") is False
        assert validate_version_format("1.0.0-beta") is False
    
    def test_non_string_versions(self):
        """Test that non-string inputs fail."""
        assert validate_version_format(None) is False
        assert validate_version_format(1.0) is False
        assert validate_version_format(100) is False


class TestForbiddenFiles:
    """Tests for forbidden file checking."""
    
    def test_clean_zip(self, temp_dir):
        """Test that a zip with no forbidden files passes."""
        zip_path = temp_dir / "clean.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("commands/test.py", "# Python file")
            zf.writestr("README.md", "# Readme")
            zf.writestr("package.json", "{}")
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Should not raise
            check_forbidden_files(zf)
    
    def test_forbidden_extensions(self, temp_dir):
        """Test that all forbidden extensions are caught."""
        forbidden = ['.exe', '.sh', '.bat', '.cmd', '.dll', '.so', '.dylib']
        
        for ext in forbidden:
            zip_path = temp_dir / f"test{ext}.zip"
            
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr(f"malicious{ext}", "fake content")
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                with pytest.raises(ValidationError) as exc_info:
                    check_forbidden_files(zf)
                
                assert "Forbidden file type" in str(exc_info.value)
                assert ext in str(exc_info.value)
    
    def test_case_insensitive(self, temp_dir):
        """Test that forbidden file check is case-insensitive."""
        zip_path = temp_dir / "uppercase.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("MALICIOUS.EXE", "fake content")
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            with pytest.raises(ValidationError) as exc_info:
                check_forbidden_files(zf)
            
            assert "Forbidden file type" in str(exc_info.value)

