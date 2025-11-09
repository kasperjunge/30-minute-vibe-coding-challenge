"""Tests for audit logging functionality."""

from datetime import date

import pytest

from app.models.audit_log import AuditLog
from app.models.travel_request import TravelRequest
from app.services import audit_service


def test_approving_request_creates_audit_log_entry(
    client, db_session, sample_employee, sample_manager, sample_taccount
):
    """Test that approving a request creates an audit log entry."""
    from app.auth.session import session_manager

    # Create a travel request
    travel_request = TravelRequest(
        requester_id=sample_employee.id,
        approver_id=sample_manager.id,
        request_type="operations",
        destination="Berlin",
        start_date=date(2024, 12, 1),
        end_date=date(2024, 12, 5),
        purpose="Conference",
        estimated_cost=2000,
        taccount_id=sample_taccount.id,
        status="pending",
    )
    db_session.add(travel_request)
    db_session.commit()
    db_session.refresh(travel_request)

    # Create manager session
    manager_session_token = session_manager.create_session(sample_manager.id)
    manager_cookies = {"travel_approval_session": manager_session_token}

    # Approve the request
    response = client.post(
        f"/requests/{travel_request.id}/approve",
        data={"comments": "Approved for business purposes"},
        cookies=manager_cookies,
        follow_redirects=False,
    )

    assert response.status_code == 303

    # Check that an audit log entry was created
    audit_logs = db_session.query(AuditLog).filter(
        AuditLog.entity_type == "travel_request",
        AuditLog.entity_id == travel_request.id,
        AuditLog.action == "approve",
    ).all()

    assert len(audit_logs) == 1
    audit_log = audit_logs[0]
    assert audit_log.user_id == sample_manager.id
    assert audit_log.entity_type == "travel_request"
    assert audit_log.entity_id == travel_request.id
    assert audit_log.action == "approve"
    assert audit_log.details is not None
    assert audit_log.details["request_id"] == travel_request.id


def test_rejecting_request_creates_audit_log_entry(
    client, db_session, sample_employee, sample_manager, sample_taccount
):
    """Test that rejecting a request creates an audit log entry."""
    from app.auth.session import session_manager

    # Create a travel request
    travel_request = TravelRequest(
        requester_id=sample_employee.id,
        approver_id=sample_manager.id,
        request_type="operations",
        destination="Paris",
        start_date=date(2024, 11, 1),
        end_date=date(2024, 11, 5),
        purpose="Training",
        estimated_cost=1500,
        taccount_id=sample_taccount.id,
        status="pending",
    )
    db_session.add(travel_request)
    db_session.commit()
    db_session.refresh(travel_request)

    # Create manager session
    manager_session_token = session_manager.create_session(sample_manager.id)
    manager_cookies = {"travel_approval_session": manager_session_token}

    # Reject the request
    response = client.post(
        f"/requests/{travel_request.id}/reject",
        data={"reason": "Budget constraints"},
        cookies=manager_cookies,
        follow_redirects=False,
    )

    assert response.status_code == 303

    # Check that an audit log entry was created
    audit_logs = db_session.query(AuditLog).filter(
        AuditLog.entity_type == "travel_request",
        AuditLog.entity_id == travel_request.id,
        AuditLog.action == "reject",
    ).all()

    assert len(audit_logs) == 1
    audit_log = audit_logs[0]
    assert audit_log.user_id == sample_manager.id
    assert audit_log.entity_type == "travel_request"
    assert audit_log.entity_id == travel_request.id
    assert audit_log.action == "reject"
    assert audit_log.details is not None
    assert audit_log.details["rejection_reason"] == "Budget constraints"


def test_creating_project_creates_audit_log_entry(
    client, db_session, sample_admin, sample_manager, admin_user_session
):
    """Test that creating a project creates an audit log entry."""
    # Create a new project
    response = client.post(
        "/admin/projects",
        data={
            "name": "New Test Project",
            "description": "A test project for audit logging",
            "team_lead_id": sample_manager.id,
        },
        cookies=admin_user_session,
        follow_redirects=False,
    )

    assert response.status_code == 303

    # Check that an audit log entry was created
    audit_logs = db_session.query(AuditLog).filter(
        AuditLog.action == "create_project",
    ).all()

    assert len(audit_logs) >= 1
    audit_log = audit_logs[0]
    assert audit_log.user_id == sample_admin.id
    assert audit_log.entity_type == "project"
    assert audit_log.action == "create_project"
    assert audit_log.details is not None
    assert audit_log.details["project_name"] == "New Test Project"


def test_updating_project_creates_audit_log_entry(
    client, db_session, sample_admin, sample_manager, sample_project, admin_user_session
):
    """Test that updating a project creates an audit log entry."""
    # Update the existing project
    response = client.post(
        f"/admin/projects/{sample_project.id}",
        data={
            "name": "Updated Project Name",
            "description": "Updated description",
            "team_lead_id": sample_manager.id,
        },
        cookies=admin_user_session,
        follow_redirects=False,
    )

    assert response.status_code == 303

    # Check that an audit log entry was created
    audit_logs = db_session.query(AuditLog).filter(
        AuditLog.entity_type == "project",
        AuditLog.entity_id == sample_project.id,
        AuditLog.action == "update_project",
    ).all()

    assert len(audit_logs) == 1
    audit_log = audit_logs[0]
    assert audit_log.user_id == sample_admin.id
    assert audit_log.entity_type == "project"
    assert audit_log.entity_id == sample_project.id
    assert audit_log.action == "update_project"
    assert audit_log.details is not None
    assert audit_log.details["project_name"] == "Updated Project Name"


def test_audit_logs_contain_correct_user_and_entity_info(
    db_session, sample_employee, sample_manager, sample_taccount
):
    """Test that audit logs contain correct user and entity information."""
    from app.models.travel_request import TravelRequest

    # Create a travel request
    travel_request = TravelRequest(
        requester_id=sample_employee.id,
        approver_id=sample_manager.id,
        request_type="operations",
        destination="Copenhagen",
        start_date=date(2024, 10, 1),
        end_date=date(2024, 10, 5),
        purpose="Client meeting",
        estimated_cost=1800,
        taccount_id=sample_taccount.id,
        status="pending",
    )
    db_session.add(travel_request)
    db_session.commit()
    db_session.refresh(travel_request)

    # Log an approval action directly
    audit_log = audit_service.log_action(
        user_id=sample_manager.id,
        action="approve",
        entity_type="travel_request",
        entity_id=travel_request.id,
        details={
            "request_id": travel_request.id,
            "requester_id": sample_employee.id,
            "destination": travel_request.destination,
        },
        db=db_session,
    )

    # Verify the audit log has correct information
    assert audit_log.user_id == sample_manager.id
    assert audit_log.action == "approve"
    assert audit_log.entity_type == "travel_request"
    assert audit_log.entity_id == travel_request.id
    assert audit_log.details["requester_id"] == sample_employee.id
    assert audit_log.details["destination"] == "Copenhagen"
    assert audit_log.timestamp is not None

    # Verify relationship works
    assert audit_log.user.id == sample_manager.id
    assert audit_log.user.full_name == sample_manager.full_name


def test_audit_service_get_logs_for_entity(
    db_session, sample_employee, sample_manager, sample_taccount
):
    """Test retrieving audit logs for a specific entity."""
    from app.models.travel_request import TravelRequest

    # Create a travel request
    travel_request = TravelRequest(
        requester_id=sample_employee.id,
        approver_id=sample_manager.id,
        request_type="operations",
        destination="Stockholm",
        start_date=date(2024, 9, 1),
        end_date=date(2024, 9, 5),
        purpose="Workshop",
        estimated_cost=1200,
        taccount_id=sample_taccount.id,
        status="pending",
    )
    db_session.add(travel_request)
    db_session.commit()
    db_session.refresh(travel_request)

    # Create multiple audit log entries
    audit_service.log_action(
        user_id=sample_manager.id,
        action="approve",
        entity_type="travel_request",
        entity_id=travel_request.id,
        details={"action": "first"},
        db=db_session,
    )

    audit_service.log_action(
        user_id=sample_manager.id,
        action="update",
        entity_type="travel_request",
        entity_id=travel_request.id,
        details={"action": "second"},
        db=db_session,
    )

    # Retrieve logs for the entity
    logs = audit_service.get_audit_logs_for_entity(
        entity_type="travel_request",
        entity_id=travel_request.id,
        db=db_session,
    )

    assert len(logs) == 2
    assert logs[0].entity_id == travel_request.id
    assert logs[1].entity_id == travel_request.id


def test_audit_service_get_logs_by_user(
    db_session, sample_employee, sample_manager, sample_taccount
):
    """Test retrieving audit logs by user."""
    # Create some audit logs for the manager
    audit_service.log_action(
        user_id=sample_manager.id,
        action="approve",
        entity_type="travel_request",
        entity_id=1,
        details={},
        db=db_session,
    )

    audit_service.log_action(
        user_id=sample_manager.id,
        action="reject",
        entity_type="travel_request",
        entity_id=2,
        details={},
        db=db_session,
    )

    # Retrieve logs for the manager
    logs = audit_service.get_audit_logs_by_user(
        user_id=sample_manager.id,
        db=db_session,
    )

    assert len(logs) >= 2
    for log in logs:
        assert log.user_id == sample_manager.id
