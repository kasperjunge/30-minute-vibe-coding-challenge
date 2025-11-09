"""Tests for the reports routes."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.project import Project
from app.models.taccount import TAccount
from app.models.travel_request import TravelRequest
from app.auth.session import session_manager


@pytest.fixture
def accounting_user(db_session: Session):
    """Create an accounting user for testing."""
    user = User(
        email="accounting@xyz.dk",
        password_hash="hash",
        full_name="Accounting User",
        role="accounting"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def manager_user(db_session: Session):
    """Create a manager user for testing."""
    user = User(
        email="manager@xyz.dk",
        password_hash="hash",
        full_name="Manager User",
        role="manager"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def employee_user(db_session: Session, manager_user: User):
    """Create an employee user for testing."""
    user = User(
        email="employee@xyz.dk",
        password_hash="hash",
        full_name="Employee User",
        role="employee",
        manager_id=manager_user.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session):
    """Create an admin user for testing."""
    user = User(
        email="admin@xyz.dk",
        password_hash="hash",
        full_name="Admin User",
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_data(db_session: Session, employee_user: User, manager_user: User):
    """Create sample data for testing reports."""
    # Create T-accounts
    taccount1 = TAccount(
        account_code="T-1234",
        account_name="Marketing",
        description="Marketing budget"
    )
    taccount2 = TAccount(
        account_code="T-5678",
        account_name="Engineering",
        description="Engineering budget"
    )
    db_session.add_all([taccount1, taccount2])
    db_session.flush()

    # Create team lead and project
    team_lead = User(
        email="teamlead@xyz.dk",
        password_hash="hash",
        full_name="Team Lead",
        role="team_lead"
    )
    db_session.add(team_lead)
    db_session.flush()

    project1 = Project(
        name="Project Alpha",
        description="Alpha project",
        team_lead_id=team_lead.id
    )
    db_session.add(project1)
    db_session.flush()

    # Create approved travel requests
    today = datetime.utcnow()
    week_ago = today - timedelta(days=7)

    request1 = TravelRequest(
        requester_id=employee_user.id,
        request_type="operations",
        destination="Copenhagen",
        start_date=date.today() + timedelta(days=10),
        end_date=date.today() + timedelta(days=12),
        purpose="Client meeting",
        estimated_cost=Decimal("5000.00"),
        taccount_id=taccount1.id,
        status="approved",
        approver_id=manager_user.id,
        approval_date=today,
        approval_comments="Approved"
    )

    request2 = TravelRequest(
        requester_id=employee_user.id,
        request_type="operations",
        destination="Stockholm",
        start_date=date.today() + timedelta(days=15),
        end_date=date.today() + timedelta(days=17),
        purpose="Conference",
        estimated_cost=Decimal("8000.00"),
        taccount_id=taccount1.id,
        status="approved",
        approver_id=manager_user.id,
        approval_date=week_ago,
        approval_comments="Approved"
    )

    request3 = TravelRequest(
        requester_id=employee_user.id,
        request_type="project",
        project_id=project1.id,
        destination="Berlin",
        start_date=date.today() + timedelta(days=20),
        end_date=date.today() + timedelta(days=22),
        purpose="Project work",
        estimated_cost=Decimal("12000.00"),
        taccount_id=taccount2.id,
        status="approved",
        approver_id=team_lead.id,
        approval_date=week_ago,
        approval_comments="Approved"
    )

    db_session.add_all([request1, request2, request3])
    db_session.commit()

    return {
        "taccount1": taccount1,
        "taccount2": taccount2,
        "project1": project1,
        "requests": [request1, request2, request3]
    }


def test_accounting_user_can_access_reports(client, db_session: Session, accounting_user: User, sample_data):
    """Test that accounting staff can access the reports page."""
    # Create session cookie
    session_token = session_manager.create_session(accounting_user.id)

    # Access reports page
    response = client.get(
        "/reports",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    assert b"Travel Request Reports" in response.content


def test_admin_user_can_access_reports(client, db_session: Session, admin_user: User, sample_data):
    """Test that admin users can access the reports page."""
    # Create session cookie
    session_token = session_manager.create_session(admin_user.id)

    # Access reports page
    response = client.get(
        "/reports",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    assert b"Travel Request Reports" in response.content


def test_non_accounting_cannot_access_reports(client, db_session: Session, employee_user: User):
    """Test that non-accounting users cannot access reports (403 error)."""
    # Create session cookie for employee
    session_token = session_manager.create_session(employee_user.id)

    # Try to access reports page
    response = client.get(
        "/reports",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 403


def test_unauthenticated_user_cannot_access_reports(client, db_session: Session):
    """Test that unauthenticated users cannot access reports (401 error)."""
    # Try to access without session cookie
    response = client.get("/reports")

    assert response.status_code == 401


def test_reports_shows_approved_requests_by_default(client, db_session: Session, accounting_user: User, sample_data):
    """Test that reports page shows approved requests by default."""
    session_token = session_manager.create_session(accounting_user.id)

    response = client.get(
        "/reports",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    # Should show all 3 approved requests
    assert b"Copenhagen" in response.content
    assert b"Stockholm" in response.content
    assert b"Berlin" in response.content


def test_reports_filter_by_taccount(client, db_session: Session, accounting_user: User, sample_data):
    """Test filtering reports by T-account."""
    session_token = session_manager.create_session(accounting_user.id)
    taccount1 = sample_data["taccount1"]

    response = client.get(
        f"/reports?taccount_id={taccount1.id}",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    # Should show only requests with taccount1 (Copenhagen and Stockholm)
    assert b"Copenhagen" in response.content
    assert b"Stockholm" in response.content
    assert b"Berlin" not in response.content


def test_reports_filter_by_project(client, db_session: Session, accounting_user: User, sample_data):
    """Test filtering reports by project."""
    session_token = session_manager.create_session(accounting_user.id)
    project1 = sample_data["project1"]

    response = client.get(
        f"/reports?project_id={project1.id}",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    # Should show only project requests (Berlin)
    assert b"Berlin" in response.content
    assert b"Copenhagen" not in response.content
    assert b"Stockholm" not in response.content


def test_reports_filter_by_date_range(client, db_session: Session, accounting_user: User, sample_data):
    """Test filtering reports by date range."""
    session_token = session_manager.create_session(accounting_user.id)

    # Filter for requests approved in last 5 days
    date_from = (datetime.utcnow() - timedelta(days=5)).date()
    date_to = datetime.utcnow().date()

    response = client.get(
        f"/reports?date_from={date_from}&date_to={date_to}",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    # Should show only request1 (approved today)
    assert b"Copenhagen" in response.content
    # Stockholm and Berlin were approved more than 5 days ago
    assert b"Stockholm" not in response.content
    assert b"Berlin" not in response.content


def test_reports_filter_by_status(client, db_session: Session, accounting_user: User, sample_data, employee_user: User):
    """Test filtering reports by status."""
    # Create a pending request
    taccount = sample_data["taccount1"]
    pending_request = TravelRequest(
        requester_id=employee_user.id,
        request_type="operations",
        destination="Oslo",
        start_date=date.today() + timedelta(days=5),
        end_date=date.today() + timedelta(days=7),
        purpose="Meeting",
        estimated_cost=Decimal("3000.00"),
        taccount_id=taccount.id,
        status="pending",
        approver_id=employee_user.manager_id
    )
    db_session.add(pending_request)
    db_session.commit()

    session_token = session_manager.create_session(accounting_user.id)

    # Filter for pending requests
    response = client.get(
        "/reports?status=pending",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    assert b"Oslo" in response.content
    # Should not show approved requests
    assert b"Copenhagen" not in response.content


def test_reports_shows_total_count_and_cost(client, db_session: Session, accounting_user: User, sample_data):
    """Test that reports page shows total count and cost."""
    session_token = session_manager.create_session(accounting_user.id)

    response = client.get(
        "/reports",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    # Total count should be 3
    assert b"3" in response.content
    # Total cost should be 25000.00 (5000 + 8000 + 12000)
    assert b"25,000.00" in response.content or b"25000.00" in response.content


def test_export_csv_downloads_file(client, db_session: Session, accounting_user: User, sample_data):
    """Test that export CSV endpoint downloads a file with correct content."""
    session_token = session_manager.create_session(accounting_user.id)

    response = client.get(
        "/reports/export",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]

    # Check CSV content
    csv_content = response.text
    assert "Request ID" in csv_content
    assert "Employee Name" in csv_content
    assert "Destination" in csv_content
    assert "Copenhagen" in csv_content
    assert "Stockholm" in csv_content
    assert "Berlin" in csv_content


def test_export_csv_respects_filters(client, db_session: Session, accounting_user: User, sample_data):
    """Test that CSV export respects filter parameters."""
    session_token = session_manager.create_session(accounting_user.id)
    taccount1 = sample_data["taccount1"]

    # Export with T-account filter
    response = client.get(
        f"/reports/export?taccount_id={taccount1.id}",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200

    csv_content = response.text
    # Should include only taccount1 requests
    assert "Copenhagen" in csv_content
    assert "Stockholm" in csv_content
    assert "Berlin" not in csv_content


def test_non_accounting_cannot_export_csv(client, db_session: Session, employee_user: User):
    """Test that non-accounting users cannot export CSV (403 error)."""
    session_token = session_manager.create_session(employee_user.id)

    response = client.get(
        "/reports/export",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 403


def test_reports_pagination_works(client, db_session: Session, accounting_user: User, employee_user: User, manager_user: User):
    """Test that pagination works for large result sets."""
    # Create many approved requests (more than 50)
    taccount = TAccount(
        account_code="T-9999",
        account_name="Test Account",
        description="Test"
    )
    db_session.add(taccount)
    db_session.flush()

    requests = []
    for i in range(60):
        request = TravelRequest(
            requester_id=employee_user.id,
            request_type="operations",
            destination=f"City {i}",
            start_date=date.today() + timedelta(days=i),
            end_date=date.today() + timedelta(days=i+2),
            purpose=f"Purpose {i}",
            estimated_cost=Decimal("1000.00"),
            taccount_id=taccount.id,
            status="approved",
            approver_id=manager_user.id,
            approval_date=datetime.utcnow()
        )
        requests.append(request)

    db_session.add_all(requests)
    db_session.commit()

    session_token = session_manager.create_session(accounting_user.id)

    # Get first page
    response = client.get(
        "/reports?page=1",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    # Should show 50 per page
    assert b"Showing 1 - 50 of 60" in response.content or b"1 - 50" in response.content

    # Get second page
    response = client.get(
        "/reports?page=2",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    # Should show remaining 10
    assert b"51" in response.content


def test_reports_shows_empty_state_when_no_results(client, db_session: Session, accounting_user: User):
    """Test that reports page shows empty state when no requests match filters."""
    session_token = session_manager.create_session(accounting_user.id)

    # Filter for dates in the future (no requests)
    date_from = date.today() + timedelta(days=100)
    date_to = date.today() + timedelta(days=200)

    response = client.get(
        f"/reports?date_from={date_from}&date_to={date_to}",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 200
    assert b"No requests found" in response.content


def test_manager_cannot_access_reports(client, db_session: Session, manager_user: User):
    """Test that managers cannot access reports (403 error)."""
    session_token = session_manager.create_session(manager_user.id)

    response = client.get(
        "/reports",
        cookies={"travel_approval_session": session_token}
    )

    assert response.status_code == 403
