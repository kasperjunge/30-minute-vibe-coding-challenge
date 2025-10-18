# Agent Skill Creation Flow Implementation Plan

## Overview

Implement a user-friendly web interface for creating Agent Skills through a guided form-based wizard. The wizard will generate properly formatted SKILL.md files, package them into plugins, and upload them using the existing plugin infrastructure. This enables non-technical users to create skills without manually writing YAML frontmatter or managing file structures.

## Current State Analysis

### What Exists Now

**Skills Infrastructure** (app/services/plugin/storage.py:117-157):
- Skills are detected by scanning for `SKILL.md` files in `skills/*/` directories
- Each `SKILL.md` file counts as one skill component
- Skills must have YAML frontmatter with `description` and optional `tags` fields
- Example skill exists: test-plugins/dev-tools-plugin/skills/code-reviewer/SKILL.md

**Plugin Upload Pipeline** (app/services/plugin/routes.py:33-180):
- Complete upload, validation, storage, and database workflow
- Handles multipart form data with file uploads
- Temporary file management with cleanup
- Version comparison for updates
- Error handling with user-friendly messages

**Validation System** (app/services/plugin/validation.py:14-143):
- Multi-layer validation (ZIP integrity, security, structure, JSON, semver)
- Custom `ValidationError` exception for user-friendly messages
- Forbidden file type scanning for security

**Form Patterns** (app/services/auth/routes.py:23-103):
- Server-side validation with inline error display
- POST-Redirect-GET pattern for success cases
- Template-based error rendering with HTTP 400 status

### What's Missing

1. **Skill Creation Service**: No dedicated service for skill creation
2. **Form Builder Utilities**: No functions to generate SKILL.md from form data
3. **Skill Validation**: No validation specific to SKILL.md structure
4. **Creation Templates**: No HTML templates for skill creation forms
5. **In-Memory Plugin Creation**: No utility to create single-skill plugins programmatically

### Key Constraints Discovered

- Skills MUST exist within plugins (no standalone skills)
- Skills MUST be in `skills/{skill-name}/SKILL.md` format
- SKILL.md filename MUST be uppercase
- YAML frontmatter is required for skill metadata
- The existing upload pipeline can handle programmatically-generated plugins

## Desired End State

### End State Specification

Users can create skills through a web form without touching code:

1. **Accessible Creation Flow**:
   - Navigate to `/skills/create`
   - Fill out intuitive form with name, description, instructions
   - Optionally restrict tool permissions
   - Preview generated SKILL.md before creating
   - Submit to create single-skill plugin automatically

2. **Generated Artifacts**:
   - Valid SKILL.md file with proper YAML frontmatter
   - Plugin ZIP containing the skill in correct directory structure
   - Plugin uploaded and visible in marketplace
   - Skill counted correctly in plugin metadata

3. **Quality Assurance**:
   - Form validation prevents invalid skills
   - Preview shows exact SKILL.md content before creation
   - User-friendly error messages guide corrections
   - Success confirmation with link to created plugin

### Verification Methods

#### Automated Verification:
- [ ] Service routes registered: `python -c "from main import app; print([r.path for r in app.routes])"`
- [ ] Template files exist: `ls app/services/skill/templates/`
- [ ] Unit tests pass: `pytest tests/test_skill_creation.py -v`
- [ ] Integration tests pass: `pytest tests/test_skill_e2e.py -v`
- [ ] Validation tests pass: `pytest tests/test_skill_validation.py -v`
- [ ] No linting errors: `flake8 app/services/skill/`
- [ ] Type checking passes: `mypy app/services/skill/`

#### Manual Verification:
- [ ] Can access `/skills/create` form without errors
- [ ] Form validation displays helpful error messages
- [ ] Preview shows correctly formatted SKILL.md
- [ ] Created plugin appears in "My Plugins" dashboard
- [ ] Skill count appears correctly on plugin detail page
- [ ] Download link works for created plugin
- [ ] Created SKILL.md follows exact format of existing example

## What We're NOT Doing

To prevent scope creep, explicitly out of scope:

- ❌ Editing existing skills (separate feature for later)
- ❌ Adding skills to existing plugins (Phase 2 feature)
- ❌ Skill templates/gallery (Phase 3 feature)
- ❌ Rich markdown editor (using textarea + preview)
- ❌ Separate skill database table (using existing plugin_metadata JSON)
- ❌ Skill marketplace view (plugins are the marketplace unit)
- ❌ Multi-skill plugins via form (advanced users use manual upload)
- ❌ Skill testing/execution (creation only)
- ❌ Importing existing SKILL.md files (use regular plugin upload)

## Implementation Approach

### Strategy

Follow the established patterns in the codebase:
1. Create new `skill` service following `auth` and `plugin` service structure
2. Reuse validation patterns with skill-specific validators
3. Leverage in-memory ZIP creation from test patterns
4. Use existing plugin upload pipeline for final storage
5. Follow form validation and error display patterns

### Key Design Decisions

**Decision 1: Service Architecture**
- Create `app/services/skill/` service module
- Separate concerns: routes, builder, validation
- Register router in main.py following existing pattern

**Decision 2: Single-Skill Plugins**
- Wizard creates plugins with exactly one skill
- Simpler UX, clearer ownership
- Advanced users can manually create multi-skill plugins

**Decision 3: Reuse Upload Pipeline**
- Generate ZIP in memory, pass to existing upload logic
- No duplication of validation/storage/database code
- Consistent behavior between manual and form-based uploads

**Decision 4: Simple Textarea + Preview**
- Avoid complex dependencies (CodeMirror, Monaco)
- Faster implementation
- Good enough UX for MVP
- Can upgrade based on user feedback

## Phase 1: Skill Service Foundation

### Overview
Create the basic skill service infrastructure with routes, templates, and builder utilities. This phase establishes the foundation without complex validation or wizard steps.

### Changes Required

#### 1. Create Skill Service Module
**New Directory**: `app/services/skill/`

**Files to create**:
- `__init__.py` (empty package marker)
- `routes.py` (route handlers)
- `builder.py` (SKILL.md generation utilities)
- `validation.py` (skill-specific validation)

**Purpose**: Establish service structure following existing pattern

#### 2. Skill Builder Utility
**File**: `app/services/skill/builder.py`

**Implementation**:
```python
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
```

**Success Criteria**:

##### Automated Verification:
- [x] Unit tests pass: `pytest tests/test_skill_builder.py::test_create_skill_md -v`
- [x] Unit tests pass: `pytest tests/test_skill_builder.py::test_create_single_skill_plugin -v`
- [x] Generated SKILL.md has valid YAML frontmatter
- [x] Generated ZIP can be opened with `zipfile.ZipFile()`
- [x] Generated ZIP contains correct file structure

##### Manual Verification:
- [ ] Generated SKILL.md matches format of test-plugins/dev-tools-plugin/skills/code-reviewer/SKILL.md
- [ ] Tags are formatted correctly as JSON array in YAML
- [ ] ZIP structure matches expected plugin structure

#### 3. Skill Validation Module
**File**: `app/services/skill/validation.py`

**Implementation**:
```python
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
```

**Success Criteria**:

##### Automated Verification:
- [x] Unit tests pass: `pytest tests/test_skill_validation.py -v`
- [x] Validation catches empty name/description/instructions
- [x] Validation catches too-short fields
- [x] Validation catches too-long fields
- [x] Tag validation catches invalid characters
- [x] Structure validation detects missing frontmatter

##### Manual Verification:
- [ ] Error messages are clear and actionable
- [ ] Multiple errors are combined into single message
- [ ] Tag format validation matches expected pattern

#### 4. Basic Skill Routes
**File**: `app/services/skill/routes.py`

**Implementation**:
```python
"""Routes for skill creation."""
from typing import Annotated
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.shared.database import get_db
from app.services.auth.models import User
from app.services.auth.dependencies import require_auth
from app.services.skill.builder import create_skill_md, create_single_skill_plugin
from app.services.skill.validation import validate_skill_form_data, SkillValidationError


# Setup templates
template_dirs = [
    "app/shared/templates",
    "app/services/skill/templates"
]
templates = Jinja2Templates(directory=template_dirs)

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/create", response_class=HTMLResponse)
async def skill_creation_form(
    request: Request,
    user: User = Depends(require_auth)
):
    """Display the skill creation form."""
    return templates.TemplateResponse(
        "create.html",
        {"request": request, "user": user}
    )


@router.post("/create")
async def create_skill(
    request: Request,
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    instructions: Annotated[str, Form()],
    examples: Annotated[str, Form()] = "",
    tags: Annotated[str, Form()] = "",
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Process skill creation and redirect to plugin upload."""

    # Validate form data
    try:
        validated = validate_skill_form_data(
            name=name,
            description=description,
            instructions=instructions,
            tags=tags
        )
    except SkillValidationError as e:
        return templates.TemplateResponse(
            "create.html",
            {
                "request": request,
                "user": user,
                "error": str(e),
                "name": name,
                "description": description,
                "instructions": instructions,
                "examples": examples,
                "tags": tags
            },
            status_code=400
        )

    # Generate SKILL.md
    skill_content = create_skill_md(
        name=validated["name"],
        description=validated["description"],
        instructions=validated["instructions"],
        examples=examples,
        tags=validated["tags"] if validated["tags"] else None
    )

    # Create plugin ZIP
    zip_buffer = create_single_skill_plugin(
        skill_name=validated["name"],
        skill_content=skill_content,
        author=user.username
    )

    # Store ZIP buffer in session for upload processing
    # (We'll implement the upload integration in Phase 2)
    # For now, return success message

    return templates.TemplateResponse(
        "create.html",
        {
            "request": request,
            "user": user,
            "success": f"Skill '{validated['name']}' created successfully!"
        }
    )
```

**Success Criteria**:

##### Automated Verification:
- [x] Route registration verified: `python -c "from main import app; assert '/skills/create' in [r.path for r in app.routes]"`
- [ ] Integration tests pass: `pytest tests/test_skill_routes.py -v`
- [ ] Form submission returns 400 on validation error
- [ ] Form submission preserves values on error

##### Manual Verification:
- [ ] Can access /skills/create when logged in
- [ ] Redirects to login when not authenticated
- [ ] Form displays without errors
- [ ] Validation errors appear above form

#### 5. Basic Creation Template
**File**: `app/services/skill/templates/create.html`

**Implementation**:
```html
{% extends "base.html" %}

{% block title %}Create Skill - Plugin Marketplace{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto">
    <div class="bg-white shadow-md rounded-lg p-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-6">Create a Skill</h1>

        <p class="text-gray-600 mb-8">
            Create a skill that extends Claude's capabilities. Skills are automatically invoked by Claude when relevant to the task.
        </p>

        <!-- Error Display -->
        {% if error %}
        <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p class="text-red-800">{{ error }}</p>
        </div>
        {% endif %}

        <!-- Success Display -->
        {% if success %}
        <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <p class="text-green-800">{{ success }}</p>
        </div>
        {% endif %}

        <!-- Form -->
        <form method="post" action="/skills/create">
            <!-- Skill Name -->
            <div class="mb-6">
                <label for="name" class="block text-sm font-medium text-gray-700 mb-2">
                    Skill Name *
                </label>
                <input
                    type="text"
                    name="name"
                    id="name"
                    value="{{ name or '' }}"
                    required
                    minlength="3"
                    maxlength="100"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Code Reviewer"
                />
                <p class="text-xs text-gray-500 mt-1">
                    A clear, descriptive name for your skill (3-100 characters)
                </p>
            </div>

            <!-- Description -->
            <div class="mb-6">
                <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
                    Description *
                </label>
                <input
                    type="text"
                    name="description"
                    id="description"
                    value="{{ description or '' }}"
                    required
                    minlength="10"
                    maxlength="500"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Analyzes code for quality, security, and best practices"
                />
                <p class="text-xs text-gray-500 mt-1">
                    Brief description of what the skill does (10-500 characters)
                </p>
            </div>

            <!-- Instructions -->
            <div class="mb-6">
                <label for="instructions" class="block text-sm font-medium text-gray-700 mb-2">
                    Instructions *
                </label>
                <textarea
                    name="instructions"
                    id="instructions"
                    required
                    minlength="20"
                    rows="10"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                    placeholder="## Purpose&#10;&#10;Explain what this skill does and when Claude should use it.&#10;&#10;## How It Works&#10;&#10;Describe the skill's behavior in detail."
                >{{ instructions or '' }}</textarea>
                <p class="text-xs text-gray-500 mt-1">
                    Detailed instructions in Markdown format (minimum 20 characters)
                </p>
            </div>

            <!-- Examples (Optional) -->
            <div class="mb-6">
                <label for="examples" class="block text-sm font-medium text-gray-700 mb-2">
                    Examples (Optional)
                </label>
                <textarea
                    name="examples"
                    id="examples"
                    rows="6"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                    placeholder="Provide example usage scenarios in Markdown format"
                >{{ examples or '' }}</textarea>
                <p class="text-xs text-gray-500 mt-1">
                    Optional examples showing when and how the skill is used
                </p>
            </div>

            <!-- Tags (Optional) -->
            <div class="mb-6">
                <label for="tags" class="block text-sm font-medium text-gray-700 mb-2">
                    Tags (Optional)
                </label>
                <input
                    type="text"
                    name="tags"
                    id="tags"
                    value="{{ tags or '' }}"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="code-quality, review, best-practices"
                />
                <p class="text-xs text-gray-500 mt-1">
                    Comma-separated tags (lowercase, hyphens allowed). Example: code-quality, security, performance
                </p>
            </div>

            <!-- Submit Button -->
            <div class="flex justify-end space-x-4">
                <a
                    href="/"
                    class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
                >
                    Cancel
                </a>
                <button
                    type="submit"
                    class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                    Create Skill
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
```

**Success Criteria**:

##### Automated Verification:
- [ ] Template renders without errors: `pytest tests/test_skill_templates.py::test_create_template_renders -v`
- [ ] Form fields have correct HTML5 validation attributes
- [ ] Template extends base.html correctly

##### Manual Verification:
- [ ] Form displays with consistent styling
- [ ] Field validation works (HTML5 required, minlength, maxlength)
- [ ] Error messages display correctly
- [ ] Form values persist after validation error
- [ ] Help text provides clear guidance

#### 6. Register Skill Service
**File**: `main.py`

**Changes**:
Add import at line 17:
```python
from app.services.skill.routes import router as skill_router
```

Add router registration at line 162 (after plugin_router):
```python
app.include_router(skill_router)
```

**Success Criteria**:

##### Automated Verification:
- [ ] Application starts without errors: `python main.py &`
- [ ] Routes registered: `curl -s http://localhost:8000/openapi.json | grep "/skills/create"`
- [ ] No import errors when running tests

##### Manual Verification:
- [ ] Server starts successfully
- [ ] /skills/create accessible when authenticated
- [ ] No 404 errors on skill routes

#### 7. Unit Tests
**File**: `tests/test_skill_builder.py`

**Implementation**: Test coverage for builder.py functions (create_skill_md, create_single_skill_plugin)

**File**: `tests/test_skill_validation.py`

**Implementation**: Test coverage for validation.py functions (validate_skill_form_data, validate_skill_md_structure)

**Success Criteria**:

##### Automated Verification:
- [x] All unit tests pass: `pytest tests/test_skill_*.py -v`
- [ ] Code coverage > 80%: `pytest --cov=app/services/skill tests/test_skill_*.py`
- [x] Tests run in < 1 second

**Implementation Note**: After completing Phase 1 and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to Phase 2.

---

## Phase 2: Plugin Upload Integration

### Overview
Integrate skill creation with the existing plugin upload pipeline. When a skill is created, automatically upload it as a plugin using the established upload flow.

### Changes Required

#### 1. Upload Integration Utility
**File**: `app/services/skill/upload.py`

**Implementation**:
```python
"""Integration with plugin upload pipeline."""
import tempfile
import shutil
from pathlib import Path
from io import BytesIO
from sqlalchemy.orm import Session

from app.services.plugin.validation import validate_plugin_zip
from app.services.plugin.storage import store_plugin_zip, extract_plugin_metadata
from app.services.plugin.models import Plugin, PluginVersion
from app.services.plugin.routes import is_version_higher
from datetime import datetime, UTC


async def upload_skill_as_plugin(
    zip_buffer: BytesIO,
    user,
    db: Session
) -> tuple[bool, str, str | None]:
    """
    Upload skill plugin using existing plugin upload pipeline.

    Args:
        zip_buffer: In-memory ZIP file
        user: Authenticated user
        db: Database session

    Returns:
        Tuple of (success, message, plugin_url)
    """
    temp_dir = None
    try:
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp())
        temp_zip_path = temp_dir / "skill-plugin.zip"

        # Write buffer to temp file
        with open(temp_zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())

        # Validate using existing pipeline
        plugin_json = validate_plugin_zip(temp_zip_path)

        # Extract metadata
        name = plugin_json.get("name")
        display_name = plugin_json.get("displayName", name)
        description = plugin_json.get("description")
        version = plugin_json.get("version")

        # Check for existing plugin
        existing_plugin = db.query(Plugin).filter(
            Plugin.author_id == user.id,
            Plugin.name == name
        ).first()

        if existing_plugin:
            # Handle version update
            latest_version = db.query(PluginVersion).filter(
                PluginVersion.plugin_id == existing_plugin.id,
                PluginVersion.is_latest == True
            ).first()

            if latest_version:
                if not is_version_higher(version, latest_version.version):
                    return (
                        False,
                        f"Version {version} must be higher than current version {latest_version.version}",
                        None
                    )
                latest_version.is_latest = False

            plugin = existing_plugin
            plugin.updated_at = datetime.now(UTC)
        else:
            # Create new plugin
            plugin = Plugin(
                name=name,
                display_name=display_name,
                description=description,
                author_id=user.id,
                is_published=True
            )
            db.add(plugin)
            db.commit()
            db.refresh(plugin)

        # Store plugin files
        stored_zip_path = store_plugin_zip(
            temp_zip_path,
            user.username,
            plugin.name,
            version
        )

        # Extract metadata
        metadata_result = extract_plugin_metadata(
            temp_zip_path,
            user.username,
            plugin.name,
            version
        )

        # Create plugin version
        plugin_version = PluginVersion(
            plugin_id=plugin.id,
            version=version,
            file_path=str(stored_zip_path),
            readme_content=metadata_result.get("readme_content"),
            plugin_metadata=metadata_result.get("plugin_json", {}),
            is_latest=True
        )
        db.add(plugin_version)
        db.commit()

        plugin_url = f"/plugins/@{user.username}/{plugin.name}"
        return (True, "Skill plugin created successfully!", plugin_url)

    except Exception as e:
        return (False, f"Error creating plugin: {str(e)}", None)

    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)
```

**Success Criteria**:

##### Automated Verification:
- [ ] Unit tests pass: `pytest tests/test_skill_upload.py -v`
- [ ] Integration with validation pipeline works
- [ ] Integration with storage pipeline works
- [ ] Database records created correctly
- [ ] Temporary files cleaned up

##### Manual Verification:
- [ ] Created plugins appear in database
- [ ] ZIP files stored in correct location
- [ ] Metadata extracted properly

#### 2. Update Skill Creation Route
**File**: `app/services/skill/routes.py`

**Changes**: Replace the success template response with upload integration

**Update the create_skill function** (around line 50-80):
```python
@router.post("/create")
async def create_skill(
    request: Request,
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    instructions: Annotated[str, Form()],
    examples: Annotated[str, Form()] = "",
    tags: Annotated[str, Form()] = "",
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Process skill creation and upload as plugin."""

    # Validate form data
    try:
        validated = validate_skill_form_data(
            name=name,
            description=description,
            instructions=instructions,
            tags=tags
        )
    except SkillValidationError as e:
        return templates.TemplateResponse(
            "create.html",
            {
                "request": request,
                "user": user,
                "error": str(e),
                "name": name,
                "description": description,
                "instructions": instructions,
                "examples": examples,
                "tags": tags
            },
            status_code=400
        )

    # Generate SKILL.md
    skill_content = create_skill_md(
        name=validated["name"],
        description=validated["description"],
        instructions=validated["instructions"],
        examples=examples,
        tags=validated["tags"] if validated["tags"] else None
    )

    # Create plugin ZIP
    zip_buffer = create_single_skill_plugin(
        skill_name=validated["name"],
        skill_content=skill_content,
        author=user.username
    )

    # Upload as plugin
    from app.services.skill.upload import upload_skill_as_plugin
    success, message, plugin_url = await upload_skill_as_plugin(
        zip_buffer,
        user,
        db
    )

    if not success:
        return templates.TemplateResponse(
            "create.html",
            {
                "request": request,
                "user": user,
                "error": message,
                "name": name,
                "description": description,
                "instructions": instructions,
                "examples": examples,
                "tags": tags
            },
            status_code=400
        )

    # Redirect to plugin detail page
    return RedirectResponse(
        plugin_url + "?created=1",
        status_code=303
    )
```

**Success Criteria**:

##### Automated Verification:
- [ ] Integration tests pass: `pytest tests/test_skill_e2e.py::test_skill_creation_flow -v`
- [ ] Successful creation redirects to plugin detail
- [ ] Failed uploads display errors in form

##### Manual Verification:
- [ ] Creating skill redirects to plugin detail page
- [ ] Success message appears on plugin page
- [ ] Plugin appears in "My Plugins"

#### 3. Update Plugin Detail Template
**File**: `app/services/plugin/templates/detail.html`

**Changes**: Add success message for newly created skills

Add after existing success message block (around line 20-30):
```html
{% if request.query_params.get('created') %}
<div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
    <p class="text-green-800">✓ Your skill has been successfully created and published!</p>
</div>
{% endif %}
```

**Success Criteria**:

##### Automated Verification:
- [ ] Template renders without errors with `?created=1` query param
- [ ] Success message block displays conditionally

##### Manual Verification:
- [ ] Success message appears after skill creation
- [ ] Success message styled consistently with other messages

#### 4. Integration Tests
**File**: `tests/test_skill_e2e.py`

**Implementation**: End-to-end tests covering complete skill creation flow from form submission to plugin visibility

**Test scenarios**:
- Complete skill creation flow
- Skill appears in plugin list
- Skill count is correct
- Plugin detail page accessible
- Download link works

**Success Criteria**:

##### Automated Verification:
- [ ] All integration tests pass: `pytest tests/test_skill_e2e.py -v`
- [ ] Tests verify complete flow
- [ ] Tests check database state
- [ ] Tests verify file system artifacts

**Implementation Note**: After completing Phase 2 and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to Phase 3.

---

## Phase 3: Preview and Polish

### Overview
Add preview functionality and UI polish to enhance user experience. Users can preview the generated SKILL.md before creating the plugin.

### Changes Required

#### 1. Preview Endpoint
**File**: `app/services/skill/routes.py`

**Add new route**:
```python
@router.post("/preview")
async def preview_skill(
    request: Request,
    name: Annotated[str, Form()],
    description: Annotated[str, Form()],
    instructions: Annotated[str, Form()],
    examples: Annotated[str, Form()] = "",
    tags: Annotated[str, Form()] = "",
    user: User = Depends(require_auth)
):
    """Generate preview of SKILL.md without creating plugin."""

    # Validate form data
    try:
        validated = validate_skill_form_data(
            name=name,
            description=description,
            instructions=instructions,
            tags=tags
        )
    except SkillValidationError as e:
        return templates.TemplateResponse(
            "create.html",
            {
                "request": request,
                "user": user,
                "error": str(e),
                "name": name,
                "description": description,
                "instructions": instructions,
                "examples": examples,
                "tags": tags
            },
            status_code=400
        )

    # Generate SKILL.md for preview
    skill_content = create_skill_md(
        name=validated["name"],
        description=validated["description"],
        instructions=validated["instructions"],
        examples=examples,
        tags=validated["tags"] if validated["tags"] else None
    )

    # Return form with preview
    return templates.TemplateResponse(
        "create.html",
        {
            "request": request,
            "user": user,
            "name": name,
            "description": description,
            "instructions": instructions,
            "examples": examples,
            "tags": tags,
            "preview": skill_content
        }
    )
```

**Success Criteria**:

##### Automated Verification:
- [ ] Route responds to POST /skills/preview
- [ ] Preview returns valid SKILL.md content
- [ ] Validation errors handled correctly
- [ ] Form values preserved in preview

##### Manual Verification:
- [ ] Preview button generates correct SKILL.md
- [ ] Preview displays formatted properly

#### 2. Update Creation Template with Preview
**File**: `app/services/skill/templates/create.html`

**Changes**:
1. Add preview button before submit button
2. Add preview display section
3. Update form to support both preview and create actions

**Add before submit button** (around line 140):
```html
<!-- Preview Section -->
{% if preview %}
<div class="mb-6">
    <h3 class="text-lg font-semibold text-gray-800 mb-3">Preview: SKILL.md</h3>
    <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <pre class="text-sm font-mono whitespace-pre-wrap overflow-x-auto">{{ preview }}</pre>
    </div>
    <p class="text-xs text-gray-500 mt-2">
        This is how your SKILL.md file will look. Review it and click "Create Skill" to proceed.
    </p>
</div>
{% endif %}

<!-- Submit Buttons -->
<div class="flex justify-end space-x-4">
    <a
        href="/"
        class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
    >
        Cancel
    </a>
    <button
        type="submit"
        formaction="/skills/preview"
        class="px-6 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition"
    >
        Preview
    </button>
    <button
        type="submit"
        formaction="/skills/create"
        class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
    >
        Create Skill
    </button>
</div>
```

**Success Criteria**:

##### Automated Verification:
- [ ] Template renders with preview section
- [ ] Preview section only shows when preview data exists
- [ ] Both buttons submit form correctly

##### Manual Verification:
- [ ] Preview button generates preview without creating plugin
- [ ] Preview displays YAML frontmatter correctly
- [ ] Create button creates plugin and redirects
- [ ] Preview content is formatted readably

#### 3. Navigation Link
**File**: `app/shared/templates/base.html`

**Changes**: Add "Create Skill" link to navigation menu

**Add after "Upload Plugin" link** (around line 35-40):
```html
{% if user %}
    <a href="/plugins/upload" class="hover:text-blue-200 transition">Upload Plugin</a>
    <a href="/skills/create" class="hover:text-blue-200 transition">Create Skill</a>
    <a href="/plugins/my-plugins" class="hover:text-blue-200 transition">My Plugins</a>
{% else %}
    <a href="/auth/register" class="hover:text-blue-200 transition">Register</a>
    <a href="/auth/login" class="hover:text-blue-200 transition">Login</a>
{% endif %}
```

**Success Criteria**:

##### Automated Verification:
- [ ] Template renders without errors
- [ ] Link only appears when authenticated

##### Manual Verification:
- [ ] "Create Skill" link appears in navigation when logged in
- [ ] Link not visible when logged out
- [ ] Link navigates to /skills/create

#### 4. Homepage Call-to-Action
**File**: `app/shared/templates/home.html`

**Changes**: Add prominent "Create Skill" call-to-action for authenticated users

**Add after header, before plugin listing** (around line 10-15):
```html
{% if user %}
<div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
    <div class="flex items-center justify-between">
        <div>
            <h3 class="text-lg font-semibold text-blue-900 mb-2">Create Your First Skill</h3>
            <p class="text-blue-700">
                Extend Claude's capabilities by creating custom skills through our intuitive form-based wizard.
                No coding required!
            </p>
        </div>
        <div class="ml-6">
            <a
                href="/skills/create"
                class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold whitespace-nowrap"
            >
                Create Skill →
            </a>
        </div>
    </div>
</div>
{% endif %}
```

**Success Criteria**:

##### Automated Verification:
- [ ] Template renders without errors
- [ ] CTA only appears when authenticated

##### Manual Verification:
- [ ] CTA appears prominently on homepage when logged in
- [ ] CTA not visible when logged out
- [ ] Button navigates to skill creation form
- [ ] Styling consistent with rest of site

#### 5. Polish and Styling
**Files**: All skill service templates

**Changes**:
- Ensure consistent Tailwind CSS styling
- Add helpful tooltips and placeholders
- Improve error message formatting
- Add loading states if needed

**Success Criteria**:

##### Automated Verification:
- [ ] All templates render without errors
- [ ] CSS classes are valid Tailwind utilities

##### Manual Verification:
- [ ] UI feels cohesive with rest of application
- [ ] Forms are intuitive and well-labeled
- [ ] Error messages are clear and actionable
- [ ] Success states are visually clear

#### 6. Documentation
**File**: `app/services/skill/README.md`

**Create new documentation file**:
```markdown
# Skill Creation Service

Web interface for creating Agent Skills through a form-based wizard.

## Overview

The skill service enables users to create Claude Code skills without manually writing YAML frontmatter or managing file structures. Skills are automatically packaged into plugins and uploaded to the marketplace.

## Architecture

- **routes.py**: HTTP endpoints for creation and preview
- **builder.py**: SKILL.md generation and plugin packaging
- **validation.py**: Form validation and SKILL.md structure validation
- **upload.py**: Integration with plugin upload pipeline
- **templates/**: HTML templates for creation form

## User Flow

1. User navigates to `/skills/create`
2. Fills out form with skill details
3. (Optional) Clicks "Preview" to see generated SKILL.md
4. Clicks "Create Skill" to generate and upload plugin
5. Redirected to plugin detail page
6. Skill is visible in marketplace

## Generated Plugin Structure

```
{skill-name}/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── {skill-name}/
│       └── SKILL.md
└── README.md
```

## Validation Rules

- **Name**: 3-100 characters
- **Description**: 10-500 characters
- **Instructions**: Minimum 20 characters (Markdown)
- **Examples**: Optional (Markdown)
- **Tags**: Optional, lowercase, hyphens only, max 30 chars each

## Integration Points

- Uses `app/services/plugin/validation.py` for plugin ZIP validation
- Uses `app/services/plugin/storage.py` for file storage
- Creates `Plugin` and `PluginVersion` database records
- Follows existing upload error handling patterns

## Testing

```bash
# Unit tests
pytest tests/test_skill_builder.py -v
pytest tests/test_skill_validation.py -v

# Integration tests
pytest tests/test_skill_routes.py -v
pytest tests/test_skill_upload.py -v

# End-to-end tests
pytest tests/test_skill_e2e.py -v
```

## Future Enhancements

- Skill templates/gallery
- Adding skills to existing plugins
- Rich markdown editor
- Skill preview before creation
- Tool permission restrictions
```

**Success Criteria**:

##### Automated Verification:
- [ ] Documentation file exists and is readable
- [ ] All referenced files exist

##### Manual Verification:
- [ ] Documentation is clear and accurate
- [ ] Code examples are correct
- [ ] Architecture description matches implementation

**Implementation Note**: After completing Phase 3 and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful.

---

## Testing Strategy

### Unit Tests

**Test Coverage Areas**:
1. **Builder Functions** (test_skill_builder.py):
   - SKILL.md generation with various inputs
   - YAML frontmatter formatting
   - Tag formatting
   - ZIP creation and structure
   - Plugin metadata generation

2. **Validation Functions** (test_skill_validation.py):
   - Form field validation
   - Error message generation
   - Tag parsing and validation
   - SKILL.md structure validation

3. **Routes** (test_skill_routes.py):
   - GET /skills/create authentication
   - POST /skills/create validation errors
   - POST /skills/create success flow
   - POST /skills/preview functionality

4. **Upload Integration** (test_skill_upload.py):
   - ZIP buffer processing
   - Plugin pipeline integration
   - Database record creation
   - Error handling

### Integration Tests

**Test Scenarios** (test_skill_e2e.py):
1. Complete skill creation flow:
   - Submit form → validate → generate → upload → redirect
2. Skill appears in database
3. Plugin ZIP exists on filesystem
4. Skill count is correct in plugin metadata
5. Plugin detail page accessible
6. Download functionality works

### Manual Testing Steps

**After Phase 1**:
1. Navigate to /skills/create
2. Verify form displays correctly
3. Test HTML5 validation (required, minlength, maxlength)
4. Submit empty form → verify validation errors
5. Fill valid data → verify success message
6. Check generated SKILL.md format

**After Phase 2**:
1. Create a skill via form
2. Verify redirect to plugin detail page
3. Check "My Plugins" dashboard shows new plugin
4. Verify skill count on plugin detail page
5. Download plugin ZIP and inspect contents
6. Verify SKILL.md matches expected format

**After Phase 3**:
1. Click "Preview" button → verify SKILL.md preview
2. Verify preview shows YAML frontmatter correctly
3. Edit form → preview again → verify changes reflected
4. Create skill from preview → verify upload works
5. Check homepage CTA appears when logged in
6. Verify navigation link works

## Performance Considerations

### In-Memory ZIP Creation
- Skill plugins are small (<100KB typically)
- BytesIO buffer is efficient for small files
- No disk I/O until upload pipeline processes file
- Temporary files cleaned up immediately

### Database Impact
- Reuses existing Plugin and PluginVersion tables
- No additional queries beyond standard plugin upload
- Single transaction for plugin creation

### File Storage
- Follows existing storage patterns
- Skills stored within plugin ZIPs (no separate storage)
- Metadata extraction runs once on upload

## Migration Notes

No database migrations required. The skill service uses existing tables and storage infrastructure.

## References

### Original Research
- Research document: `tasks/001-2025-10-17-agent-skill-creation-flow/research.md`
- Existing skill example: `test-plugins/dev-tools-plugin/skills/code-reviewer/SKILL.md`

### Key Implementation Files
- Plugin validation: `app/services/plugin/validation.py:14-143`
- Plugin storage: `app/services/plugin/storage.py:28-189`
- Component counting: `app/services/plugin/storage.py:117-157`
- Upload route: `app/services/plugin/routes.py:33-180`
- Form pattern: `app/services/auth/routes.py:23-103`

### Test Patterns
- ZIP creation: `tests/test_plugin_upload.py:27-49`
- Component counting: `tests/test_plugin_storage.py:160-174`
- Form testing: `tests/test_auth.py`
