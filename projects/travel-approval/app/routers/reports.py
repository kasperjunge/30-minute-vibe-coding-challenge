"""Reports routes for accounting staff to view and export approved travel requests."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.taccount import TAccount
from app.services import notification_service
from app.services.reporting_service import (
    get_approved_requests,
    export_to_csv,
    get_summary_by_taccount
)

router = APIRouter(prefix="/reports", tags=["reports"])

# Import templates from main
from app.main import templates


@router.get("", response_class=HTMLResponse)
async def reports_index(
    request: Request,
    current_user: User = Depends(require_role("accounting", "admin")),
    db: Session = Depends(get_db),
    date_from: Optional[date] = Query(None, description="Filter by approval date from"),
    date_to: Optional[date] = Query(None, description="Filter by approval date to"),
    taccount_id: Optional[int] = Query(None, description="Filter by T-account ID"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: str = Query("approved", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
):
    """
    Display reports page with filters and results.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user (must be accounting or admin)
        db: Database session
        date_from: Optional start date filter
        date_to: Optional end date filter
        taccount_id: Optional T-account filter
        project_id: Optional project filter
        status: Status filter (default: approved)
        page: Page number for pagination (default: 1)

    Returns:
        HTML response with reports page
    """
    # Pagination settings
    per_page = 50
    offset = (page - 1) * per_page

    # Get filtered requests
    all_requests = get_approved_requests(
        db=db,
        date_from=date_from,
        date_to=date_to,
        taccount_id=taccount_id,
        project_id=project_id,
        status=status
    )

    # Calculate pagination
    total_count = len(all_requests)
    total_pages = (total_count + per_page - 1) // per_page
    requests = all_requests[offset:offset + per_page]

    # Calculate total cost
    total_cost = sum(float(req.estimated_cost) for req in all_requests)

    # Get all T-accounts for dropdown (active only)
    taccounts = db.query(TAccount).filter(TAccount.is_active == True).order_by(TAccount.account_code).all()

    # Get all projects for dropdown (active only)
    projects = db.query(Project).filter(Project.is_active == True).order_by(Project.name).all()

    # Get unread notification count
    unread_notifications = notification_service.get_unread_notifications(current_user, db)

    # Status options
    status_options = ["approved", "pending", "rejected"]

    return templates.TemplateResponse(
        request,
        "reports/index.html",
        {
            "current_user": current_user,
            "requests": requests,
            "total_count": total_count,
            "total_cost": total_cost,
            "taccounts": taccounts,
            "projects": projects,
            "status_options": status_options,
            "filters": {
                "date_from": date_from,
                "date_to": date_to,
                "taccount_id": taccount_id,
                "project_id": project_id,
                "status": status,
            },
            "page": page,
            "total_pages": total_pages,
            "per_page": per_page,
            "unread_count": len(unread_notifications),
        },
    )


@router.get("/export", response_class=Response)
async def reports_export(
    current_user: User = Depends(require_role("accounting", "admin")),
    db: Session = Depends(get_db),
    date_from: Optional[date] = Query(None, description="Filter by approval date from"),
    date_to: Optional[date] = Query(None, description="Filter by approval date to"),
    taccount_id: Optional[int] = Query(None, description="Filter by T-account ID"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: str = Query("approved", description="Filter by status"),
):
    """
    Export filtered travel requests as CSV.

    Args:
        current_user: Current authenticated user (must be accounting or admin)
        db: Database session
        date_from: Optional start date filter
        date_to: Optional end date filter
        taccount_id: Optional T-account filter
        project_id: Optional project filter
        status: Status filter (default: approved)

    Returns:
        CSV file download response
    """
    # Get filtered requests
    requests = get_approved_requests(
        db=db,
        date_from=date_from,
        date_to=date_to,
        taccount_id=taccount_id,
        project_id=project_id,
        status=status
    )

    # Generate CSV content
    csv_content = export_to_csv(requests)

    # Generate filename with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"travel_requests_{timestamp}.csv"

    # Return CSV response with proper headers
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/summary", response_class=HTMLResponse)
async def reports_summary(
    request: Request,
    current_user: User = Depends(require_role("accounting", "admin")),
    db: Session = Depends(get_db),
    date_from: date = Query(..., description="Summary start date"),
    date_to: date = Query(..., description="Summary end date"),
):
    """
    Display summary of approved travel requests by T-account.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user (must be accounting or admin)
        db: Database session
        date_from: Start date for summary
        date_to: End date for summary

    Returns:
        JSON response with summary data
    """
    summary = get_summary_by_taccount(db, date_from, date_to)

    # Get unread notification count
    unread_notifications = notification_service.get_unread_notifications(current_user, db)

    return templates.TemplateResponse(
        request,
        "reports/summary.html",
        {
            "current_user": current_user,
            "summary": summary,
            "date_from": date_from,
            "date_to": date_to,
            "total_cost": sum(summary.values()),
            "unread_count": len(unread_notifications),
        },
    )
