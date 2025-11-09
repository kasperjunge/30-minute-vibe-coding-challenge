"""Tests for project service."""

import pytest
from fastapi import HTTPException

from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services import project_service


def test_create_project_with_valid_data(db_session, sample_manager):
    """Test creating a project with valid data."""
    project_data = ProjectCreate(
        name="New Project",
        description="A test project",
        team_lead_id=sample_manager.id
    )

    project = project_service.create_project(project_data, db_session)

    assert project.id is not None
    assert project.name == "New Project"
    assert project.description == "A test project"
    assert project.team_lead_id == sample_manager.id
    assert project.is_active is True


def test_create_project_with_duplicate_name_fails(db_session, sample_project):
    """Test that creating a project with duplicate name fails."""
    project_data = ProjectCreate(
        name=sample_project.name,  # Use existing project name
        description="Another project",
        team_lead_id=sample_project.team_lead_id
    )

    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project(project_data, db_session)

    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail


def test_assign_team_lead_with_valid_user(db_session, sample_project):
    """Test assigning a team lead with valid user."""
    # Create a team lead user
    team_lead = User(
        email="teamlead@test.com",
        password_hash="hashed_password",
        full_name="Team Lead",
        role="team_lead",
        is_active=True
    )
    db_session.add(team_lead)
    db_session.commit()
    db_session.refresh(team_lead)

    # Assign team lead
    project = project_service.assign_team_lead(sample_project.id, team_lead.id, db_session)

    assert project.team_lead_id == team_lead.id


def test_assign_team_lead_with_manager_role(db_session, sample_project):
    """Test assigning a manager as team lead (should work)."""
    # Create a manager user
    manager = User(
        email="manager2@test.com",
        password_hash="hashed_password",
        full_name="Another Manager",
        role="manager",
        is_active=True
    )
    db_session.add(manager)
    db_session.commit()
    db_session.refresh(manager)

    # Assign manager as team lead
    project = project_service.assign_team_lead(sample_project.id, manager.id, db_session)

    assert project.team_lead_id == manager.id


def test_assign_team_lead_with_employee_role_fails(db_session, sample_project, sample_employee):
    """Test that assigning an employee as team lead fails."""
    with pytest.raises(HTTPException) as exc_info:
        project_service.assign_team_lead(sample_project.id, sample_employee.id, db_session)

    assert exc_info.value.status_code == 400
    assert "team_lead" in exc_info.value.detail or "manager" in exc_info.value.detail


def test_deactivate_project_sets_is_active_false(db_session, sample_project):
    """Test that deactivating a project sets is_active to False."""
    assert sample_project.is_active is True

    project = project_service.deactivate_project(sample_project.id, db_session)

    assert project.is_active is False


def test_get_active_projects_returns_only_active(db_session, sample_manager):
    """Test that get_active_projects returns only active projects."""
    # Create active project
    active_project = Project(
        name="Active Project",
        description="Active",
        team_lead_id=sample_manager.id,
        is_active=True
    )
    db_session.add(active_project)

    # Create inactive project
    inactive_project = Project(
        name="Inactive Project",
        description="Inactive",
        team_lead_id=sample_manager.id,
        is_active=False
    )
    db_session.add(inactive_project)
    db_session.commit()

    # Get active projects
    active_projects = project_service.get_active_projects(db_session)

    # Should only return the active project
    assert len(active_projects) == 1
    assert active_projects[0].name == "Active Project"
    assert active_projects[0].is_active is True


def test_update_project_name(db_session, sample_project):
    """Test updating project name."""
    update_data = ProjectUpdate(name="Updated Name")

    project = project_service.update_project(sample_project.id, update_data, db_session)

    assert project.name == "Updated Name"


def test_update_project_description(db_session, sample_project):
    """Test updating project description."""
    update_data = ProjectUpdate(description="Updated description")

    project = project_service.update_project(sample_project.id, update_data, db_session)

    assert project.description == "Updated description"


def test_update_project_team_lead(db_session, sample_project):
    """Test updating project team lead."""
    # Create new team lead
    new_team_lead = User(
        email="newlead@test.com",
        password_hash="hashed_password",
        full_name="New Team Lead",
        role="team_lead",
        is_active=True
    )
    db_session.add(new_team_lead)
    db_session.commit()
    db_session.refresh(new_team_lead)

    update_data = ProjectUpdate(team_lead_id=new_team_lead.id)

    project = project_service.update_project(sample_project.id, update_data, db_session)

    assert project.team_lead_id == new_team_lead.id


def test_create_project_with_invalid_team_lead_fails(db_session):
    """Test that creating a project with invalid team lead fails."""
    project_data = ProjectCreate(
        name="Test Project",
        description="Test",
        team_lead_id=99999  # Non-existent user
    )

    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project(project_data, db_session)

    assert exc_info.value.status_code == 404


def test_create_project_with_employee_as_team_lead_fails(db_session, sample_employee):
    """Test that creating a project with employee as team lead fails."""
    project_data = ProjectCreate(
        name="Test Project",
        description="Test",
        team_lead_id=sample_employee.id
    )

    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project(project_data, db_session)

    assert exc_info.value.status_code == 400
    assert "team_lead" in exc_info.value.detail or "manager" in exc_info.value.detail
