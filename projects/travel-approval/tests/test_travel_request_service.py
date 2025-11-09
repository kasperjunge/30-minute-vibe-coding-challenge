"""Tests for Travel Request Service."""

from datetime import date, datetime
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.models.project import Project
from app.models.taccount import TAccount
from app.models.travel_request import TravelRequest
from app.models.user import User
from app.schemas.travel_request import TravelRequestCreate
from app.services.travel_request_service import (
    approve_request,
    create_request,
    determine_approver,
    get_pending_requests_for_approver,
    reject_request,
)


class TestDetermineApprover:
    """Tests for determine_approver function."""

    def test_operations_request_routes_to_manager(self, db_session, sample_employee, sample_manager):
        """Test that operations requests route to the employee's manager."""
        # Create a travel request (operations type)
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Copenhagen",
            start_date=date(2025, 6, 15),
            end_date=date(2025, 6, 17),
            purpose="Client meeting",
            estimated_cost=Decimal("5000.00"),
            taccount_id=1,
            status="pending"
        )
        travel_request.requester = sample_employee

        # Determine approver
        approver = determine_approver(travel_request, db_session)

        # Assert the approver is the employee's manager
        assert approver.id == sample_manager.id
        assert approver.email == "manager@test.com"

    def test_project_request_routes_to_team_lead(self, db_session, sample_employee, sample_project):
        """Test that project requests route to the project's team lead."""
        # Create a travel request (project type)
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="project",
            project_id=sample_project.id,
            destination="Stockholm",
            start_date=date(2025, 7, 1),
            end_date=date(2025, 7, 3),
            purpose="Project kickoff",
            estimated_cost=Decimal("7500.00"),
            taccount_id=1,
            status="pending"
        )
        travel_request.requester = sample_employee
        travel_request.project = sample_project

        # Determine approver
        approver = determine_approver(travel_request, db_session)

        # Assert the approver is the project's team lead
        assert approver.id == sample_project.team_lead_id
        assert approver.email == "manager@test.com"  # In fixtures, manager is team lead

    def test_error_when_manager_id_is_null(self, db_session):
        """Test that an error is raised when employee has no manager assigned."""
        # Create employee without manager
        employee = User(
            email="no_manager@test.com",
            password_hash="hashed_password",
            full_name="Employee No Manager",
            role="employee",
            manager_id=None,  # No manager assigned
            is_active=True
        )
        db_session.add(employee)
        db_session.commit()

        # Create travel request
        travel_request = TravelRequest(
            requester_id=employee.id,
            request_type="operations",
            destination="Oslo",
            start_date=date(2025, 8, 1),
            end_date=date(2025, 8, 3),
            purpose="Conference",
            estimated_cost=Decimal("6000.00"),
            taccount_id=1,
            status="pending"
        )
        travel_request.requester = employee

        # Attempt to determine approver should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            determine_approver(travel_request, db_session)

        assert exc_info.value.status_code == 400
        assert "no manager assigned" in exc_info.value.detail.lower()

    def test_error_when_project_team_lead_not_found(self, db_session, sample_employee, sample_manager):
        """Test that an error is raised when project's team lead doesn't exist in the system."""
        # Create a project with a valid team lead
        project = Project(
            name="Project Test Lead",
            description="Test project",
            team_lead_id=sample_manager.id,
            is_active=True
        )
        db_session.add(project)
        db_session.commit()

        # Create travel request
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="project",
            project_id=project.id,
            destination="Berlin",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 3),
            purpose="Project work",
            estimated_cost=Decimal("8000.00"),
            taccount_id=1,
            status="pending"
        )
        travel_request.requester = sample_employee
        travel_request.project = project

        # Manually set the team_lead_id to a non-existent user ID
        project.team_lead_id = 99999  # This ID doesn't exist

        # Now attempting to determine approver should fail because team lead doesn't exist
        with pytest.raises(HTTPException) as exc_info:
            determine_approver(travel_request, db_session)

        assert exc_info.value.status_code == 400
        assert "team lead not found" in exc_info.value.detail.lower()


class TestCreateRequest:
    """Tests for create_request function."""

    def test_create_operations_request(self, db_session, sample_employee, sample_manager, sample_taccount):
        """Test creating an operations travel request."""
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Paris",
            start_date=date(2025, 10, 1),
            end_date=date(2025, 10, 5),
            purpose="Sales meeting with French clients",
            estimated_cost=Decimal("12000.00"),
            taccount_id=sample_taccount.id
        )

        travel_request = create_request(request_data, sample_employee, db_session)

        # Verify request was created correctly
        assert travel_request.id is not None
        assert travel_request.requester_id == sample_employee.id
        assert travel_request.request_type == "operations"
        assert travel_request.destination == "Paris"
        assert travel_request.status == "pending"
        assert travel_request.approver_id == sample_manager.id

    def test_create_project_request(self, db_session, sample_employee, sample_project, sample_taccount):
        """Test creating a project travel request."""
        request_data = TravelRequestCreate(
            request_type="project",
            project_id=sample_project.id,
            destination="Amsterdam",
            start_date=date(2025, 11, 10),
            end_date=date(2025, 11, 12),
            purpose="Project workshop",
            estimated_cost=Decimal("9500.00"),
            taccount_id=sample_taccount.id
        )

        travel_request = create_request(request_data, sample_employee, db_session)

        # Verify request was created correctly
        assert travel_request.id is not None
        assert travel_request.requester_id == sample_employee.id
        assert travel_request.request_type == "project"
        assert travel_request.project_id == sample_project.id
        assert travel_request.destination == "Amsterdam"
        assert travel_request.status == "pending"
        assert travel_request.approver_id == sample_project.team_lead_id

    def test_create_request_fails_without_manager(self, db_session, sample_taccount):
        """Test that creating request fails when employee has no manager."""
        # Create employee without manager
        employee = User(
            email="orphan@test.com",
            password_hash="hashed_password",
            full_name="Orphan Employee",
            role="employee",
            manager_id=None,
            is_active=True
        )
        db_session.add(employee)
        db_session.commit()

        request_data = TravelRequestCreate(
            request_type="operations",
            destination="London",
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 3),
            purpose="Training",
            estimated_cost=Decimal("8000.00"),
            taccount_id=sample_taccount.id
        )

        with pytest.raises(HTTPException) as exc_info:
            create_request(request_data, employee, db_session)

        assert exc_info.value.status_code == 400


class TestGetPendingRequestsForApprover:
    """Tests for get_pending_requests_for_approver function."""

    def test_manager_sees_pending_operations_requests(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that manager sees pending operations requests from their employees."""
        # Create pending operations request
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Rome",
            start_date=date(2025, 6, 20),
            end_date=date(2025, 6, 22),
            purpose="Client visit",
            estimated_cost=Decimal("10000.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)

        # Get pending requests for manager
        pending_requests = get_pending_requests_for_approver(sample_manager, db_session)

        assert len(pending_requests) == 1
        assert pending_requests[0].id == travel_request.id
        assert pending_requests[0].status == "pending"

    def test_team_lead_sees_pending_project_requests(
        self, db_session, sample_employee, sample_manager, sample_project, sample_taccount
    ):
        """Test that team lead sees pending project requests."""
        # Create pending project request
        request_data = TravelRequestCreate(
            request_type="project",
            project_id=sample_project.id,
            destination="Brussels",
            start_date=date(2025, 7, 10),
            end_date=date(2025, 7, 12),
            purpose="Project meeting",
            estimated_cost=Decimal("7000.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)

        # Get pending requests for team lead (sample_manager is team lead in fixtures)
        pending_requests = get_pending_requests_for_approver(sample_manager, db_session)

        assert len(pending_requests) == 1
        assert pending_requests[0].id == travel_request.id
        assert pending_requests[0].request_type == "project"

    def test_approved_requests_not_returned(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that approved requests are not returned in pending list."""
        # Create and approve a request
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Vienna",
            start_date=date(2025, 8, 5),
            end_date=date(2025, 8, 7),
            purpose="Conference",
            estimated_cost=Decimal("9000.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)
        approve_request(travel_request.id, sample_manager, "Approved", db_session)

        # Get pending requests - should be empty
        pending_requests = get_pending_requests_for_approver(sample_manager, db_session)

        assert len(pending_requests) == 0


class TestApproveRequest:
    """Tests for approve_request function."""

    def test_approve_updates_status_and_records_date(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that approving a request updates status and records approval date."""
        # Create pending request
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Madrid",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 3),
            purpose="Business development",
            estimated_cost=Decimal("11000.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)

        # Approve the request
        comments = "Approved for strategic business development"
        approved_request = approve_request(travel_request.id, sample_manager, comments, db_session)

        # Verify status updated
        assert approved_request.status == "approved"
        assert approved_request.approval_date is not None
        assert isinstance(approved_request.approval_date, datetime)
        assert approved_request.approval_comments == comments
        assert approved_request.rejection_reason is None

    def test_approve_with_null_comments(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that approving without comments is allowed."""
        # Create pending request
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Lisbon",
            start_date=date(2025, 10, 5),
            end_date=date(2025, 10, 7),
            purpose="Partner meeting",
            estimated_cost=Decimal("8500.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)

        # Approve without comments
        approved_request = approve_request(travel_request.id, sample_manager, None, db_session)

        assert approved_request.status == "approved"
        assert approved_request.approval_comments is None

    def test_approver_must_be_designated_approver(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that only the designated approver can approve a request."""
        # Create another user who is not the approver
        other_user = User(
            email="other@test.com",
            password_hash="hashed_password",
            full_name="Other User",
            role="manager",
            is_active=True
        )
        db_session.add(other_user)
        db_session.commit()

        # Create pending request (will be assigned to sample_manager)
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Athens",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 3),
            purpose="Trade show",
            estimated_cost=Decimal("9500.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)

        # Attempt to approve as other_user (not the designated approver)
        with pytest.raises(HTTPException) as exc_info:
            approve_request(travel_request.id, other_user, "Trying to approve", db_session)

        assert exc_info.value.status_code == 403
        assert "not the designated approver" in exc_info.value.detail.lower()

    def test_cannot_approve_already_approved_request(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that already approved requests cannot be approved again."""
        # Create and approve request
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Dublin",
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 3),
            purpose="Client meeting",
            estimated_cost=Decimal("7500.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)
        approve_request(travel_request.id, sample_manager, "First approval", db_session)

        # Attempt to approve again
        with pytest.raises(HTTPException) as exc_info:
            approve_request(travel_request.id, sample_manager, "Second approval", db_session)

        assert exc_info.value.status_code == 400
        assert "already approved" in exc_info.value.detail.lower()

    def test_cannot_approve_rejected_request(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that rejected requests cannot be approved."""
        # Create and reject request
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Helsinki",
            start_date=date(2026, 1, 10),
            end_date=date(2026, 1, 12),
            purpose="Workshop",
            estimated_cost=Decimal("8000.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)
        reject_request(travel_request.id, sample_manager, "Budget constraints", db_session)

        # Attempt to approve
        with pytest.raises(HTTPException) as exc_info:
            approve_request(travel_request.id, sample_manager, "Trying to approve", db_session)

        assert exc_info.value.status_code == 400
        assert "already rejected" in exc_info.value.detail.lower()


class TestRejectRequest:
    """Tests for reject_request function."""

    def test_reject_requires_reason(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that rejecting a request requires a non-empty reason."""
        # Create pending request
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Warsaw",
            start_date=date(2025, 6, 15),
            end_date=date(2025, 6, 17),
            purpose="Training",
            estimated_cost=Decimal("6500.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)

        # Attempt to reject with empty reason
        with pytest.raises(HTTPException) as exc_info:
            reject_request(travel_request.id, sample_manager, "", db_session)

        assert exc_info.value.status_code == 400
        assert "reason is required" in exc_info.value.detail.lower()

        # Also test with whitespace-only reason
        with pytest.raises(HTTPException) as exc_info:
            reject_request(travel_request.id, sample_manager, "   ", db_session)

        assert exc_info.value.status_code == 400

    def test_reject_updates_status_and_records_reason(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that rejecting a request updates status and records reason."""
        # Create pending request
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Prague",
            start_date=date(2025, 7, 20),
            end_date=date(2025, 7, 22),
            purpose="Conference",
            estimated_cost=Decimal("7800.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)

        # Reject the request
        reason = "Travel budget exhausted for Q3"
        rejected_request = reject_request(travel_request.id, sample_manager, reason, db_session)

        # Verify status updated
        assert rejected_request.status == "rejected"
        assert rejected_request.approval_date is not None
        assert isinstance(rejected_request.approval_date, datetime)
        assert rejected_request.rejection_reason == reason
        assert rejected_request.approval_comments is None

    def test_reject_approver_must_be_designated_approver(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that only the designated approver can reject a request."""
        # Create another user who is not the approver
        other_user = User(
            email="unauthorized@test.com",
            password_hash="hashed_password",
            full_name="Unauthorized User",
            role="manager",
            is_active=True
        )
        db_session.add(other_user)
        db_session.commit()

        # Create pending request
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Budapest",
            start_date=date(2025, 8, 10),
            end_date=date(2025, 8, 12),
            purpose="Vendor meeting",
            estimated_cost=Decimal("6800.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)

        # Attempt to reject as other_user
        with pytest.raises(HTTPException) as exc_info:
            reject_request(travel_request.id, other_user, "Not authorized", db_session)

        assert exc_info.value.status_code == 403
        assert "not the designated approver" in exc_info.value.detail.lower()

    def test_cannot_reject_already_rejected_request(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that already rejected requests cannot be rejected again."""
        # Create and reject request
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Oslo",
            start_date=date(2025, 9, 5),
            end_date=date(2025, 9, 7),
            purpose="Summit",
            estimated_cost=Decimal("9200.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)
        reject_request(travel_request.id, sample_manager, "First rejection", db_session)

        # Attempt to reject again
        with pytest.raises(HTTPException) as exc_info:
            reject_request(travel_request.id, sample_manager, "Second rejection", db_session)

        assert exc_info.value.status_code == 400
        assert "already rejected" in exc_info.value.detail.lower()

    def test_cannot_reject_approved_request(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that approved requests cannot be rejected."""
        # Create and approve request
        request_data = TravelRequestCreate(
            request_type="operations",
            destination="Zurich",
            start_date=date(2025, 10, 15),
            end_date=date(2025, 10, 17),
            purpose="Banking conference",
            estimated_cost=Decimal("13000.00"),
            taccount_id=sample_taccount.id
        )
        travel_request = create_request(request_data, sample_employee, db_session)
        approve_request(travel_request.id, sample_manager, "Approved", db_session)

        # Attempt to reject
        with pytest.raises(HTTPException) as exc_info:
            reject_request(travel_request.id, sample_manager, "Trying to reject", db_session)

        assert exc_info.value.status_code == 400
        assert "already approved" in exc_info.value.detail.lower()
