"""Validation logic specific to SKILL.md files."""
import re
from typing import Dict, List


class SkillValidationError(Exception):
    """Skill-specific validation errors with user-friendly messages."""
    pass


def validate_skill_form_data(
    name: str,
    description: str,
    instructions: str,
    tags: str = ""
) -> Dict[str, str]:
    """
    Validate form data before creating SKILL.md.

    Args:
        name: Skill name
        description: Brief description
        instructions: Markdown instructions
        tags: Comma-separated tags (optional)

    Returns:
        Dict with parsed/validated data

    Raises:
        SkillValidationError: If validation fails
    """
    errors = []

    # Validate name
    if not name or not name.strip():
        errors.append("Skill name is required")
    elif len(name) < 3:
        errors.append("Skill name must be at least 3 characters")
    elif len(name) > 100:
        errors.append("Skill name must be less than 100 characters")

    # Validate description
    if not description or not description.strip():
        errors.append("Description is required")
    elif len(description) < 10:
        errors.append("Description must be at least 10 characters")
    elif len(description) > 500:
        errors.append("Description must be less than 500 characters")

    # Validate instructions
    if not instructions or not instructions.strip():
        errors.append("Instructions are required")
    elif len(instructions) < 20:
        errors.append("Instructions must be at least 20 characters")

    # Parse and validate tags
    parsed_tags = []
    if tags and tags.strip():
        raw_tags = [t.strip() for t in tags.split(',')]
        for tag in raw_tags:
            if not tag:
                continue
            if not re.match(r'^[a-z0-9-]+$', tag):
                errors.append(
                    f"Invalid tag '{tag}'. Tags must contain only "
                    "lowercase letters, numbers, and hyphens"
                )
            elif len(tag) > 30:
                errors.append(f"Tag '{tag}' is too long (max 30 characters)")
            else:
                parsed_tags.append(tag)

    if errors:
        raise SkillValidationError("; ".join(errors))

    return {
        "name": name.strip(),
        "description": description.strip(),
        "instructions": instructions.strip(),
        "tags": parsed_tags
    }


def validate_skill_md_structure(content: str) -> Dict:
    """
    Validate SKILL.md structure and extract metadata.

    Used for testing/verification of generated content.

    Args:
        content: Complete SKILL.md content

    Returns:
        Dict with extracted frontmatter

    Raises:
        SkillValidationError: If structure is invalid
    """
    if not content.startswith('---'):
        raise SkillValidationError(
            "SKILL.md must start with YAML frontmatter (---). "
            "Example:\n---\ndescription: My skill\n---"
        )

    parts = content.split('---', 2)
    if len(parts) < 3:
        raise SkillValidationError(
            "SKILL.md must have closing --- for frontmatter"
        )

    # Simple YAML parsing (only need description and tags)
    frontmatter_text = parts[1].strip()
    lines = frontmatter_text.split('\n')

    metadata = {}
    for line in lines:
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        metadata[key] = value

    # Validate required fields
    if 'description' not in metadata:
        raise SkillValidationError(
            "SKILL.md frontmatter must include 'description' field"
        )

    return metadata
