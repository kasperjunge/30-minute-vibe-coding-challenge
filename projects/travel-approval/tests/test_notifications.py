"""Integration tests for notifications."""

from datetime import date
from decimal import Decimal

import pytest

from app.models.notification import Notification
from app.models.travel_request import TravelRequest
from app.models.user import User


class TestNotificationIntegration:
    """Integration tests for notification workflow."""

    def test_creating_request_triggers_notification_to_approver(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that creating a travel request creates a notification for the approver."""
        # Create travel request
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

        # Manually trigger notification (simulating what happens in the router)
        from app.services.notification_service import notify_request_submitted
        notify_request_submitted(travel_request, db_session)

        # Verify notification was created for approver
        notifications = db_session.query(Notification).filter(
            Notification.user_id == sample_manager.id,
            Notification.travel_request_id == travel_request.id
        ).all()

        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.notification_type == "request_submitted"
        assert notification.is_read is False
        assert str(travel_request.id) in notification.message
        assert sample_employee.full_name in notification.message

    def test_approving_request_triggers_notifications(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that approving a request creates notifications for employee and accounting."""
        # Create accounting staff
        accountant = User(
            email="accountant@test.com",
            password_hash="hashed_password",
            full_name="Test Accountant",
            role="accounting",
            is_active=True
        )
        db_session.add(accountant)
        db_session.commit()

        # Create travel request
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="London",
            start_date=date(2025, 7, 10),
            end_date=date(2025, 7, 12),
            purpose="Training",
            estimated_cost=Decimal("4000.00"),
            taccount_id=sample_taccount.id,
            approver_id=sample_manager.id,
            status="approved"
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        # Manually trigger notification (simulating what happens in the router)
        from app.services.notification_service import notify_request_approved
        notify_request_approved(travel_request, db_session)

        # Verify notification was created for employee
        employee_notifications = db_session.query(Notification).filter(
            Notification.user_id == sample_employee.id,
            Notification.travel_request_id == travel_request.id
        ).all()

        assert len(employee_notifications) == 1
        employee_notification = employee_notifications[0]
        assert employee_notification.notification_type == "request_approved"
        assert employee_notification.is_read is False
        assert "approved" in employee_notification.message.lower()
        assert sample_manager.full_name in employee_notification.message

        # Verify notification was created for accountant
        accounting_notifications = db_session.query(Notification).filter(
            Notification.user_id == accountant.id,
            Notification.travel_request_id == travel_request.id
        ).all()

        assert len(accounting_notifications) == 1
        accounting_notification = accounting_notifications[0]
        assert accounting_notification.notification_type == "request_approved"
        assert accounting_notification.is_read is False
        assert "requires processing" in accounting_notification.message

    def test_rejecting_request_triggers_notification(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that rejecting a request creates a notification for the employee."""
        # Create travel request
        rejection_reason = "Budget constraints for this quarter"
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Rome",
            start_date=date(2025, 8, 15),
            end_date=date(2025, 8, 17),
            purpose="Conference",
            estimated_cost=Decimal("6000.00"),
            taccount_id=sample_taccount.id,
            approver_id=sample_manager.id,
            status="rejected",
            rejection_reason=rejection_reason
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        # Manually trigger notification (simulating what happens in the router)
        from app.services.notification_service import notify_request_rejected
        notify_request_rejected(travel_request, db_session)

        # Verify notification was created for employee
        notifications = db_session.query(Notification).filter(
            Notification.user_id == sample_employee.id,
            Notification.travel_request_id == travel_request.id
        ).all()

        assert len(notifications) == 1
        notification = notifications[0]
        assert notification.notification_type == "request_rejected"
        assert notification.is_read is False
        assert "rejected" in notification.message.lower()
        assert rejection_reason in notification.message

    def test_notification_links_to_travel_request(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that notifications are properly linked to their travel requests."""
        # Create travel request
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Berlin",
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 3),
            purpose="Workshop",
            estimated_cost=Decimal("3500.00"),
            taccount_id=sample_taccount.id,
            approver_id=sample_manager.id,
            status="pending"
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        # Create notification
        from app.services.notification_service import notify_request_submitted
        notify_request_submitted(travel_request, db_session)

        # Get notification
        notification = db_session.query(Notification).filter(
            Notification.user_id == sample_manager.id
        ).first()

        # Verify link
        assert notification.travel_request_id == travel_request.id
        assert notification.travel_request is not None
        assert notification.travel_request.destination == "Berlin"

    def test_multiple_accounting_staff_receive_notifications(
        self, db_session, sample_employee, sample_manager, sample_taccount
    ):
        """Test that all active accounting staff receive notifications when a request is approved."""
        # Create multiple accounting staff
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
        accountant3 = User(
            email="accountant3@test.com",
            password_hash="hashed_password",
            full_name="Accountant Three",
            role="accounting",
            is_active=True
        )
        db_session.add(accountant1)
        db_session.add(accountant2)
        db_session.add(accountant3)
        db_session.commit()

        # Create and approve travel request
        travel_request = TravelRequest(
            requester_id=sample_employee.id,
            request_type="operations",
            destination="Madrid",
            start_date=date(2025, 10, 5),
            end_date=date(2025, 10, 7),
            purpose="Sales meeting",
            estimated_cost=Decimal("4500.00"),
            taccount_id=sample_taccount.id,
            approver_id=sample_manager.id,
            status="approved"
        )
        db_session.add(travel_request)
        db_session.commit()
        db_session.refresh(travel_request)

        # Trigger notifications
        from app.services.notification_service import notify_request_approved
        notify_request_approved(travel_request, db_session)

        # Verify all accountants received notifications
        accounting_notifications = db_session.query(Notification).filter(
            Notification.user_id.in_([accountant1.id, accountant2.id, accountant3.id])
        ).all()

        assert len(accounting_notifications) == 3

        # Verify each accountant got one notification
        accountant_ids = [n.user_id for n in accounting_notifications]
        assert accountant1.id in accountant_ids
        assert accountant2.id in accountant_ids
        assert accountant3.id in accountant_ids
