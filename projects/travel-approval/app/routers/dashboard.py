"""Dashboard route - main user interface for viewing travel requests."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import require_auth
from app.database import get_db
from app.models.travel_request import TravelRequest
from app.models.user import User
from app.services import notification_service

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Display dashboard with user's travel requests grouped by status."""

    # Query user's travel requests grouped by status (with eager loading to prevent N+1 queries)
    pending_requests = (
        db.query(TravelRequest)
        .options(
            joinedload(TravelRequest.approver),
            joinedload(TravelRequest.project),
            joinedload(TravelRequest.taccount)
        )
        .filter(
            TravelRequest.requester_id == current_user.id,
            TravelRequest.status == "pending"
        )
        .order_by(TravelRequest.created_at.desc())
        .limit(50)
        .all()
    )

    approved_requests = (
        db.query(TravelRequest)
        .options(
            joinedload(TravelRequest.approver),
            joinedload(TravelRequest.project),
            joinedload(TravelRequest.taccount)
        )
        .filter(
            TravelRequest.requester_id == current_user.id,
            TravelRequest.status == "approved"
        )
        .order_by(TravelRequest.approval_date.desc())
        .limit(50)
        .all()
    )

    rejected_requests = (
        db.query(TravelRequest)
        .options(
            joinedload(TravelRequest.approver),
            joinedload(TravelRequest.project),
            joinedload(TravelRequest.taccount)
        )
        .filter(
            TravelRequest.requester_id == current_user.id,
            TravelRequest.status == "rejected"
        )
        .order_by(TravelRequest.approval_date.desc())
        .limit(50)
        .all()
    )

    # Get unread notification count
    unread_notifications = notification_service.get_unread_notifications(current_user, db)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "current_user": current_user,
            "pending_requests": pending_requests,
            "approved_requests": approved_requests,
            "rejected_requests": rejected_requests,
            "unread_count": len(unread_notifications),
        }
    )
