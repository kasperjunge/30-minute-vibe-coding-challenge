"""Notifications routes for viewing and managing notifications."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import require_auth
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])

# Import templates from main
from app.main import templates


@router.get("", response_class=HTMLResponse)
async def list_notifications(
    request: Request,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Display all notifications for the current user."""
    # Get all notifications (both read and unread) for better UX (limited to 100 most recent)
    all_notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(100)
        .all()
    )

    # Get unread count
    unread_notifications = notification_service.get_unread_notifications(current_user, db)

    return templates.TemplateResponse(
        request,
        "notifications/list.html",
        {
            "current_user": current_user,
            "notifications": all_notifications,
            "unread_count": len(unread_notifications),
        },
    )


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Mark a notification as read."""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    # Verify the notification belongs to the current user
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this notification")

    # Mark as read
    notification_service.mark_notification_read(notification_id, db)

    # Redirect back to notifications page
    return RedirectResponse(url="/notifications", status_code=303)
