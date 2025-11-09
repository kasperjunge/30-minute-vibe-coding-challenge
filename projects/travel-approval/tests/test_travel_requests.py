"""Tests for travel request form and creation."""

import pytest
from fastapi.testclient import TestClient
from decimal import Decimal

from app.auth.password import hash_password
from app.auth.session import session_manager
from app.main import app
from app.models import User, TravelRequest, Project, TAccount


def test_get_new_request_form_renders_for_authenticated_user(db_session, sample_employee, sample_project, sample_taccount):
    """Test GET /requests/new renders form for authenticated user."""
    client = TestClient(app)

    # Create session for authenticated user
    session_token = session_manager.create_session(sample_employee.id)

    # Access form
    response = client.get(
        "/requests/new",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    # Check that form elements are present
    assert b"destination" in response.content
    assert b"start_date" in response.content
    assert b"end_date" in response.content
    assert b"purpose" in response.content
    assert b"estimated_cost" in response.content
    assert b"taccount_id" in response.content
    assert b"request_type" in response.content


def test_get_new_request_form_redirects_unauthenticated(db_session):
    """Test GET /requests/new returns 401 for unauthenticated users."""
    client = TestClient(app)

    # Access form without authentication
    response = client.get("/requests/new", follow_redirects=False)

    # Should return 401 Unauthorized (based on actual behavior)
    assert response.status_code == 401


def test_post_creates_request_with_valid_operations_data(db_session, sample_employee, sample_manager, sample_taccount):
    """Test POST creates request with valid operations data."""
    client = TestClient(app)

    # Create session for authenticated employee
    session_token = session_manager.create_session(sample_employee.id)

    # Submit operations request
    response = client.post(
        "/requests/new",
        data={
            "request_type": "operations",
            "destination": "Copenhagen",
            "start_date": "2025-12-01",
            "end_date": "2025-12-05",
            "purpose": "Client meeting and business development",
            "estimated_cost": "5000.00",
            "taccount_id": sample_taccount.id,
        },
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    # Should redirect to dashboard on success
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"

    # Verify request was created in database
    travel_request = db_session.query(TravelRequest).filter(
        TravelRequest.requester_id == sample_employee.id
    ).first()

    assert travel_request is not None
    assert travel_request.request_type == "operations"
    assert travel_request.destination == "Copenhagen"
    assert travel_request.project_id is None
    assert travel_request.estimated_cost == Decimal("5000.00")
    assert travel_request.taccount_id == sample_taccount.id
    assert travel_request.status == "pending"
    # Should route to employee's manager
    assert travel_request.approver_id == sample_manager.id


def test_post_creates_request_with_valid_project_data(db_session, sample_employee, sample_manager, sample_project, sample_taccount):
    """Test POST creates request with valid project data."""
    client = TestClient(app)

    # Create session for authenticated employee
    session_token = session_manager.create_session(sample_employee.id)

    # Submit project request
    response = client.post(
        "/requests/new",
        data={
            "request_type": "project",
            "project_id": sample_project.id,
            "destination": "London",
            "start_date": "2025-12-01",
            "end_date": "2025-12-05",
            "purpose": "Project kickoff meeting",
            "estimated_cost": "7500.50",
            "taccount_id": sample_taccount.id,
        },
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    # Should redirect to dashboard on success
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"

    # Verify request was created in database
    travel_request = db_session.query(TravelRequest).filter(
        TravelRequest.requester_id == sample_employee.id
    ).first()

    assert travel_request is not None
    assert travel_request.request_type == "project"
    assert travel_request.destination == "London"
    assert travel_request.project_id == sample_project.id
    assert travel_request.estimated_cost == Decimal("7500.50")
    assert travel_request.taccount_id == sample_taccount.id
    assert travel_request.status == "pending"
    # Should route to project's team lead
    assert travel_request.approver_id == sample_project.team_lead_id


def test_post_fails_when_project_type_but_no_project_id(db_session, sample_employee, sample_taccount):
    """Test POST fails when project type selected but no project_id provided."""
    client = TestClient(app)

    # Create session for authenticated employee
    session_token = session_manager.create_session(sample_employee.id)

    # Submit project request without project_id
    response = client.post(
        "/requests/new",
        data={
            "request_type": "project",
            # project_id is missing
            "destination": "Amsterdam",
            "start_date": "2025-12-01",
            "end_date": "2025-12-05",
            "purpose": "Project milestone review",
            "estimated_cost": "3000.00",
            "taccount_id": sample_taccount.id,
        },
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    # Should return error (422 Unprocessable Entity)
    assert response.status_code == 422

    # Check error message is displayed
    assert b"validation" in response.content or b"Project ID is required" in response.content

    # Verify request was NOT created in database
    travel_request = db_session.query(TravelRequest).filter(
        TravelRequest.requester_id == sample_employee.id
    ).first()
    assert travel_request is None


def test_post_fails_when_end_date_before_start_date(db_session, sample_employee, sample_taccount):
    """Test POST fails when end_date is before start_date."""
    client = TestClient(app)

    # Create session for authenticated employee
    session_token = session_manager.create_session(sample_employee.id)

    # Submit request with end_date before start_date
    response = client.post(
        "/requests/new",
        data={
            "request_type": "operations",
            "destination": "Paris",
            "start_date": "2025-12-10",
            "end_date": "2025-12-05",  # Before start_date
            "purpose": "Conference attendance",
            "estimated_cost": "4000.00",
            "taccount_id": sample_taccount.id,
        },
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    # Should return error (422 Unprocessable Entity)
    assert response.status_code == 422

    # Check error message is displayed
    assert b"validation" in response.content or b"End date" in response.content

    # Verify request was NOT created in database
    travel_request = db_session.query(TravelRequest).filter(
        TravelRequest.requester_id == sample_employee.id
    ).first()
    assert travel_request is None


def test_post_fails_when_taccount_not_selected(db_session, sample_employee):
    """Test POST fails when T-account is not selected."""
    client = TestClient(app)

    # Create session for authenticated employee
    session_token = session_manager.create_session(sample_employee.id)

    # Submit request without taccount_id (Form(...) makes it required, so this should error)
    # The route expects taccount_id as Form(...) which means it's required
    # FastAPI will raise a 422 validation error for missing required fields
    response = client.post(
        "/requests/new",
        data={
            "request_type": "operations",
            "destination": "Berlin",
            "start_date": "2025-12-01",
            "end_date": "2025-12-05",
            "purpose": "Training workshop",
            "estimated_cost": "3500.00",
            # taccount_id is missing - this should cause validation error
        },
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    # FastAPI returns 422 for missing required form fields
    assert response.status_code == 422


def test_post_fails_with_negative_cost(db_session, sample_employee, sample_taccount):
    """Test POST fails when estimated_cost is negative."""
    client = TestClient(app)

    # Create session for authenticated employee
    session_token = session_manager.create_session(sample_employee.id)

    # Submit request with negative cost
    response = client.post(
        "/requests/new",
        data={
            "request_type": "operations",
            "destination": "Brussels",
            "start_date": "2025-12-01",
            "end_date": "2025-12-05",
            "purpose": "EU meetings",
            "estimated_cost": "-500.00",  # Negative cost
            "taccount_id": sample_taccount.id,
        },
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    # Should return error (422 Unprocessable Entity)
    assert response.status_code == 422

    # Check error message is displayed
    assert b"validation" in response.content or b"cost" in response.content

    # Verify request was NOT created in database
    travel_request = db_session.query(TravelRequest).filter(
        TravelRequest.requester_id == sample_employee.id
    ).first()
    assert travel_request is None


def test_request_automatically_routed_to_manager_for_operations(db_session, sample_employee, sample_manager, sample_taccount):
    """Test request is automatically routed to correct approver (manager) for operations."""
    client = TestClient(app)

    # Create session for authenticated employee
    session_token = session_manager.create_session(sample_employee.id)

    # Submit operations request
    response = client.post(
        "/requests/new",
        data={
            "request_type": "operations",
            "destination": "Stockholm",
            "start_date": "2025-12-01",
            "end_date": "2025-12-05",
            "purpose": "Annual operations review",
            "estimated_cost": "6000.00",
            "taccount_id": sample_taccount.id,
        },
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    assert response.status_code == 303

    # Verify request was routed to the employee's manager
    travel_request = db_session.query(TravelRequest).filter(
        TravelRequest.requester_id == sample_employee.id
    ).first()

    assert travel_request is not None
    assert travel_request.approver_id == sample_manager.id
    assert travel_request.approver_id == sample_employee.manager_id


def test_request_automatically_routed_to_team_lead_for_project(db_session, sample_employee, sample_manager, sample_project, sample_taccount):
    """Test request is automatically routed to correct approver (team lead) for project."""
    client = TestClient(app)

    # Create session for authenticated employee
    session_token = session_manager.create_session(sample_employee.id)

    # Submit project request
    response = client.post(
        "/requests/new",
        data={
            "request_type": "project",
            "project_id": sample_project.id,
            "destination": "Oslo",
            "start_date": "2025-12-01",
            "end_date": "2025-12-05",
            "purpose": "Project planning session",
            "estimated_cost": "4500.00",
            "taccount_id": sample_taccount.id,
        },
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    assert response.status_code == 303

    # Verify request was routed to the project's team lead
    travel_request = db_session.query(TravelRequest).filter(
        TravelRequest.requester_id == sample_employee.id
    ).first()

    assert travel_request is not None
    assert travel_request.approver_id == sample_project.team_lead_id
    # Verify it's the manager (who is the team lead in the fixture)
    assert travel_request.approver_id == sample_manager.id


def test_post_fails_when_employee_has_no_manager(db_session, sample_taccount):
    """Test POST fails gracefully when employee has no manager assigned for operations request."""
    client = TestClient(app)

    # Create employee without manager
    employee_no_manager = User(
        email="orphan@test.com",
        password_hash=hash_password("password123"),
        full_name="Orphan Employee",
        role="employee",
        manager_id=None,  # No manager
        is_active=True
    )
    db_session.add(employee_no_manager)
    db_session.commit()
    db_session.refresh(employee_no_manager)

    # Create session for this employee
    session_token = session_manager.create_session(employee_no_manager.id)

    # Submit operations request
    response = client.post(
        "/requests/new",
        data={
            "request_type": "operations",
            "destination": "Copenhagen",
            "start_date": "2025-12-01",
            "end_date": "2025-12-05",
            "purpose": "Client meeting",
            "estimated_cost": "5000.00",
            "taccount_id": sample_taccount.id,
        },
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    # Should return error (422)
    assert response.status_code == 422

    # Check error message about missing manager
    assert b"No manager assigned" in response.content or b"approver" in response.content

    # Verify request was NOT created
    travel_request = db_session.query(TravelRequest).filter(
        TravelRequest.requester_id == employee_no_manager.id
    ).first()
    assert travel_request is None


def test_post_with_same_start_and_end_date_succeeds(db_session, sample_employee, sample_taccount):
    """Test POST succeeds when start_date equals end_date (same day trip)."""
    client = TestClient(app)

    # Create session for authenticated employee
    session_token = session_manager.create_session(sample_employee.id)

    # Submit request with same start and end date
    response = client.post(
        "/requests/new",
        data={
            "request_type": "operations",
            "destination": "Aarhus",
            "start_date": "2025-12-01",
            "end_date": "2025-12-01",  # Same day
            "purpose": "One-day workshop",
            "estimated_cost": "1500.00",
            "taccount_id": sample_taccount.id,
        },
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    # Should succeed
    assert response.status_code == 303

    # Verify request was created
    travel_request = db_session.query(TravelRequest).filter(
        TravelRequest.requester_id == sample_employee.id
    ).first()

    assert travel_request is not None
    assert str(travel_request.start_date) == "2025-12-01"
    assert str(travel_request.end_date) == "2025-12-01"
