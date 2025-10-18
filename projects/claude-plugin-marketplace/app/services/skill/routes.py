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
