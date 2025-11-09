"""Tests for Notification Service."""

from datetime import date
from decimal import Decimal

import pytest

from app.models.notification import Notification
from app.models.travel_request import TravelRequest
from app.models.user import User
from app.services.notification_service import (
    get_unread_notifications,
    mark_notification_read,
    notify_request_approved,
    notify_request_rejected,
    notify_request_submitted,
)


class TestNotifyRequestSubmitted:
    """Tests for notify_request_submitted function."""

    def test_creates_notification_for_approver(self, db_session, sample_employee, sample_manager, sample_taccount):
        """Test that submitting a request creates a notification for the approver."""
        # Create a travel request
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Paris",
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 5),
            purpose="Client meeting",
            estimated_cost=Decimal("5000.00"),
            taccount_id=sample_taccount.id,
            approver_id=sample_manager.id,
            status="pending"
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        # Call notify_request_submitted
        notify_request_submitted(travel_request, db_session)

        # Verify notification was created
        notifications = db_session.query(Notification).filter(
            Notification.user_id == sample_manager.id
        ).all()

        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.travel_request_id == travel_request.id
        assert notification.notification_type == "request_submitted"
        assert f"New travel request #{travel_request.id}" in notification.message
        assert sample_employee.full_name in notification.message
        assert notification.is_read is False

    def test_message_includes_request_id_and_requester_name(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that notification message includes request ID and requester name."""
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Berlin",
            start_date=date(2025, 7, 10),
            end_date=date(2025, 7, 12),
            purpose="Conference",
            estimated_cost=Decimal("3000.00"),
            taccount_id=sample_taccount.id,
            approver_id=sample_manager.id,
            status="pending"
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        notify_request_submitted(travel_request, db_session)

        notification = db_session.query(Notification).filter(
            Notification.user_id == sample_manager.id
        ).first()

        expected_message = f"New travel request #{travel_request.id} from {sample_employee.full_name} requires your approval"
        assert notification.message == expected_message


class TestNotifyRequestApproved:
    """Tests for notify_request_approved function."""

    def test_creates_notification_for_employee(self, db_session, sample_employee, sample_manager, sample_taccount):
        """Test that approving a request creates a notification for the employee."""
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="London",
            start_date=date(2025, 8, 1),
            end_date=date(2025, 8, 3),
            purpose="Training",
            estimated_cost=Decimal("4000.00"),
            taccount_id=sample_taccount.id,
            approver_id=sample_manager.id,
            status="approved"
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        notify_request_approved(travel_request, db_session)

        # Check employee notification
        employee_notifications = db_session.query(Notification).filter(
            Notification.user_id == sample_employee.id
        ).all()

        assert len(employee_notifications) == 1
        notification = employee_notifications[0]
        assert notification.travel_request_id == travel_request.id
        assert notification.notification_type == "request_approved"
        assert f"Your travel request #{travel_request.id} has been approved" in notification.message
        assert sample_manager.full_name in notification.message
        assert notification.is_read is False

    def test_creates_notifications_for_accounting_staff(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that approving a request creates notifications for all accounting staff."""
        # Create accounting staff
        accountant1 = User(
            email="accountant1@test.com",
            password_hash="hashed_password",
            full_name="Accountant One",
            role="accounting",
            is_active=True
        )
        accountant2 = User(
            email="accountant2@test.com",
            password_hash="hashed_password",
            full_name="Accountant Two",
            role="accounting",
            is_active=True
        )
        db_session.add(accountant1)
        db_session.add(accountant2)
        db_session.commit()

        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Amsterdam",
            start_date=date(2025, 9, 5),
            end_date=date(2025, 9, 7),
            purpose="Workshop",
            estimated_cost=Decimal("3500.00"),
            taccount_id=sample_taccount.id,
            approver_id=sample_manager.id,
            status="approved"
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        notify_request_approved(travel_request, db_session)

        # Check accounting notifications
        accounting_notifications = db_session.query(Notification).filter(
            Notification.user_id.in_([accountant1.id, accountant2.id])
        ).all()

        assert len(accounting_notifications) == 2
        for notification in accounting_notifications:
            assert notification.travel_request_id == travel_request.id
            assert notification.notification_type == "request_approved"
            assert f"Travel request #{travel_request.id} has been approved" in notification.message
            assert "requires processing" in notification.message
            assert notification.is_read is False

    def test_inactive_accounting_staff_not_notified(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that inactive accounting staff do not receive notifications."""
        # Create active and inactive accounting staff
        active_accountant = User(
            email="active@test.com",
            password_hash="hashed_password",
            full_name="Active Accountant",
            role="accounting",
            is_active=True
        )
        inactive_accountant = User(
            email="inactive@test.com",
            password_hash="hashed_password",
            full_name="Inactive Accountant",
            role="accounting",
            is_active=False
        )
        db_session.add(active_accountant)
        db_session.add(inactive_accountant)
        db_session.commit()

        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Madrid",
            start_date=date(2025, 10, 1),
            end_date=date(2025, 10, 3),
            purpose="Sales",
            estimated_cost=Decimal("4500.00"),
            taccount_id=sample_taccount.id,
            approver_id=sample_manager.id,
            status="approved"
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        notify_request_approved(travel_request, db_session)

        # Check that only active accountant received notification
        active_notifications = db_session.query(Notification).filter(
            Notification.user_id == active_accountant.id
        ).all()
        inactive_notifications = db_session.query(Notification).filter(
            Notification.user_id == inactive_accountant.id
        ).all()

        assert len(active_notifications) == 1
        assert len(inactive_notifications) == 0


class TestNotifyRequestRejected:
    """Tests for notify_request_rejected function."""

    def test_creates_notification_for_employee(self, db_session, sample_employee, sample_manager, sample_taccount):
        """Test that rejecting a request creates a notification for the employee."""
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Rome",
            start_date=date(2025, 11, 10),
            end_date=date(2025, 11, 12),
            purpose="Meeting",
            estimated_cost=Decimal("5500.00"),
            taccount_id=sample_taccount.id,
            approver_id=sample_manager.id,
            status="rejected",
            rejection_reason="Budget constraints"
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        notify_request_rejected(travel_request, db_session)

        # Check employee notification
        notifications = db_session.query(Notification).filter(
            Notification.user_id == sample_employee.id
        ).all()

        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.travel_request_id == travel_request.id
        assert notification.notification_type == "request_rejected"
        assert f"Your travel request #{travel_request.id} has been rejected" in notification.message
        assert "Budget constraints" in notification.message
        assert notification.is_read is False

    def test_notification_includes_rejection_reason(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that rejection notification includes the rejection reason."""
        rejection_reason = "Travel not essential to business objectives"
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Vienna",
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 3),
            purpose="Optional conference",
            estimated_cost=Decimal("6000.00"),
            taccount_id=sample_taccount.id,
            approver_id=sample_manager.id,
            status="rejected",
            rejection_reason=rejection_reason
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        notify_request_rejected(travel_request, db_session)

        notification = db_session.query(Notification).filter(
            Notification.user_id == sample_employee.id
        ).first()

        expected_message = f"Your travel request #{travel_request.id} has been rejected: {rejection_reason}"
        assert notification.message == expected_message


class TestGetUnreadNotifications:
    """Tests for get_unread_notifications function."""

    def test_returns_only_unread_notifications(self, db_session, sample_employee, sample_taccount):
        """Test that only unread notifications are returned."""
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Dublin",
            start_date=date(2026, 1, 10),
            end_date=date(2026, 1, 12),
            purpose="Visit",
            estimated_cost=Decimal("4000.00"),
            taccount_id=sample_taccount.id,
            status="pending"
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        # Create unread notification
        unread_notification = Notification(
            user_id=sample_employee.id,
            travel_request_id=travel_request.id,
            notification_type="request_approved",
            message="Unread notification",
            is_read=False
        )

        # Create read notification
        read_notification = Notification(
            user_id=sample_employee.id,
            travel_request_id=travel_request.id,
            notification_type="request_approved",
            message="Read notification",
            is_read=True
        )

        db_session.add(unread_notification)
        db_session.add(read_notification)
        db_session.commit()

        # Get unread notifications
        unread = get_unread_notifications(sample_employee, db_session)

        assert len(unread) == 1
        assert unread[0].id == unread_notification.id
        assert unread[0].is_read is False

    def test_returns_only_user_notifications(self, db_session, sample_employee, sample_manager, sample_taccount):
        """Test that only the specified user's notifications are returned."""
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Brussels",
            start_date=date(2026, 2, 5),
            end_date=date(2026, 2, 7),
            purpose="Meeting",
            estimated_cost=Decimal("3000.00"),
            taccount_id=sample_taccount.id,
            status="pending"
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        # Create notification for employee
        employee_notification = Notification(
            user_id=sample_employee.id,
            travel_request_id=travel_request.id,
            notification_type="request_approved",
            message="Employee notification",
            is_read=False
        )

        # Create notification for manager
        manager_notification = Notification(
            user_id=sample_manager.id,
            travel_request_id=travel_request.id,
            notification_type="request_submitted",
            message="Manager notification",
            is_read=False
        )

        db_session.add(employee_notification)
        db_session.add(manager_notification)
        db_session.commit()

        # Get employee's unread notifications
        employee_unread = get_unread_notifications(sample_employee, db_session)

        assert len(employee_unread) == 1
        assert employee_unread[0].user_id == sample_employee.id
        assert employee_unread[0].message == "Employee notification"

    def test_returns_empty_list_when_no_unread(self, db_session, sample_employee):
        """Test that empty list is returned when there are no unread notifications."""
        unread = get_unread_notifications(sample_employee, db_session)
        assert len(unread) == 0


class TestMarkNotificationRead:
    """Tests for mark_notification_read function."""

    def test_marks_notification_as_read(self, db_session, sample_employee, sample_taccount):
        """Test that mark_notification_read updates the is_read flag."""
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Lisbon",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 3),
            purpose="Conference",
            estimated_cost=Decimal("5000.00"),
            taccount_id=sample_taccount.id,
            status="pending"
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        notification = Notification(
            user_id=sample_employee.id,
            travel_request_id=travel_request.id,
            notification_type="request_approved",
            message="Test notification",
            is_read=False
        )
        db_session.add(notification)
        db_session.commit()
        db_session.refresh(notification)

        # Mark as read
        mark_notification_read(notification.id, db_session)

        # Verify it was marked as read
        db_session.refresh(notification)
        assert notification.is_read is True

    def test_handles_non_existent_notification(self, db_session):
        """Test that marking a non-existent notification doesn't raise an error."""
        # Should not raise an error
        mark_notification_read(99999, db_session)
