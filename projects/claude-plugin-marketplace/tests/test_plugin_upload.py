"""Tests for plugin upload functionality."""
import pytest
import zipfile
import json
import tempfile
from pathlib import Path
from io import BytesIO

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from itsdangerous import URLSafeSerializer

from app.services.auth.models import User
from app.services.plugin.models import Plugin, PluginVersion
from app.services.plugin.routes import is_version_higher
from app.shared.config import settings


def get_session_cookie(user_id: int) -> str:
    """Helper to create a signed session cookie for testing."""
    serializer = URLSafeSerializer(settings.session_secret_key)
    session_data = {"user_id": user_id}
    signed_data = serializer.dumps(session_data)
    return f"plugin_marketplace_session={signed_data}; Path=/; HttpOnly"


def create_test_plugin_zip(name="test-plugin", version="1.0.0", add_readme=True):
    """Helper to create a test plugin zip in memory."""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        # Add plugin.json
        plugin_json = {
            "name": name,
            "version": version,
            "description": "A test plugin",
            "author": "Test Author"
        }
        zf.writestr(".claude-plugin/plugin.json", json.dumps(plugin_json))
        
        # Add README if requested
        if add_readme:
            zf.writestr("README.md", "# Test Plugin\n\nThis is a test.")
        
        # Add some component files
        zf.writestr("commands/test.py", "# Test command")
    
    zip_buffer.seek(0)
    return zip_buffer


class TestPluginUpload:
    """Tests for plugin upload functionality."""
    
    def test_upload_form_requires_auth(self, client):
        """Test that upload form requires authentication."""
        response = client.get("/plugins/upload", follow_redirects=False)
        
        # Should redirect to login or return 401
        assert response.status_code in [401, 302, 303]
    
    def test_upload_form_renders(self, client, test_db):
        """Test that upload form renders for authenticated users."""
        # Create a user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Make authenticated request
        cookies = {"plugin_marketplace_session": get_session_cookie(user.id)}
        response = client.get("/plugins/upload", cookies=cookies)
        
        assert response.status_code == 200
        assert b"Upload Plugin" in response.content
        assert b"plugin.json" in response.content
    
    def test_upload_valid_plugin(self, client, test_db):
        """Test uploading a valid plugin."""
        # Create and login user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed"
        )
        test_db.add(user)
        test_db.commit()
        
        # Create test plugin zip
        zip_buffer = create_test_plugin_zip()
        
        # Upload with authenticated request
        cookies = {"plugin_marketplace_session": get_session_cookie(user.id)}
        response = client.post(
            "/plugins/upload",
            files={"file": ("test_plugin.zip", zip_buffer, "application/zip")},
            data={"plugin_name": ""},
            cookies=cookies
        )
        
        assert response.status_code in [200, 302, 303]  # Success or redirect
        
        # Verify database records created
        plugin = test_db.query(Plugin).filter(Plugin.author_id == user.id).first()
        assert plugin is not None
        assert plugin.name == "test-plugin"
        assert plugin.is_published is True
        
        version = test_db.query(PluginVersion).filter(PluginVersion.plugin_id == plugin.id).first()
        assert version is not None
        assert version.version == "1.0.0"
        assert version.is_latest is True
    
    def test_upload_with_custom_name(self, client, test_db):
        """Test uploading with a custom plugin name."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed"
        )
        test_db.add(user)
        test_db.commit()
        
        zip_buffer = create_test_plugin_zip()
        
        cookies = {"plugin_marketplace_session": get_session_cookie(user.id)}
        response = client.post(
            "/plugins/upload",
            files={"file": ("test_plugin.zip", zip_buffer, "application/zip")},
            data={"plugin_name": "custom-name"},
            cookies=cookies
        )
        
        # Verify custom name used
        plugin = test_db.query(Plugin).filter(Plugin.author_id == user.id).first()
        assert plugin is not None
        assert plugin.name == "custom-name"
    
    def test_upload_invalid_plugin(self, client, test_db):
        """Test that invalid plugin is rejected."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed"
        )
        test_db.add(user)
        test_db.commit()
        
        # Create invalid zip (no plugin.json)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("README.md", "# Test")
        zip_buffer.seek(0)
        
        cookies = {"plugin_marketplace_session": get_session_cookie(user.id)}
        response = client.post(
            "/plugins/upload",
            files={"file": ("invalid.zip", zip_buffer, "application/zip")},
            data={"plugin_name": ""},
            cookies=cookies
        )
        
        assert response.status_code == 400
        assert b"plugin.json" in response.content
        
        # Verify no database records created
        plugin = test_db.query(Plugin).filter(Plugin.author_id == user.id).first()
        assert plugin is None


class TestVersionManagement:
    """Tests for version management during uploads."""
    
    def test_upload_new_version(self, client, test_db):
        """Test uploading a new version of existing plugin."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create initial plugin
        plugin = Plugin(
            name="test-plugin",
            display_name="Test Plugin",
            description="Test",
            author_id=user.id
        )
        test_db.add(plugin)
        test_db.commit()
        test_db.refresh(plugin)
        
        # Create initial version
        v1 = PluginVersion(
            plugin_id=plugin.id,
            version="1.0.0",
            file_path="/path/1.0.0.zip",
            plugin_metadata={},
            is_latest=True
        )
        test_db.add(v1)
        test_db.commit()
        
        # Upload new version
        zip_buffer = create_test_plugin_zip(version="1.0.1")
        
        cookies = {"plugin_marketplace_session": get_session_cookie(user.id)}
        response = client.post(
            "/plugins/upload",
            files={"file": ("test_plugin.zip", zip_buffer, "application/zip")},
            data={"plugin_name": "test-plugin"},
            cookies=cookies
        )
        
        assert response.status_code in [200, 302, 303]
        
        # Verify old version is no longer latest
        test_db.refresh(v1)
        assert v1.is_latest is False
        
        # Verify new version is latest
        v2 = test_db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin.id,
            PluginVersion.version == "1.0.1"
        ).first()
        assert v2 is not None
        assert v2.is_latest is True
    
    def test_upload_lower_version_rejected(self, client, test_db):
        """Test that uploading a lower version is rejected."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create plugin with version 1.0.1
        plugin = Plugin(
            name="test-plugin",
            display_name="Test Plugin",
            description="Test",
            author_id=user.id
        )
        test_db.add(plugin)
        test_db.commit()
        test_db.refresh(plugin)
        
        v1 = PluginVersion(
            plugin_id=plugin.id,
            version="1.0.1",
            file_path="/path/1.0.1.zip",
            plugin_metadata={},
            is_latest=True
        )
        test_db.add(v1)
        test_db.commit()
        
        # Try to upload version 1.0.0 (lower)
        zip_buffer = create_test_plugin_zip(version="1.0.0")
        
        cookies = {"plugin_marketplace_session": get_session_cookie(user.id)}
        response = client.post(
            "/plugins/upload",
            files={"file": ("test_plugin.zip", zip_buffer, "application/zip")},
            data={"plugin_name": "test-plugin"},
            cookies=cookies
        )
        
        assert response.status_code == 400
        assert b"must be higher" in response.content


class TestVersionComparison:
    """Tests for version comparison logic."""
    
    def test_version_comparison(self):
        """Test that version comparison works correctly."""
        assert is_version_higher("1.0.1", "1.0.0") is True
        assert is_version_higher("1.1.0", "1.0.9") is True
        assert is_version_higher("2.0.0", "1.9.9") is True
        assert is_version_higher("1.0.0", "1.0.1") is False
        assert is_version_higher("1.0.0", "1.0.0") is False
        assert is_version_higher("0.1.0", "1.0.0") is False
    
    def test_version_comparison_invalid(self):
        """Test that invalid versions return False."""
        assert is_version_higher("invalid", "1.0.0") is False
        assert is_version_higher("1.0.0", "invalid") is False
        assert is_version_higher("1.0", "1.0.0") is False

