"""Tests for skill builder utilities."""
import pytest
import zipfile
from io import BytesIO
from app.services.skill.builder import create_skill_md, create_single_skill_plugin


class TestCreateSkillMd:
    """Tests for create_skill_md function."""

    def test_basic_skill_md(self):
        """Test creating a basic SKILL.md without tags or examples."""
        content = create_skill_md(
            name="Test Skill",
            description="A test skill for unit testing",
            instructions="This is a test skill.\n\nIt does testing things."
        )

        # Should start with YAML frontmatter
        assert content.startswith("---\n")

        # Should contain description
        assert "description: A test skill for unit testing" in content

        # Should close frontmatter
        assert "---\n\n" in content

        # Should contain skill name as header
        assert "# Test Skill\n\n" in content

        # Should contain instructions
        assert "This is a test skill.\n\nIt does testing things." in content

        # Should not contain Examples section
        assert "## Examples" not in content

    def test_skill_md_with_tags(self):
        """Test creating SKILL.md with tags."""
        content = create_skill_md(
            name="Tagged Skill",
            description="A skill with tags",
            instructions="Instructions here",
            tags=["testing", "unit-test", "automation"]
        )

        # Tags should be in frontmatter as JSON array
        assert 'tags: ["testing", "unit-test", "automation"]' in content

    def test_skill_md_with_examples(self):
        """Test creating SKILL.md with examples section."""
        content = create_skill_md(
            name="Example Skill",
            description="A skill with examples",
            instructions="Instructions here",
            examples="Example 1: Do this\nExample 2: Do that"
        )

        # Should contain Examples section
        assert "## Examples\n\n" in content
        assert "Example 1: Do this\nExample 2: Do that" in content

    def test_skill_md_complete(self):
        """Test creating complete SKILL.md with all fields."""
        content = create_skill_md(
            name="Complete Skill",
            description="A complete skill",
            instructions="Full instructions",
            examples="Example usage",
            tags=["complete", "full"]
        )

        # Check all parts are present
        assert "---\n" in content
        assert "description: A complete skill" in content
        assert 'tags: ["complete", "full"]' in content
        assert "# Complete Skill\n\n" in content
        assert "Full instructions" in content
        assert "## Examples\n\n" in content
        assert "Example usage" in content

    def test_empty_tags_list(self):
        """Test that empty tags list doesn't add tags field."""
        content = create_skill_md(
            name="No Tags",
            description="Skill without tags",
            instructions="Instructions",
            tags=[]
        )

        # Should not contain tags field
        assert "tags:" not in content

    def test_none_tags(self):
        """Test that None tags doesn't add tags field."""
        content = create_skill_md(
            name="No Tags",
            description="Skill without tags",
            instructions="Instructions",
            tags=None
        )

        # Should not contain tags field
        assert "tags:" not in content


class TestCreateSingleSkillPlugin:
    """Tests for create_single_skill_plugin function."""

    def test_basic_plugin_creation(self):
        """Test creating a basic plugin ZIP."""
        skill_content = "---\ndescription: Test\n---\n\n# Test\n\nContent"

        zip_buffer = create_single_skill_plugin(
            skill_name="Test Skill",
            skill_content=skill_content,
            author="testuser"
        )

        # Should return BytesIO
        assert isinstance(zip_buffer, BytesIO)

        # Should be a valid ZIP
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            # Check file list
            files = zf.namelist()

            # Should contain plugin.json
            assert ".claude-plugin/plugin.json" in files

            # Should contain skill in correct location
            assert "skills/test-skill/SKILL.md" in files

            # Should contain README
            assert "README.md" in files

    def test_plugin_json_structure(self):
        """Test that plugin.json has correct structure."""
        import json

        skill_content = "---\ndescription: Test\n---\n\n# Test"

        zip_buffer = create_single_skill_plugin(
            skill_name="My Test Skill",
            skill_content=skill_content,
            author="testuser",
            version="2.0.0"
        )

        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            plugin_json_str = zf.read(".claude-plugin/plugin.json").decode('utf-8')
            plugin_json = json.loads(plugin_json_str)

            # Check required fields
            assert plugin_json["name"] == "my-test-skill"
            assert plugin_json["displayName"] == "My Test Skill"
            assert plugin_json["version"] == "2.0.0"
            assert plugin_json["description"] == "Plugin containing My Test Skill skill"
            assert plugin_json["author"] == "testuser"

    def test_skill_content_preservation(self):
        """Test that SKILL.md content is preserved exactly."""
        skill_content = "---\ndescription: Test skill\ntags: [\"test\"]\n---\n\n# Test Skill\n\nThis is a test."

        zip_buffer = create_single_skill_plugin(
            skill_name="Test Skill",
            skill_content=skill_content,
            author="testuser"
        )

        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            actual_content = zf.read("skills/test-skill/SKILL.md").decode('utf-8')

            # Content should match exactly
            assert actual_content == skill_content

    def test_custom_display_name(self):
        """Test using custom plugin display name."""
        import json

        skill_content = "---\ndescription: Test\n---\n\n# Test"

        zip_buffer = create_single_skill_plugin(
            skill_name="test",
            skill_content=skill_content,
            author="testuser",
            plugin_display_name="Custom Display Name"
        )

        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            plugin_json = json.loads(zf.read(".claude-plugin/plugin.json"))

            assert plugin_json["displayName"] == "Custom Display Name"

    def test_skill_name_normalization(self):
        """Test that skill names are normalized to lowercase-hyphenated."""
        skill_content = "---\ndescription: Test\n---\n\n# Test"

        zip_buffer = create_single_skill_plugin(
            skill_name="My Awesome Skill",
            skill_content=skill_content,
            author="testuser"
        )

        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            import json
            plugin_json = json.loads(zf.read(".claude-plugin/plugin.json"))

            # Plugin name should be lowercase with hyphens
            assert plugin_json["name"] == "my-awesome-skill"

            # Skill directory should match
            assert "skills/my-awesome-skill/SKILL.md" in zf.namelist()

    def test_readme_generation(self):
        """Test that README is generated correctly."""
        skill_content = "---\ndescription: Test\n---\n\n# Test"

        zip_buffer = create_single_skill_plugin(
            skill_name="Test Skill",
            skill_content=skill_content,
            author="testuser"
        )

        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            readme = zf.read("README.md").decode('utf-8')

            # Should contain display name
            assert "# Test Skill" in readme

            # Should contain description
            assert "Plugin containing Test Skill skill" in readme

    def test_default_version(self):
        """Test that default version is 1.0.0."""
        import json

        skill_content = "---\ndescription: Test\n---\n\n# Test"

        zip_buffer = create_single_skill_plugin(
            skill_name="Test Skill",
            skill_content=skill_content,
            author="testuser"
        )

        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            plugin_json = json.loads(zf.read(".claude-plugin/plugin.json"))

            assert plugin_json["version"] == "1.0.0"

    def test_zip_buffer_seeked_to_start(self):
        """Test that returned buffer is seeked to start."""
        skill_content = "---\ndescription: Test\n---\n\n# Test"

        zip_buffer = create_single_skill_plugin(
            skill_name="Test Skill",
            skill_content=skill_content,
            author="testuser"
        )

        # Buffer should be at position 0
        assert zip_buffer.tell() == 0

        # Should be able to read immediately
        data = zip_buffer.read()
        assert len(data) > 0
