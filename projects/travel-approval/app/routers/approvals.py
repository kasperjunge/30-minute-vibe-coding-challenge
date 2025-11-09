"""Approvals routes for managers and team leads to review pending travel requests."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import require_auth
from app.database import get_db
from app.models.travel_request import TravelRequest
from app.models.user import User
from app.services import notification_service

router = APIRouter(prefix="/approvals", tags=["approvals"])

# Import templates from main
from app.main import templates


@router.get("", response_class=HTMLResponse)
async def approvals_list(
    request: Request,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Display pending approvals for managers and team leads."""
    # Check that user has manager or team_lead role
    if current_user.role not in ["manager", "team_lead", "admin"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied. Only managers and team leads can access approvals.")

    # Query pending requests where current user is the approver (with eager loading to prevent N+1 queries)
    pending_requests = (
        db.query(TravelRequest)
        .options(
            joinedload(TravelRequest.requester),
            joinedload(TravelRequest.project),
            joinedload(TravelRequest.taccount)
        )
        .filter(
            TravelRequest.approver_id == current_user.id,
            TravelRequest.status == "pending"
        )
        .order_by(TravelRequest.created_at.desc())
        .limit(50)
        .all()
    )

    # Get unread notification count
    unread_notifications = notification_service.get_unread_notifications(current_user, db)

    return templates.TemplateResponse(
        request,
        "approvals/list.html",
        {
            "current_user": current_user,
            "pending_requests": pending_requests,
            "pending_count": len(pending_requests),
            "unread_count": len(unread_notifications),
        },
    )
