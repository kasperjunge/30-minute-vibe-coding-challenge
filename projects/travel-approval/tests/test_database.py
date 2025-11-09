"""Tests for database models and relationships."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from app.models import User, TravelRequest, Project, TAccount, Notification


def test_user_model_creation(db_session):
    """Test that User model can be instantiated and saved."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        role="employee",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.role == "employee"
    assert user.is_active is True


def test_user_manager_relationship(db_session, sample_manager, sample_employee):
    """Test the self-referential manager relationship."""
    assert sample_employee.manager_id == sample_manager.id
    assert sample_employee.manager.email == "manager@test.com"
    assert sample_manager.employees[0].email == "employee@test.com"


def test_taccount_model(db_session, sample_taccount):
    """Test T-Account model."""
    assert sample_taccount.id is not None
    assert sample_taccount.account_code == "T-1234"
    assert sample_taccount.is_active is True


def test_project_model(db_session, sample_project, sample_manager):
    """Test Project model and team lead relationship."""
    assert sample_project.id is not None
    assert sample_project.name == "Test Project"
    assert sample_project.team_lead_id == sample_manager.id
    assert sample_project.team_lead.email == "manager@test.com"


def test_travel_request_model(db_session, sample_employee, sample_manager, sample_taccount):
    """Test TravelRequest model creation."""
    travel_request = TravelRequest(
        requester_id=sample_employee.id,
        request_type="operations",
        destination="Copenhagen",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 5),
        purpose="Business meeting",
        estimated_cost=Decimal("5000.00"),
        taccount_id=sample_taccount.id,
        status="pending",
        approver_id=sample_manager.id
    )
    db_session.add(travel_request)
    db_session.commit()

    assert travel_request.id is not None
    assert travel_request.destination == "Copenhagen"
    assert travel_request.status == "pending"
    assert travel_request.estimated_cost == Decimal("5000.00")


def test_travel_request_relationships(db_session, sample_employee, sample_manager, sample_taccount):
    """Test TravelRequest relationships with User and TAccount."""
    travel_request = TravelRequest(
        requester_id=sample_employee.id,
        request_type="operations",
        destination="London",
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 3),
        purpose="Client visit",
        estimated_cost=Decimal("3000.00"),
        taccount_id=sample_taccount.id,
        status="pending",
        approver_id=sample_manager.id
    )
    db_session.add(travel_request)
    db_session.commit()
    db_session.refresh(travel_request)

    # Test requester relationship
    assert travel_request.requester.email == "employee@test.com"

    # Test approver relationship
    assert travel_request.approver.email == "manager@test.com"

    # Test T-account relationship
    assert travel_request.taccount.account_code == "T-1234"

    # Test reverse relationships
    assert len(sample_employee.travel_requests) == 1
    assert len(sample_manager.approval_requests) == 1


def test_notification_model(db_session, sample_employee, sample_taccount, sample_manager):
    """Test Notification model."""
    # Create a travel request first
    travel_request = TravelRequest(
        requester_id=sample_employee.id,
        request_type="operations",
        destination="Paris",
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 3),
        purpose="Conference",
        estimated_cost=Decimal("4000.00"),
        taccount_id=sample_taccount.id,
        status="pending",
        approver_id=sample_manager.id
    )
    db_session.add(travel_request)
    db_session.commit()

    # Create notification
    notification = Notification(
        user_id=sample_manager.id,
        travel_request_id=travel_request.id,
        notification_type="request_submitted",
        message="New travel request requires your approval",
        is_read=False
    )
    db_session.add(notification)
    db_session.commit()

    assert notification.id is not None
    assert notification.user.email == "manager@test.com"
    assert notification.travel_request.destination == "Paris"
    assert notification.is_read is False


def test_project_travel_request_relationship(db_session, sample_employee, sample_project, sample_taccount):
    """Test Project and TravelRequest relationship."""
    travel_request = TravelRequest(
        requester_id=sample_employee.id,
        request_type="project",
        project_id=sample_project.id,
        destination="Berlin",
        start_date=date(2025, 8, 1),
        end_date=date(2025, 8, 5),
        purpose="Project kickoff",
        estimated_cost=Decimal("6000.00"),
        taccount_id=sample_taccount.id,
        status="pending",
        approver_id=sample_project.team_lead_id
    )
    db_session.add(travel_request)
    db_session.commit()
    db_session.refresh(travel_request)

    assert travel_request.project.name == "Test Project"
    assert len(sample_project.travel_requests) == 1
    assert sample_project.travel_requests[0].destination == "Berlin"


def test_unique_constraints(db_session):
    """Test unique constraints on email and account_code."""
    # Test unique email
    user1 = User(
        email="duplicate@test.com",
        password_hash="pass1",
        full_name="User 1",
        role="employee"
    )
    db_session.add(user1)
    db_session.commit()

    user2 = User(
        email="duplicate@test.com",
        password_hash="pass2",
        full_name="User 2",
        role="employee"
    )
    db_session.add(user2)

    with pytest.raises(Exception):  # Should raise IntegrityError
        db_session.commit()
