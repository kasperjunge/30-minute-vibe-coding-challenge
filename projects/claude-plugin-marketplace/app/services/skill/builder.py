"""Utilities for building SKILL.md files and skill plugins."""
import json
import zipfile
from io import BytesIO
from typing import List, Optional


def create_skill_md(
    name: str,
    description: str,
    instructions: str,
    examples: str = "",
    tags: Optional[List[str]] = None
) -> str:
    """
    Generate SKILL.md content from form data.

    Args:
        name: Skill name
        description: Brief skill description
        instructions: Detailed markdown instructions
        examples: Optional examples section
        tags: Optional list of tags

    Returns:
        Complete SKILL.md content with YAML frontmatter
    """
    # Generate frontmatter
    frontmatter = "---\n"
    frontmatter += f"description: {description}\n"

    if tags:
        # Format tags as YAML list
        tags_str = json.dumps(tags)
        frontmatter += f"tags: {tags_str}\n"

    frontmatter += "---\n\n"

    # Build content
    content = frontmatter
    content += f"# {name}\n\n"
    content += instructions + "\n\n"

    if examples:
        content += "## Examples\n\n"
        content += examples + "\n\n"

    return content


def create_single_skill_plugin(
    skill_name: str,
    skill_content: str,
    author: str,
    version: str = "1.0.0",
    plugin_display_name: Optional[str] = None
) -> BytesIO:
    """
    Create a plugin ZIP containing a single skill.

    Args:
        skill_name: Name of the skill (used for directory)
        skill_content: Complete SKILL.md content
        author: Plugin author username
        version: Plugin version (default 1.0.0)
        plugin_display_name: Optional display name (defaults to skill_name)

    Returns:
        BytesIO buffer containing ZIP file
    """
    zip_buffer = BytesIO()

    # Convert skill name to plugin name (lowercase, hyphenated)
    plugin_name = skill_name.lower().replace(' ', '-')
    display_name = plugin_display_name or skill_name

    # Generate plugin.json
    plugin_json = {
        "name": plugin_name,
        "displayName": display_name,
        "version": version,
        "description": f"Plugin containing {skill_name} skill",
        "author": author
    }

    # Create ZIP structure
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        # Add plugin.json
        zf.writestr(
            ".claude-plugin/plugin.json",
            json.dumps(plugin_json, indent=2)
        )

        # Add skill
        skill_dir = skill_name.lower().replace(' ', '-')
        zf.writestr(
            f"skills/{skill_dir}/SKILL.md",
            skill_content
        )

        # Add README
        readme = f"# {display_name}\n\n{plugin_json['description']}"
        zf.writestr("README.md", readme)

    zip_buffer.seek(0)
    return zip_buffer
