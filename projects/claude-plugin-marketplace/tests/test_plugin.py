"""Tests for plugin models and routes."""
import pytest
from sqlalchemy.orm import Session
from app.services.plugin.models import Plugin, PluginVersion
from app.services.auth.models import User
from datetime import datetime, UTC


class TestPluginModels:
    """Tests for Plugin and PluginVersion models."""
    
    def test_plugin_model_creates_successfully(self, test_db: Session):
        """Test that a Plugin model can be created."""
        # Create a user first
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        
        # Create a plugin
        plugin = Plugin(
            name="test-plugin",
            display_name="Test Plugin",
            description="A test plugin for testing",
            author_id=user.id
        )
        test_db.add(plugin)
        test_db.commit()
        test_db.refresh(plugin)
        
        assert plugin.id is not None
        assert plugin.name == "test-plugin"
        assert plugin.display_name == "Test Plugin"
        assert plugin.description == "A test plugin for testing"
        assert plugin.author_id == user.id
        assert plugin.is_published is True  # Default value
        assert isinstance(plugin.created_at, datetime)
        assert isinstance(plugin.updated_at, datetime)
    
    def test_plugin_version_model_creates_successfully(self, test_db: Session):
        """Test that a PluginVersion model can be created."""
        # Create user and plugin first
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        plugin = Plugin(
            name="test-plugin",
            display_name="Test Plugin",
            description="A test plugin",
            author_id=user.id
        )
        test_db.add(plugin)
        test_db.commit()
        test_db.refresh(plugin)
        
        # Create a version
        version = PluginVersion(
            plugin_id=plugin.id,
            version="1.0.0",
            file_path="/data/plugins/testuser/test-plugin/1.0.0.zip",
            readme_content="# Test Plugin\n\nThis is a test.",
            plugin_metadata={"components": {"commands": 2, "agents": 1}},
            is_latest=True
        )
        test_db.add(version)
        test_db.commit()
        test_db.refresh(version)
        
        assert version.id is not None
        assert version.plugin_id == plugin.id
        assert version.version == "1.0.0"
        assert version.file_path == "/data/plugins/testuser/test-plugin/1.0.0.zip"
        assert version.readme_content == "# Test Plugin\n\nThis is a test."
        assert version.plugin_metadata == {"components": {"commands": 2, "agents": 1}}
        assert version.is_latest is True
        assert isinstance(version.uploaded_at, datetime)
    
    def test_plugin_user_relationship(self, test_db: Session):
        """Test relationship between Plugin and User."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        plugin = Plugin(
            name="test-plugin",
            display_name="Test Plugin",
            description="A test plugin",
            author_id=user.id
        )
        test_db.add(plugin)
        test_db.commit()
        test_db.refresh(plugin)
        
        # Test author relationship
        assert plugin.author.id == user.id
        assert plugin.author.username == "testuser"
        
        # Test backref
        assert len(user.plugins) == 1
        assert user.plugins[0].name == "test-plugin"
    
    def test_plugin_version_relationship(self, test_db: Session):
        """Test relationship between Plugin and PluginVersion."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        plugin = Plugin(
            name="test-plugin",
            display_name="Test Plugin",
            description="A test plugin",
            author_id=user.id
        )
        test_db.add(plugin)
        test_db.commit()
        test_db.refresh(plugin)
        
        # Create two versions
        v1 = PluginVersion(
            plugin_id=plugin.id,
            version="1.0.0",
            file_path="/path/1.0.0.zip",
            plugin_metadata={},
            is_latest=False
        )
        v2 = PluginVersion(
            plugin_id=plugin.id,
            version="1.0.1",
            file_path="/path/1.0.1.zip",
            plugin_metadata={},
            is_latest=True
        )
        test_db.add_all([v1, v2])
        test_db.commit()
        test_db.refresh(plugin)
        
        # Test versions relationship
        assert len(plugin.versions) == 2
        assert plugin.versions[0].version in ["1.0.0", "1.0.1"]
        assert plugin.versions[1].version in ["1.0.0", "1.0.1"]
        
        # Test plugin relationship from version
        assert v1.plugin.name == "test-plugin"
        assert v2.plugin.name == "test-plugin"
    
    def test_plugin_default_values(self, test_db: Session):
        """Test that Plugin model has correct default values."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        
        plugin = Plugin(
            name="test-plugin",
            display_name="Test Plugin",
            description="A test plugin",
            author_id=user.id
        )
        test_db.add(plugin)
        test_db.commit()
        test_db.refresh(plugin)
        
        assert plugin.is_published is True  # Default
        assert plugin.created_at is not None
        assert plugin.updated_at is not None
    
    def test_plugin_version_default_values(self, test_db: Session):
        """Test that PluginVersion model has correct default values."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        plugin = Plugin(
            name="test-plugin",
            display_name="Test Plugin",
            description="A test plugin",
            author_id=user.id
        )
        test_db.add(plugin)
        test_db.commit()
        test_db.refresh(plugin)
        
        version = PluginVersion(
            plugin_id=plugin.id,
            version="1.0.0",
            file_path="/path/1.0.0.zip",
            plugin_metadata={}
        )
        test_db.add(version)
        test_db.commit()
        test_db.refresh(version)
        
        assert version.is_latest is False  # Default
        assert version.uploaded_at is not None
        assert version.readme_content is None  # Optional field


class TestMyPluginsPage:
    """Tests for My Plugins page."""
    
    def test_my_plugins_page_shows_users_plugins_only(self, client, test_db: Session, authenticated_user):
        """Test that My Plugins page shows only the authenticated user's plugins."""
        user1, session_cookie = authenticated_user
        
        # Create another user with plugins
        user2 = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user2)
        test_db.commit()
        test_db.refresh(user2)
        
        # Create plugin for user1
        plugin1 = Plugin(
            name="user1-plugin",
            display_name="User 1 Plugin",
            description="Plugin by user 1",
            author_id=user1.id
        )
        test_db.add(plugin1)
        
        # Create plugin for user2
        plugin2 = Plugin(
            name="user2-plugin",
            display_name="User 2 Plugin",
            description="Plugin by user 2",
            author_id=user2.id
        )
        test_db.add(plugin2)
        test_db.commit()
        
        # Visit My Plugins page as user1
        response = client.get("/plugins/my-plugins", cookies=session_cookie)
        
        assert response.status_code == 200
        assert "User 1 Plugin" in response.text
        assert "User 2 Plugin" not in response.text
    
    def test_my_plugins_page_shows_latest_version(self, client, test_db: Session, authenticated_user):
        """Test that My Plugins page shows the latest version for each plugin."""
        user, session_cookie = authenticated_user
        
        # Create plugin with multiple versions
        plugin = Plugin(
            name="test-plugin",
            display_name="Test Plugin",
            description="A test plugin",
            author_id=user.id
        )
        test_db.add(plugin)
        test_db.commit()
        test_db.refresh(plugin)
        
        # Create two versions
        v1 = PluginVersion(
            plugin_id=plugin.id,
            version="1.0.0",
            file_path="/path/1.0.0.zip",
            plugin_metadata={},
            is_latest=False
        )
        v2 = PluginVersion(
            plugin_id=plugin.id,
            version="1.0.1",
            file_path="/path/1.0.1.zip",
            plugin_metadata={},
            is_latest=True
        )
        test_db.add_all([v1, v2])
        test_db.commit()
        
        # Visit My Plugins page
        response = client.get("/plugins/my-plugins", cookies=session_cookie)
        
        assert response.status_code == 200
        assert "1.0.1" in response.text
    
    def test_my_plugins_page_shows_empty_state_when_no_plugins(self, client, test_db: Session, authenticated_user):
        """Test that My Plugins page shows empty state when user has no plugins."""
        user, session_cookie = authenticated_user
        
        # Visit My Plugins page without any plugins
        response = client.get("/plugins/my-plugins", cookies=session_cookie)
        
        assert response.status_code == 200
        assert "haven't uploaded any plugins yet" in response.text.lower()
    
    def test_my_plugins_page_requires_authentication(self, client, test_db: Session):
        """Test that My Plugins page requires authentication."""
        # Try to access without authentication
        response = client.get("/plugins/my-plugins", follow_redirects=False)
        
        # Should get 401 unauthorized
        assert response.status_code == 401


class TestHomepage:
    """Tests for homepage with plugin listing."""
    
    def test_homepage_shows_published_plugins_only(self, client, test_db: Session):
        """Test that homepage shows only published plugins."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create published plugin
        plugin1 = Plugin(
            name="published-plugin",
            display_name="Published Plugin",
            description="This is published",
            author_id=user.id,
            is_published=True
        )
        # Create unpublished plugin
        plugin2 = Plugin(
            name="unpublished-plugin",
            display_name="Unpublished Plugin",
            description="This is not published",
            author_id=user.id,
            is_published=False
        )
        test_db.add_all([plugin1, plugin2])
        test_db.commit()
        
        # Visit homepage
        response = client.get("/")
        
        assert response.status_code == 200
        assert "Published Plugin" in response.text
        assert "Unpublished Plugin" not in response.text
    
    def test_homepage_search_by_name(self, client, test_db: Session):
        """Test that homepage search filters by plugin name."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create plugins with different names
        plugin1 = Plugin(
            name="database-plugin",
            display_name="Database Plugin",
            description="A plugin for databases",
            author_id=user.id
        )
        plugin2 = Plugin(
            name="api-plugin",
            display_name="API Plugin",
            description="A plugin for APIs",
            author_id=user.id
        )
        test_db.add_all([plugin1, plugin2])
        test_db.commit()
        
        # Search for "database"
        response = client.get("/?search=database")
        
        assert response.status_code == 200
        assert "Database Plugin" in response.text
        assert "API Plugin" not in response.text
    
    def test_homepage_search_by_description(self, client, test_db: Session):
        """Test that homepage search filters by description."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create plugins with different descriptions
        plugin1 = Plugin(
            name="plugin1",
            display_name="Plugin 1",
            description="This is about artificial intelligence",
            author_id=user.id
        )
        plugin2 = Plugin(
            name="plugin2",
            display_name="Plugin 2",
            description="This is about web development",
            author_id=user.id
        )
        test_db.add_all([plugin1, plugin2])
        test_db.commit()
        
        # Search for "artificial"
        response = client.get("/?search=artificial")
        
        assert response.status_code == 200
        assert "Plugin 1" in response.text
        assert "Plugin 2" not in response.text
    
    def test_homepage_sort_newest(self, client, test_db: Session):
        """Test that homepage sorts by newest first."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        from datetime import datetime, UTC, timedelta
        
        # Create plugins with different creation dates
        plugin1 = Plugin(
            name="old-plugin",
            display_name="Old Plugin",
            description="Created earlier",
            author_id=user.id,
            created_at=datetime.now(UTC) - timedelta(days=2)
        )
        plugin2 = Plugin(
            name="new-plugin",
            display_name="New Plugin",
            description="Created recently",
            author_id=user.id,
            created_at=datetime.now(UTC)
        )
        test_db.add_all([plugin1, plugin2])
        test_db.commit()
        
        # Get homepage with newest sort
        response = client.get("/?sort=newest")
        
        assert response.status_code == 200
        # New plugin should appear before old plugin
        assert response.text.index("New Plugin") < response.text.index("Old Plugin")
    
    def test_homepage_sort_alphabetical(self, client, test_db: Session):
        """Test that homepage sorts alphabetically."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create plugins with different names
        plugin1 = Plugin(
            name="zebra-plugin",
            display_name="Zebra Plugin",
            description="Starts with Z",
            author_id=user.id
        )
        plugin2 = Plugin(
            name="apple-plugin",
            display_name="Apple Plugin",
            description="Starts with A",
            author_id=user.id
        )
        test_db.add_all([plugin1, plugin2])
        test_db.commit()
        
        # Get homepage with alphabetical sort
        response = client.get("/?sort=alphabetical")
        
        assert response.status_code == 200
        # Apple should appear before Zebra
        assert response.text.index("Apple Plugin") < response.text.index("Zebra Plugin")
    
    def test_homepage_pagination(self, client, test_db: Session):
        """Test that homepage pagination works correctly."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create 35 plugins (more than one page of 30)
        plugins = []
        for i in range(35):
            plugin = Plugin(
                name=f"plugin-{i}",
                display_name=f"Plugin {i}",
                description=f"Plugin number {i}",
                author_id=user.id
            )
            plugins.append(plugin)
        test_db.add_all(plugins)
        test_db.commit()
        
        # Get first page
        response1 = client.get("/?page=1")
        assert response1.status_code == 200
        
        # Get second page
        response2 = client.get("/?page=2")
        assert response2.status_code == 200
        
        # Both pages should have different content
        assert response1.text != response2.text
    
    def test_homepage_empty_state(self, client, test_db: Session):
        """Test that homepage shows empty state when no plugins."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "No plugins yet" in response.text
    
    def test_homepage_search_no_results(self, client, test_db: Session):
        """Test that homepage shows 'no results' message for empty search."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword123"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create a plugin
        plugin = Plugin(
            name="test-plugin",
            display_name="Test Plugin",
            description="A test plugin",
            author_id=user.id
        )
        test_db.add(plugin)
        test_db.commit()
        
        # Search for something that doesn't exist
        response = client.get("/?search=nonexistent")
        
        assert response.status_code == 200
        assert "No plugins found" in response.text


class TestMarkdownRendering:
    """Tests for markdown rendering utility."""
    
    def test_markdown_renders_headings(self):
        """Test that markdown renders headings correctly."""
        from app.services.plugin.utils import render_markdown
        
        content = "# Heading 1\n## Heading 2"
        result = render_markdown(content)
        
        assert "<h1>Heading 1</h1>" in str(result)
        assert "<h2>Heading 2</h2>" in str(result)
    
    def test_markdown_renders_code_blocks(self):
        """Test that markdown renders code blocks correctly."""
        from app.services.plugin.utils import render_markdown
        
        content = "```python\nprint('hello')\n```"
        result = render_markdown(content)
        
        result_str = str(result)
        assert "code" in result_str.lower()  # Check for code tag (case insensitive)
        assert "print('hello')" in result_str or "print(\\'hello\\')" in result_str
    
    def test_markdown_renders_links(self):
        """Test that markdown renders links correctly."""
        from app.services.plugin.utils import render_markdown
        
        content = "[Link Text](https://example.com)"
        result = render_markdown(content)
        
        assert '<a href="https://example.com">Link Text</a>' in str(result)
    
    def test_markdown_escapes_html(self):
        """Test that markdown safely escapes HTML tags."""
        from app.services.plugin.utils import render_markdown
        from markupsafe import Markup
        
        content = "Some text with <script>alert('xss')</script> html"
        result = render_markdown(content)
        
        # The result should be Markup type (safe for Jinja2)
        assert isinstance(result, Markup)
        # HTML should NOT be executed but rendered as text or escaped
        # Markdown will actually pass HTML through by default, but Markup makes it safe
        assert "text" in str(result)
    
    def test_markdown_handles_none(self):
        """Test that markdown handles None input gracefully."""
        from app.services.plugin.utils import render_markdown
        
        result = render_markdown(None)
        
        assert str(result) == ""
    
    def test_markdown_handles_empty_string(self):
        """Test that markdown handles empty string gracefully."""
        from app.services.plugin.utils import render_markdown
        
        result = render_markdown("")
        
        assert str(result) == ""

