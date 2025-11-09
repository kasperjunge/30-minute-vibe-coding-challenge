"""Admin routes - project and T-account management."""

from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import get_current_user, require_role
from app.database import get_db
from app.models.project import Project
from app.models.taccount import TAccount
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.taccount import TAccountCreate, TAccountResponse, TAccountUpdate
from app.services import audit_service, project_service

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/taccounts", response_class=HTMLResponse)
async def taccounts_page(
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Display T-accounts management page."""
    # Get all T-accounts
    taccounts = db.query(TAccount).order_by(TAccount.is_active.desc(), TAccount.account_code).all()

    return templates.TemplateResponse(
        request,
        "admin/taccounts.html",
        {
            "current_user": current_user,
            "taccounts": taccounts,
            "unread_count": 0,  # TODO: Implement notification count
        },
    )


@router.post("/taccounts")
async def create_taccount(
    account_code: str = Form(...),
    account_name: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Create a new T-account."""
    # Check if account code already exists
    existing = db.query(TAccount).filter(TAccount.account_code == account_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"T-account with code '{account_code}' already exists",
        )

    # Create new T-account
    taccount = TAccount(
        account_code=account_code,
        account_name=account_name,
        description=description,
        is_active=True,
    )

    db.add(taccount)
    db.commit()
    db.refresh(taccount)

    return RedirectResponse(url="/admin/taccounts", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/taccounts/{taccount_id}")
async def update_taccount(
    taccount_id: int,
    account_code: str = Form(...),
    account_name: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Update an existing T-account."""
    # Get T-account
    taccount = db.query(TAccount).filter(TAccount.id == taccount_id).first()
    if not taccount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="T-account not found",
        )

    # Check if account code is being changed and if it conflicts
    if account_code != taccount.account_code:
        existing = db.query(TAccount).filter(
            TAccount.account_code == account_code,
            TAccount.id != taccount_id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"T-account with code '{account_code}' already exists",
            )

    # Update T-account
    taccount.account_code = account_code
    taccount.account_name = account_name
    taccount.description = description

    db.commit()
    db.refresh(taccount)

    return RedirectResponse(url="/admin/taccounts", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/taccounts/{taccount_id}/deactivate")
async def deactivate_taccount(
    taccount_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Deactivate a T-account."""
    # Get T-account
    taccount = db.query(TAccount).filter(TAccount.id == taccount_id).first()
    if not taccount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="T-account not found",
        )

    # Deactivate T-account
    taccount.is_active = False

    db.commit()

    return RedirectResponse(url="/admin/taccounts", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/taccounts/{taccount_id}/activate")
async def activate_taccount(
    taccount_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Activate a T-account."""
    # Get T-account
    taccount = db.query(TAccount).filter(TAccount.id == taccount_id).first()
    if not taccount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="T-account not found",
        )

    # Activate T-account
    taccount.is_active = True

    db.commit()

    return RedirectResponse(url="/admin/taccounts", status_code=status.HTTP_303_SEE_OTHER)


# Project Management Routes


@router.get("/projects", response_class=HTMLResponse)
async def list_projects(
    request: Request,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Display admin project management page."""
    # Get all projects (active and inactive) with eager loading
    all_projects = (
        db.query(Project)
        .options(joinedload(Project.team_lead))
        .order_by(Project.is_active.desc(), Project.name)
        .all()
    )
    active_projects = [p for p in all_projects if p.is_active]
    inactive_projects = [p for p in all_projects if not p.is_active]

    # Get all users with team_lead or manager roles for the dropdown
    team_leads = (
        db.query(User)
        .filter(User.role.in_(["team_lead", "manager"]), User.is_active == True)
        .order_by(User.full_name)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "admin/projects.html",
        {
            "current_user": current_user,
            "active_projects": active_projects,
            "inactive_projects": inactive_projects,
            "team_leads": team_leads,
            "unread_count": 0,  # TODO: Implement notification count
        },
    )


@router.post("/projects", response_class=HTMLResponse)
async def create_project(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    team_lead_id: int = Form(...),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Create a new project."""
    try:
        project_data = ProjectCreate(
            name=name,
            description=description,
            team_lead_id=team_lead_id,
        )

        project = project_service.create_project(project_data, db)

        # Log the project creation
        audit_service.log_action(
            user_id=current_user.id,
            action="create_project",
            entity_type="project",
            entity_id=project.id,
            details={
                "project_name": project.name,
                "team_lead_id": project.team_lead_id,
                "description": project.description,
            },
            db=db,
        )

        return RedirectResponse(
            url="/admin/projects?success=Project created successfully",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except HTTPException as e:
        return RedirectResponse(
            url=f"/admin/projects?error={e.detail}",
            status_code=status.HTTP_303_SEE_OTHER,
        )


@router.post("/projects/{project_id}", response_class=HTMLResponse)
async def update_project(
    project_id: int,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    team_lead_id: int = Form(...),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Update an existing project."""
    try:
        project_data = ProjectUpdate(
            name=name,
            description=description,
            team_lead_id=team_lead_id,
        )

        project = project_service.update_project(project_id, project_data, db)

        # Log the project update
        audit_service.log_action(
            user_id=current_user.id,
            action="update_project",
            entity_type="project",
            entity_id=project.id,
            details={
                "project_name": project.name,
                "team_lead_id": project.team_lead_id,
                "description": project.description,
            },
            db=db,
        )

        return RedirectResponse(
            url="/admin/projects?success=Project updated successfully",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except HTTPException as e:
        return RedirectResponse(
            url=f"/admin/projects?error={e.detail}",
            status_code=status.HTTP_303_SEE_OTHER,
        )


@router.post("/projects/{project_id}/deactivate", response_class=HTMLResponse)
async def deactivate_project(
    project_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Deactivate a project."""
    try:
        project_service.deactivate_project(project_id, db)

        return RedirectResponse(
            url="/admin/projects?success=Project deactivated successfully",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except HTTPException as e:
        return RedirectResponse(
            url=f"/admin/projects?error={e.detail}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
