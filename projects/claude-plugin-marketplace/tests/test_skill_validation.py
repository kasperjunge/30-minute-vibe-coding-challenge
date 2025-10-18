"""Tests for skill validation logic."""
import pytest
from app.services.skill.validation import (
    validate_skill_form_data,
    validate_skill_md_structure,
    SkillValidationError
)


class TestValidateSkillFormData:
    """Tests for validate_skill_form_data function."""

    def test_valid_basic_data(self):
        """Test validation with valid basic data."""
        result = validate_skill_form_data(
            name="Test Skill",
            description="A test skill for testing purposes",
            instructions="This skill performs testing operations."
        )

        assert result["name"] == "Test Skill"
        assert result["description"] == "A test skill for testing purposes"
        assert result["instructions"] == "This skill performs testing operations."
        assert result["tags"] == []

    def test_valid_with_tags(self):
        """Test validation with valid tags."""
        result = validate_skill_form_data(
            name="Tagged Skill",
            description="A skill with tags",
            instructions="Instructions for the skill",
            tags="testing, unit-test, automation"
        )

        assert result["tags"] == ["testing", "unit-test", "automation"]

    def test_strips_whitespace(self):
        """Test that whitespace is stripped from fields."""
        result = validate_skill_form_data(
            name="  Test Skill  ",
            description="  A test skill  ",
            instructions="  These are valid instructions for testing  "
        )

        assert result["name"] == "Test Skill"
        assert result["description"] == "A test skill"
        assert result["instructions"] == "These are valid instructions for testing"

    def test_empty_name(self):
        """Test that empty name raises error."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="",
                description="Valid description",
                instructions="Valid instructions"
            )

        assert "Skill name is required" in str(exc_info.value)

    def test_whitespace_only_name(self):
        """Test that whitespace-only name raises error."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="   ",
                description="Valid description",
                instructions="Valid instructions"
            )

        assert "Skill name is required" in str(exc_info.value)

    def test_name_too_short(self):
        """Test that name shorter than 3 characters raises error."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="Ab",
                description="Valid description",
                instructions="Valid instructions"
            )

        assert "at least 3 characters" in str(exc_info.value)

    def test_name_too_long(self):
        """Test that name longer than 100 characters raises error."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="A" * 101,
                description="Valid description",
                instructions="Valid instructions"
            )

        assert "less than 100 characters" in str(exc_info.value)

    def test_empty_description(self):
        """Test that empty description raises error."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="Test Skill",
                description="",
                instructions="Valid instructions"
            )

        assert "Description is required" in str(exc_info.value)

    def test_description_too_short(self):
        """Test that description shorter than 10 characters raises error."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="Test Skill",
                description="Too short",
                instructions="Valid instructions"
            )

        assert "at least 10 characters" in str(exc_info.value)

    def test_description_too_long(self):
        """Test that description longer than 500 characters raises error."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="Test Skill",
                description="A" * 501,
                instructions="Valid instructions"
            )

        assert "less than 500 characters" in str(exc_info.value)

    def test_empty_instructions(self):
        """Test that empty instructions raises error."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="Test Skill",
                description="Valid description",
                instructions=""
            )

        assert "Instructions are required" in str(exc_info.value)

    def test_instructions_too_short(self):
        """Test that instructions shorter than 20 characters raises error."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="Test Skill",
                description="Valid description",
                instructions="Too short"
            )

        assert "at least 20 characters" in str(exc_info.value)

    def test_invalid_tag_uppercase(self):
        """Test that uppercase letters in tags raise error."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="Test Skill",
                description="Valid description",
                instructions="Valid instructions here",
                tags="valid-tag, InvalidTag"
            )

        assert "Invalid tag 'InvalidTag'" in str(exc_info.value)
        assert "lowercase letters, numbers, and hyphens" in str(exc_info.value)

    def test_invalid_tag_special_chars(self):
        """Test that special characters in tags raise error."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="Test Skill",
                description="Valid description",
                instructions="Valid instructions here",
                tags="valid, invalid@tag"
            )

        assert "Invalid tag 'invalid@tag'" in str(exc_info.value)

    def test_tag_too_long(self):
        """Test that tags longer than 30 characters raise error."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="Test Skill",
                description="Valid description",
                instructions="Valid instructions here",
                tags="a" * 31
            )

        assert "too long (max 30 characters)" in str(exc_info.value)

    def test_empty_tag_ignored(self):
        """Test that empty tags (from extra commas) are ignored."""
        result = validate_skill_form_data(
            name="Test Skill",
            description="Valid description",
            instructions="Valid instructions here",
            tags="tag1,,tag2,  ,tag3"
        )

        # Should only have non-empty tags
        assert result["tags"] == ["tag1", "tag2", "tag3"]

    def test_tags_whitespace_stripped(self):
        """Test that whitespace around tags is stripped."""
        result = validate_skill_form_data(
            name="Test Skill",
            description="Valid description",
            instructions="Valid instructions here",
            tags="  tag1  ,  tag2  ,  tag3  "
        )

        assert result["tags"] == ["tag1", "tag2", "tag3"]

    def test_multiple_errors_combined(self):
        """Test that multiple validation errors are combined."""
        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_form_data(
                name="AB",  # Too short
                description="Short",  # Too short
                instructions="Too short",  # Too short
                tags="InvalidTag"  # Invalid format
            )

        error_msg = str(exc_info.value)
        # Should contain multiple errors separated by semicolons
        assert "at least 3 characters" in error_msg
        assert ";" in error_msg

    def test_valid_numeric_tags(self):
        """Test that tags with numbers are valid."""
        result = validate_skill_form_data(
            name="Test Skill",
            description="Valid description",
            instructions="Valid instructions here",
            tags="tag1, test2, abc123"
        )

        assert result["tags"] == ["tag1", "test2", "abc123"]

    def test_valid_hyphenated_tags(self):
        """Test that hyphenated tags are valid."""
        result = validate_skill_form_data(
            name="Test Skill",
            description="Valid description",
            instructions="Valid instructions here",
            tags="code-quality, best-practices, unit-test"
        )

        assert result["tags"] == ["code-quality", "best-practices", "unit-test"]


class TestValidateSkillMdStructure:
    """Tests for validate_skill_md_structure function."""

    def test_valid_skill_md(self):
        """Test validation of valid SKILL.md structure."""
        content = """---
description: A test skill
tags: ["testing", "unit"]
---

# Test Skill

Content here.
"""

        metadata = validate_skill_md_structure(content)

        assert metadata["description"] == "A test skill"
        assert metadata["tags"] == '["testing", "unit"]'

    def test_minimal_valid_skill_md(self):
        """Test validation of minimal valid SKILL.md."""
        content = """---
description: Test
---

Content
"""

        metadata = validate_skill_md_structure(content)

        assert metadata["description"] == "Test"
        assert "tags" not in metadata

    def test_missing_frontmatter_start(self):
        """Test that missing opening --- raises error."""
        content = "description: Test\n---\n\nContent"

        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_md_structure(content)

        assert "must start with YAML frontmatter" in str(exc_info.value)
        assert "Example:" in str(exc_info.value)

    def test_missing_frontmatter_end(self):
        """Test that missing closing --- raises error."""
        content = "---\ndescription: Test\n\nContent"

        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_md_structure(content)

        assert "must have closing ---" in str(exc_info.value)

    def test_missing_description_field(self):
        """Test that missing description field raises error."""
        content = """---
tags: ["test"]
---

Content
"""

        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_md_structure(content)

        assert "must include 'description' field" in str(exc_info.value)

    def test_empty_frontmatter(self):
        """Test that empty frontmatter raises error."""
        content = "---\n---\n\nContent"

        with pytest.raises(SkillValidationError) as exc_info:
            validate_skill_md_structure(content)

        assert "must include 'description' field" in str(exc_info.value)

    def test_multiline_values(self):
        """Test that multiline values are handled."""
        content = """---
description: A test skill
author: Test Author
---

Content
"""

        metadata = validate_skill_md_structure(content)

        assert metadata["description"] == "A test skill"
        assert metadata["author"] == "Test Author"

    def test_extra_fields_preserved(self):
        """Test that extra fields are preserved in metadata."""
        content = """---
description: Test skill
tags: ["test"]
custom_field: custom value
---

Content
"""

        metadata = validate_skill_md_structure(content)

        assert metadata["description"] == "Test skill"
        assert metadata["tags"] == '["test"]'
        assert metadata["custom_field"] == "custom value"

    def test_whitespace_handling(self):
        """Test that whitespace in frontmatter is handled correctly."""
        content = """---
description:    Test skill
tags:   ["test"]
---

Content
"""

        metadata = validate_skill_md_structure(content)

        # Whitespace should be stripped
        assert metadata["description"] == "Test skill"
        assert metadata["tags"] == '["test"]'
