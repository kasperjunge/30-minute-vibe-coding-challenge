"""Project service - business logic for project management."""

from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_project(project_data: ProjectCreate, db: Session) -> Project:
    """
    Create a new project.

    Args:
        project_data: Project creation data
        db: Database session

    Returns:
        Created project

    Raises:
        HTTPException: If project name already exists or team lead is invalid
    """
    # Check if project name already exists
    existing_project = db.query(Project).filter(Project.name == project_data.name).first()
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with name '{project_data.name}' already exists",
        )

    # Verify team lead exists and has appropriate role
    team_lead = db.query(User).filter(User.id == project_data.team_lead_id).first()
    if not team_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {project_data.team_lead_id} not found",
        )

    if team_lead.role not in ["team_lead", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User must have 'team_lead' or 'manager' role. Current role: '{team_lead.role}'",
        )

    # Create project
    project = Project(
        name=project_data.name,
        description=project_data.description,
        team_lead_id=project_data.team_lead_id,
        is_active=True,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def update_project(project_id: int, project_data: ProjectUpdate, db: Session) -> Project:
    """
    Update an existing project.

    Args:
        project_id: ID of project to update
        project_data: Project update data
        db: Database session

    Returns:
        Updated project

    Raises:
        HTTPException: If project not found or validation fails
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Update name if provided
    if project_data.name is not None:
        # Check if new name conflicts with existing project
        existing_project = (
            db.query(Project)
            .filter(Project.name == project_data.name, Project.id != project_id)
            .first()
        )
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project with name '{project_data.name}' already exists",
            )
        project.name = project_data.name

    # Update description if provided
    if project_data.description is not None:
        project.description = project_data.description

    # Update team lead if provided
    if project_data.team_lead_id is not None:
        team_lead = db.query(User).filter(User.id == project_data.team_lead_id).first()
        if not team_lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {project_data.team_lead_id} not found",
            )

        if team_lead.role not in ["team_lead", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User must have 'team_lead' or 'manager' role. Current role: '{team_lead.role}'",
            )
        project.team_lead_id = project_data.team_lead_id

    db.commit()
    db.refresh(project)

    return project


def assign_team_lead(project_id: int, user_id: int, db: Session) -> Project:
    """
    Assign a team lead to a project.

    Args:
        project_id: ID of project
        user_id: ID of user to assign as team lead
        db: Database session

    Returns:
        Updated project

    Raises:
        HTTPException: If project or user not found, or user doesn't have appropriate role
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Verify user exists and has appropriate role
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    if user.role not in ["team_lead", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User must have 'team_lead' or 'manager' role. Current role: '{user.role}'",
        )

    # Update project
    project.team_lead_id = user_id
    db.commit()
    db.refresh(project)

    return project


def deactivate_project(project_id: int, db: Session) -> Project:
    """
    Deactivate a project.

    Args:
        project_id: ID of project to deactivate
        db: Database session

    Returns:
        Deactivated project

    Raises:
        HTTPException: If project not found
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Deactivate
    project.is_active = False
    db.commit()
    db.refresh(project)

    return project


def get_active_projects(db: Session) -> List[Project]:
    """
    Get all active projects.

    Args:
        db: Database session

    Returns:
        List of active projects
    """
    return db.query(Project).filter(Project.is_active == True).all()
