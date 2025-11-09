"""Tests for the reporting service."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.project import Project
from app.models.taccount import TAccount
from app.models.travel_request import TravelRequest
from app.services.reporting_service import (
    get_approved_requests,
    export_to_csv,
    get_summary_by_taccount
)


@pytest.fixture
def sample_data(db_session: Session):
    """Create sample data for testing reports."""
    # Create users
    manager = User(
        email="manager@xyz.dk",
        password_hash="hash",
        full_name="Manager User",
        role="manager"
    )
    db_session.add(manager)
    db_session.flush()

    employee1 = User(
        email="employee1@xyz.dk",
        password_hash="hash",
        full_name="Employee One",
        role="employee",
        manager_id=manager.id
    )
    employee2 = User(
        email="employee2@xyz.dk",
        password_hash="hash",
        full_name="Employee Two",
        role="employee",
        manager_id=manager.id
    )
    db_session.add_all([employee1, employee2])
    db_session.flush()

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

    # Create approved travel requests with different dates and T-accounts
    today = datetime.utcnow()
    week_ago = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)

    request1 = TravelRequest(
        requester_id=employee1.id,
        request_type="operations",
        destination="Copenhagen",
        start_date=date.today() + timedelta(days=10),
        end_date=date.today() + timedelta(days=12),
        purpose="Client meeting",
        estimated_cost=Decimal("5000.00"),
        taccount_id=taccount1.id,
        status="approved",
        approver_id=manager.id,
        approval_date=today,
        approval_comments="Approved"
    )

    request2 = TravelRequest(
        requester_id=employee2.id,
        request_type="operations",
        destination="Stockholm",
        start_date=date.today() + timedelta(days=15),
        end_date=date.today() + timedelta(days=17),
        purpose="Conference",
        estimated_cost=Decimal("8000.00"),
        taccount_id=taccount1.id,
        status="approved",
        approver_id=manager.id,
        approval_date=week_ago,
        approval_comments="Approved"
    )

    request3 = TravelRequest(
        requester_id=employee1.id,
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
        approval_date=two_weeks_ago,
        approval_comments="Approved"
    )

    request4 = TravelRequest(
        requester_id=employee2.id,
        request_type="operations",
        destination="Oslo",
        start_date=date.today() + timedelta(days=25),
        end_date=date.today() + timedelta(days=27),
        purpose="Training",
        estimated_cost=Decimal("6000.00"),
        taccount_id=taccount2.id,
        status="pending",
        approver_id=manager.id
    )

    request5 = TravelRequest(
        requester_id=employee1.id,
        request_type="operations",
        destination="Paris",
        start_date=date.today() + timedelta(days=30),
        end_date=date.today() + timedelta(days=32),
        purpose="Sales meeting",
        estimated_cost=Decimal("7500.00"),
        taccount_id=taccount1.id,
        status="rejected",
        approver_id=manager.id,
        approval_date=today,
        rejection_reason="Budget constraints"
    )

    db_session.add_all([request1, request2, request3, request4, request5])
    db_session.commit()

    return {
        "manager": manager,
        "employee1": employee1,
        "employee2": employee2,
        "team_lead": team_lead,
        "taccount1": taccount1,
        "taccount2": taccount2,
        "project1": project1,
        "requests": [request1, request2, request3, request4, request5]
    }


def test_get_approved_requests_no_filters(db_session: Session, sample_data):
    """Test getting all approved requests without filters."""
    results = get_approved_requests(db_session)

    # Should return 3 approved requests
    assert len(results) == 3
    assert all(req.status == "approved" for req in results)

    # Should be ordered by approval_date descending (most recent first)
    approval_dates = [req.approval_date for req in results]
    assert approval_dates == sorted(approval_dates, reverse=True)


def test_get_approved_requests_filter_by_date_range(db_session: Session, sample_data):
    """Test filtering by date range."""
    # Filter for requests approved in the last 5 days
    date_from = datetime.utcnow() - timedelta(days=5)
    date_to = datetime.utcnow()

    results = get_approved_requests(
        db_session,
        date_from=date_from,
        date_to=date_to
    )

    # Should return only requests approved in the last 5 days
    assert len(results) == 1
    assert all(req.approval_date >= date_from for req in results)
    assert all(req.approval_date <= date_to for req in results)


def test_get_approved_requests_filter_by_taccount(db_session: Session, sample_data):
    """Test filtering by T-account."""
    taccount1 = sample_data["taccount1"]

    results = get_approved_requests(
        db_session,
        taccount_id=taccount1.id
    )

    # Should return only requests with taccount1
    assert len(results) == 2
    assert all(req.taccount_id == taccount1.id for req in results)


def test_get_approved_requests_filter_by_project(db_session: Session, sample_data):
    """Test filtering by project."""
    project1 = sample_data["project1"]

    results = get_approved_requests(
        db_session,
        project_id=project1.id
    )

    # Should return only requests for project1
    assert len(results) == 1
    assert all(req.project_id == project1.id for req in results)


def test_get_approved_requests_multiple_filters(db_session: Session, sample_data):
    """Test combining multiple filters."""
    taccount2 = sample_data["taccount2"]
    date_from = datetime.utcnow() - timedelta(days=20)
    date_to = datetime.utcnow()

    results = get_approved_requests(
        db_session,
        date_from=date_from,
        date_to=date_to,
        taccount_id=taccount2.id
    )

    # Should return only approved requests with taccount2 in date range
    assert len(results) == 1
    assert all(req.taccount_id == taccount2.id for req in results)
    assert all(req.approval_date >= date_from for req in results)


def test_get_approved_requests_filter_by_status(db_session: Session, sample_data):
    """Test filtering by different status."""
    # Get pending requests
    results = get_approved_requests(db_session, status="pending")

    assert len(results) == 1
    assert all(req.status == "pending" for req in results)

    # Get rejected requests
    results = get_approved_requests(db_session, status="rejected")

    assert len(results) == 1
    assert all(req.status == "rejected" for req in results)


def test_get_approved_requests_eager_loading(db_session: Session, sample_data):
    """Test that relationships are eager loaded (no N+1 queries)."""
    results = get_approved_requests(db_session)

    # Access relationships - should not trigger additional queries
    for req in results:
        assert req.requester is not None
        assert req.requester.full_name is not None
        assert req.taccount is not None
        assert req.taccount.account_code is not None
        if req.approver:
            assert req.approver.full_name is not None
        if req.project:
            assert req.project.name is not None


def test_export_to_csv_has_correct_headers(db_session: Session, sample_data):
    """Test that CSV export has correct headers."""
    requests = get_approved_requests(db_session)
    csv_content = export_to_csv(requests)

    lines = csv_content.strip().split("\n")
    headers = lines[0]

    expected_headers = [
        "Request ID",
        "Employee Name",
        "Department",
        "Request Type",
        "Project Name",
        "Destination",
        "Start Date",
        "End Date",
        "Purpose",
        "Estimated Cost",
        "T-Account",
        "Status",
        "Approved By",
        "Approval Date"
    ]

    for expected_header in expected_headers:
        assert expected_header in headers


def test_export_to_csv_has_correct_data(db_session: Session, sample_data):
    """Test that CSV export contains correct data."""
    requests = get_approved_requests(db_session)
    csv_content = export_to_csv(requests)

    lines = csv_content.strip().split("\n")

    # Should have header + 3 data rows
    assert len(lines) == 4

    # Check that first data row contains expected values
    first_row = lines[1]
    assert "Employee One" in first_row or "Employee Two" in first_row
    assert "Copenhagen" in first_row or "Stockholm" in first_row or "Berlin" in first_row


def test_export_to_csv_formats_data_correctly(db_session: Session, sample_data):
    """Test that CSV export formats data correctly."""
    requests = get_approved_requests(db_session, taccount_id=sample_data["taccount1"].id)
    csv_content = export_to_csv(requests)

    # Check for proper formatting
    assert "T-1234 - Marketing" in csv_content
    assert "5000.00" in csv_content or "8000.00" in csv_content
    assert "Manager User" in csv_content
    assert "Operations" in csv_content  # Capitalized request type


def test_export_to_csv_handles_operations_requests(db_session: Session, sample_data):
    """Test that CSV export correctly handles operations requests (no project)."""
    requests = get_approved_requests(db_session, taccount_id=sample_data["taccount1"].id)
    csv_content = export_to_csv(requests)

    # Operations requests should have "N/A" for project name
    lines = csv_content.strip().split("\n")
    for line in lines[1:]:  # Skip header
        if "Operations" in line:
            assert "N/A" in line  # Project name should be N/A


def test_export_to_csv_handles_project_requests(db_session: Session, sample_data):
    """Test that CSV export correctly handles project requests."""
    requests = get_approved_requests(db_session, project_id=sample_data["project1"].id)
    csv_content = export_to_csv(requests)

    # Project requests should have project name
    assert "Project Alpha" in csv_content


def test_get_summary_by_taccount(db_session: Session, sample_data):
    """Test summary aggregation by T-account."""
    date_from = datetime.utcnow() - timedelta(days=30)
    date_to = datetime.utcnow()

    summary = get_summary_by_taccount(db_session, date_from, date_to)

    # Should have two T-accounts in summary
    assert len(summary) == 2

    # Check T-account 1 (Marketing): 5000 + 8000 = 13000
    assert "T-1234 - Marketing" in summary
    assert summary["T-1234 - Marketing"] == 13000.00

    # Check T-account 2 (Engineering): 12000
    assert "T-5678 - Engineering" in summary
    assert summary["T-5678 - Engineering"] == 12000.00


def test_get_summary_by_taccount_date_filtering(db_session: Session, sample_data):
    """Test that summary respects date range filters."""
    # Only get last 5 days
    date_from = datetime.utcnow() - timedelta(days=5)
    date_to = datetime.utcnow()

    summary = get_summary_by_taccount(db_session, date_from, date_to)

    # Should only include requests approved in last 5 days
    # Only request1 was approved today (5000.00 from taccount1)
    assert len(summary) == 1
    assert "T-1234 - Marketing" in summary
    assert summary["T-1234 - Marketing"] == 5000.00


def test_get_summary_by_taccount_empty_result(db_session: Session, sample_data):
    """Test summary with date range that has no approved requests."""
    # Use a date range in the future
    date_from = datetime.utcnow() + timedelta(days=100)
    date_to = datetime.utcnow() + timedelta(days=200)

    summary = get_summary_by_taccount(db_session, date_from, date_to)

    # Should return empty dictionary
    assert len(summary) == 0


def test_export_to_csv_empty_list(db_session: Session):
    """Test CSV export with empty list."""
    csv_content = export_to_csv([])

    lines = csv_content.strip().split("\n")

    # Should have header only
    assert len(lines) == 1
    assert "Request ID" in lines[0]
