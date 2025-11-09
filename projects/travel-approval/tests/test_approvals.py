"""Tests for approval workflow."""

import pytest
from datetime import date, datetime
from decimal import Decimal
from fastapi.testclient import TestClient

from app.auth.session import session_manager
from app.main import app
from app.models import User, TravelRequest, Project, TAccount


@pytest.fixture
def team_lead(db_session):
    """Create a team lead user."""
    team_lead = User(
        email="teamlead@test.com",
        password_hash="hashed_password",
        full_name="Test Team Lead",
        role="team_lead",
        is_active=True
    )
    db_session.add(team_lead)
    db_session.commit()
    db_session.refresh(team_lead)
    return team_lead


@pytest.fixture
def project_with_team_lead(db_session, team_lead):
    """Create a project with a team lead assigned."""
    project = Project(
        name="Test Project Alpha",
        description="Test project with team lead",
        team_lead_id=team_lead.id,
        is_active=True
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def operations_request(db_session, sample_employee, sample_manager, sample_taccount):
    """Create an operations travel request."""
    travel_request = TravelRequest(
        requester_id=sample_employee.id,
        request_type="operations",
        destination="Copenhagen",
        start_date=date(2024, 6, 15),
        end_date=date(2024, 6, 18),
        purpose="Operations team meeting",
        estimated_cost=Decimal("5000.00"),
        taccount_id=sample_taccount.id,
        approver_id=sample_manager.id,
        status="pending"
    )
    db_session.add(travel_request)
    db_session.commit()
    db_session.refresh(travel_request)
    return travel_request


@pytest.fixture
def project_request(db_session, sample_employee, team_lead, project_with_team_lead, sample_taccount):
    """Create a project travel request."""
    travel_request = TravelRequest(
        requester_id=sample_employee.id,
        request_type="project",
        project_id=project_with_team_lead.id,
        destination="Oslo",
        start_date=date(2024, 7, 10),
        end_date=date(2024, 7, 12),
        purpose="Project Alpha kickoff meeting",
        estimated_cost=Decimal("7000.00"),
        taccount_id=sample_taccount.id,
        approver_id=team_lead.id,
        status="pending"
    )
    db_session.add(travel_request)
    db_session.commit()
    db_session.refresh(travel_request)
    return travel_request


def test_manager_sees_requests_from_direct_reports(db_session, sample_manager, operations_request):
    """Test that a manager sees pending requests from their direct reports."""
    client = TestClient(app)

    # Create session for manager
    session_token = session_manager.create_session(sample_manager.id)

    response = client.get(
        "/approvals",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    assert b"Pending Approvals" in response.content
    assert b"Copenhagen" in response.content  # Destination of operations_request
    assert b"Test Employee" in response.content  # Requester name


def test_team_lead_sees_requests_for_their_projects(db_session, team_lead, project_request):
    """Test that a team lead sees pending requests for projects they lead."""
    client = TestClient(app)

    # Create session for team lead
    session_token = session_manager.create_session(team_lead.id)

    response = client.get(
        "/approvals",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    assert b"Pending Approvals" in response.content
    assert b"Oslo" in response.content  # Destination of project_request
    assert b"Test Employee" in response.content  # Requester name


def test_manager_doesnt_see_other_teams_requests(db_session, sample_manager, team_lead, project_request):
    """Test that a manager doesn't see project requests not assigned to them."""
    client = TestClient(app)

    # Manager should not see project_request (assigned to team_lead)
    session_token = session_manager.create_session(sample_manager.id)

    response = client.get(
        "/approvals",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    # Should show no pending requests
    assert b"Oslo" not in response.content  # Destination of project_request


def test_employee_cannot_access_approvals_page(db_session, sample_employee):
    """Test that regular employees cannot access the approvals page."""
    client = TestClient(app)

    # Create session for employee
    session_token = session_manager.create_session(sample_employee.id)

    response = client.get(
        "/approvals",
        cookies={"travel_approval_session": session_token}
    )

    # Should return 403 Forbidden
    assert response.status_code == 403


def test_approver_can_view_request_detail(db_session, sample_manager, operations_request):
    """Test that an approver can view the detail page of a request."""
    client = TestClient(app)

    session_token = session_manager.create_session(sample_manager.id)

    response = client.get(
        f"/requests/{operations_request.id}",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    assert b"Travel Request" in response.content
    assert b"Copenhagen" in response.content
    assert b"Approval Actions" in response.content


def test_approver_can_approve_request(db_session, sample_manager, operations_request):
    """Test that an approver can approve a travel request."""
    client = TestClient(app)

    session_token = session_manager.create_session(sample_manager.id)

    # Approve the request with comments
    response = client.post(
        f"/requests/{operations_request.id}/approve",
        data={"comments": "Approved - looks good"},
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    # Should redirect to approvals page
    assert response.status_code == 303
    assert response.headers["location"] == "/approvals"

    # Verify the request was approved in the database
    db_session.refresh(operations_request)
    assert operations_request.status == "approved"
    assert operations_request.approval_comments == "Approved - looks good"
    assert operations_request.approval_date is not None


def test_approver_can_approve_without_comments(db_session, sample_manager, operations_request):
    """Test that an approver can approve without providing comments."""
    client = TestClient(app)

    session_token = session_manager.create_session(sample_manager.id)

    # Approve without comments
    response = client.post(
        f"/requests/{operations_request.id}/approve",
        data={},
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    # Should redirect to approvals page
    assert response.status_code == 303

    # Verify the request was approved
    db_session.refresh(operations_request)
    assert operations_request.status == "approved"
    assert operations_request.approval_comments is None


def test_approver_can_reject_with_reason(db_session, sample_manager, operations_request):
    """Test that an approver can reject a travel request with a reason."""
    client = TestClient(app)

    session_token = session_manager.create_session(sample_manager.id)

    # Reject the request with reason
    response = client.post(
        f"/requests/{operations_request.id}/reject",
        data={"reason": "Budget constraints for this quarter"},
        cookies={"travel_approval_session": session_token},
        follow_redirects=False
    )

    # Should redirect to approvals page
    assert response.status_code == 303
    assert response.headers["location"] == "/approvals"

    # Verify the request was rejected in the database
    db_session.refresh(operations_request)
    assert operations_request.status == "rejected"
    assert operations_request.rejection_reason == "Budget constraints for this quarter"
    assert operations_request.approval_date is not None


def test_reject_without_reason_returns_error(db_session, sample_manager, operations_request):
    """Test that rejecting without a reason returns an error."""
    client = TestClient(app)

    session_token = session_manager.create_session(sample_manager.id)

    # Try to reject without reason
    response = client.post(
        f"/requests/{operations_request.id}/reject",
        data={"reason": ""},
        cookies={"travel_approval_session": session_token}
    )

    # Should return 422 with error message
    assert response.status_code == 422
    assert b"Rejection reason is required" in response.content

    # Verify the request is still pending
    db_session.refresh(operations_request)
    assert operations_request.status == "pending"


def test_non_approver_cannot_approve(db_session, sample_manager, team_lead, project_request):
    """Test that a non-approver cannot approve a request (403 error)."""
    client = TestClient(app)

    # Manager tries to approve a project request assigned to team_lead
    session_token = session_manager.create_session(sample_manager.id)

    response = client.post(
        f"/requests/{project_request.id}/approve",
        data={"comments": "Attempting to approve"},
        cookies={"travel_approval_session": session_token}
    )

    # Should return 403 Forbidden
    assert response.status_code == 403

    # Verify the request is still pending
    db_session.refresh(project_request)
    assert project_request.status == "pending"


def test_employee_can_view_their_own_request_details(db_session, sample_employee, operations_request):
    """Test that an employee can view details of their own request."""
    client = TestClient(app)

    session_token = session_manager.create_session(sample_employee.id)

    response = client.get(
        f"/requests/{operations_request.id}",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    assert b"Travel Request" in response.content
    assert b"Copenhagen" in response.content
    # Employee should NOT see approval actions
    assert b"Approve" not in response.content or b"Approval Actions" not in response.content


def test_employee_cannot_view_others_request_details(db_session, sample_employee):
    """Test that an employee cannot view another employee's request."""
    # Create another employee with their own manager
    other_manager = User(
        email="othermanager@test.com",
        password_hash="hashed_password",
        full_name="Other Manager",
        role="manager",
        is_active=True
    )
    db_session.add(other_manager)
    db_session.commit()

    other_employee = User(
        email="otheremployee@test.com",
        password_hash="hashed_password",
        full_name="Other Employee",
        role="employee",
        manager_id=other_manager.id,
        is_active=True
    )
    db_session.add(other_employee)
    db_session.commit()

    # Create taccount for the request
    taccount = TAccount(
        account_code="T-9999",
        account_name="Test Account",
        description="Test",
        is_active=True
    )
    db_session.add(taccount)
    db_session.commit()

    # Create request for other employee
    other_request = TravelRequest(
        requester_id=other_employee.id,
        request_type="operations",
        destination="Berlin",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 3),
        purpose="Conference",
        estimated_cost=Decimal("6000.00"),
        taccount_id=taccount.id,
        approver_id=other_manager.id,
        status="pending"
    )
    db_session.add(other_request)
    db_session.commit()

    client = TestClient(app)

    # Try to view as sample_employee
    session_token = session_manager.create_session(sample_employee.id)

    response = client.get(
        f"/requests/{other_request.id}",
        cookies={"travel_approval_session": session_token}
    )

    # Should return 403 Forbidden
    assert response.status_code == 403


def test_cannot_approve_already_approved_request(db_session, sample_manager, operations_request):
    """Test that already approved requests cannot be approved again."""
    client = TestClient(app)

    # First, approve the request
    operations_request.status = "approved"
    operations_request.approval_date = datetime.utcnow()
    db_session.commit()

    session_token = session_manager.create_session(sample_manager.id)

    # Try to approve again
    response = client.post(
        f"/requests/{operations_request.id}/approve",
        data={"comments": "Trying to approve again"},
        cookies={"travel_approval_session": session_token}
    )

    # Should return 400 Bad Request
    assert response.status_code == 400


def test_only_pending_requests_shown_in_approvals_list(db_session, sample_manager, sample_employee, sample_taccount):
    """Test that only pending requests are shown in the approvals list."""
    client = TestClient(app)

    # Create multiple requests with different statuses
    pending_request = TravelRequest(
        requester_id=sample_employee.id,
        request_type="operations",
        destination="Paris",
        start_date=date(2024, 9, 1),
        end_date=date(2024, 9, 3),
        purpose="Meeting",
        estimated_cost=Decimal("4000.00"),
        taccount_id=sample_taccount.id,
        approver_id=sample_manager.id,
        status="pending"
    )
    db_session.add(pending_request)

    approved_request = TravelRequest(
        requester_id=sample_employee.id,
        request_type="operations",
        destination="London",
        start_date=date(2024, 10, 1),
        end_date=date(2024, 10, 3),
        purpose="Conference",
        estimated_cost=Decimal("5000.00"),
        taccount_id=sample_taccount.id,
        approver_id=sample_manager.id,
        status="approved",
        approval_date=datetime.utcnow()
    )
    db_session.add(approved_request)

    db_session.commit()

    session_token = session_manager.create_session(sample_manager.id)

    response = client.get(
        "/approvals",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    assert b"Paris" in response.content  # Pending request shown
    assert b"London" not in response.content  # Approved request not shown
