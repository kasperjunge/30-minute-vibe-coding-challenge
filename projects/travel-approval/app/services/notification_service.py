"""Notification service for creating and managing notifications."""

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.travel_request import TravelRequest
from app.models.user import User


def notify_request_submitted(request: TravelRequest, db: Session) -> None:
    """
    Create notification for approver when a request is submitted.

    Args:
        request: The travel request that was submitted
        db: Database session
    """
    # Get the approver and requester names
    requester = db.query(User).filter(User.id == request.requester_id).first()

    if not requester:
        return  # Skip if requester not found

    message = f"New travel request #{request.id} from {requester.full_name} requires your approval"

    notification = Notification(
        user_id=request.approver_id,
        travel_request_id=request.id,
        notification_type="request_submitted",
        message=message,
        is_read=False
    )

    db.add(notification)
    db.commit()


def notify_request_approved(request: TravelRequest, db: Session) -> None:
    """
    Create notifications when a request is approved.
    Notifies the employee (requester) and all accounting staff.

    Args:
        request: The travel request that was approved
        db: Database session
    """
    # Get the approver name
    approver = db.query(User).filter(User.id == request.approver_id).first()
    approver_name = approver.full_name if approver else "Unknown"

    # Notify the employee (requester)
    employee_message = f"Your travel request #{request.id} has been approved by {approver_name}"

    employee_notification = Notification(
        user_id=request.requester_id,
        travel_request_id=request.id,
        notification_type="request_approved",
        message=employee_message,
        is_read=False
    )

    db.add(employee_notification)

    # Notify all accounting staff
    accounting_staff = db.query(User).filter(User.role == "accounting", User.is_active == True).all()

    for accountant in accounting_staff:
        accounting_message = f"Travel request #{request.id} has been approved and requires processing"

        accounting_notification = Notification(
            user_id=accountant.id,
            travel_request_id=request.id,
            notification_type="request_approved",
            message=accounting_message,
            is_read=False
        )

        db.add(accounting_notification)

    db.commit()


def notify_request_rejected(request: TravelRequest, db: Session) -> None:
    """
    Create notification for employee when their request is rejected.

    Args:
        request: The travel request that was rejected
        db: Database session
    """
    # Get the rejection reason
    reason = request.rejection_reason if request.rejection_reason else "No reason provided"

    message = f"Your travel request #{request.id} has been rejected: {reason}"

    notification = Notification(
        user_id=request.requester_id,
        travel_request_id=request.id,
        notification_type="request_rejected",
        message=message,
        is_read=False
    )

    db.add(notification)
    db.commit()


def get_unread_notifications(user: User, db: Session) -> list[Notification]:
    """
    Get all unread notifications for a user.

    Args:
        user: The user to get notifications for
        db: Database session

    Returns:
        List of unread Notification objects
    """
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user.id, Notification.is_read == False)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return notifications


def mark_notification_read(notification_id: int, db: Session) -> None:
    """
    Mark a notification as read.

    Args:
        notification_id: ID of the notification to mark as read
        db: Database session
    """
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if notification:
        notification.is_read = True
        db.commit()
