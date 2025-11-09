"""Travel request routes for creating and viewing travel requests."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import get_unread_count, require_auth
from app.database import get_db
from app.models.project import Project
from app.models.taccount import TAccount
from app.models.travel_request import TravelRequest
from app.models.user import User
from app.schemas.travel_request import TravelRequestCreate
from app.services import audit_service, notification_service

router = APIRouter(prefix="/requests", tags=["travel_requests"])

# Import templates from main
from app.main import templates


@router.get("/new", response_class=HTMLResponse)
async def new_travel_request_form(
    request: Request,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Display the create travel request form."""
    # Get active projects for dropdown
    active_projects = db.query(Project).filter(Project.is_active == True).all()

    # Get active T-accounts for dropdown
    active_taccounts = db.query(TAccount).filter(TAccount.is_active == True).all()

    return templates.TemplateResponse(
        request,
        "requests/new.html",
        {
            "current_user": current_user,
            "projects": active_projects,
            "taccounts": active_taccounts,
            "errors": {},
            "unread_count": get_unread_count(current_user, db),
        },
    )


@router.post("/new")
async def create_travel_request(
    request: Request,
    request_type: str = Form(...),
    project_id: int | None = Form(None),
    destination: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    purpose: str = Form(...),
    estimated_cost: str = Form(...),
    taccount_id: int = Form(...),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Create a new travel request."""
    from datetime import date
    from decimal import Decimal, InvalidOperation

    errors = {}

    try:
        # Parse and validate dates
        try:
            start_date_obj = date.fromisoformat(start_date)
            end_date_obj = date.fromisoformat(end_date)
        except ValueError:
            errors["dates"] = "Invalid date format"

        # Parse and validate cost
        try:
            cost = Decimal(estimated_cost)
        except (ValueError, InvalidOperation):
            errors["estimated_cost"] = "Invalid cost format"

        # If we have parsing errors, return form with errors
        if errors:
            active_projects = db.query(Project).filter(Project.is_active == True).all()
            active_taccounts = db.query(TAccount).filter(TAccount.is_active == True).all()
            return templates.TemplateResponse(
                request,
                "requests/new.html",
                {
                    "current_user": current_user,
                    "projects": active_projects,
                    "taccounts": active_taccounts,
                    "errors": errors,
                    "form_data": {
                        "request_type": request_type,
                        "project_id": project_id,
                        "destination": destination,
                        "start_date": start_date,
                        "end_date": end_date,
                        "purpose": purpose,
                        "estimated_cost": estimated_cost,
                        "taccount_id": taccount_id,
                    },
                    "unread_count": get_unread_count(current_user, db),
                    "unread_count": get_unread_count(current_user, db),
                },
                status_code=422,
            )

        # Create and validate schema
        try:
            travel_request_data = TravelRequestCreate(
                request_type=request_type,
                project_id=project_id,
                destination=destination,
                start_date=start_date_obj,
                end_date=end_date_obj,
                purpose=purpose,
                estimated_cost=cost,
                taccount_id=taccount_id,
            )
        except ValueError as e:
            # Pydantic validation error
            errors["validation"] = str(e)
            active_projects = db.query(Project).filter(Project.is_active == True).all()
            active_taccounts = db.query(TAccount).filter(TAccount.is_active == True).all()
            return templates.TemplateResponse(
                request,
                "requests/new.html",
                {
                    "current_user": current_user,
                    "projects": active_projects,
                    "taccounts": active_taccounts,
                    "errors": errors,
                    "form_data": {
                        "request_type": request_type,
                        "project_id": project_id,
                        "destination": destination,
                        "start_date": start_date,
                        "end_date": end_date,
                        "purpose": purpose,
                        "estimated_cost": estimated_cost,
                        "taccount_id": taccount_id,
                    },
                    "unread_count": get_unread_count(current_user, db),
                },
                status_code=422,
            )

        # Determine approver based on request type
        if request_type == "operations":
            # Operations requests go to the employee's manager
            if not current_user.manager_id:
                errors["approver"] = "No manager assigned. Please contact an administrator."
                active_projects = db.query(Project).filter(Project.is_active == True).all()
                active_taccounts = db.query(TAccount).filter(TAccount.is_active == True).all()
                return templates.TemplateResponse(
                    request,
                    "requests/new.html",
                    {
                        "current_user": current_user,
                        "projects": active_projects,
                        "taccounts": active_taccounts,
                        "errors": errors,
                        "form_data": {
                            "request_type": request_type,
                            "project_id": project_id,
                            "destination": destination,
                            "start_date": start_date,
                            "end_date": end_date,
                            "purpose": purpose,
                            "estimated_cost": estimated_cost,
                            "taccount_id": taccount_id,
                        },
                    "unread_count": get_unread_count(current_user, db),
                    },
                    status_code=422,
                )
            approver_id = current_user.manager_id
        else:  # project
            # Project requests go to the project's team lead
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                errors["project"] = "Selected project not found."
                active_projects = db.query(Project).filter(Project.is_active == True).all()
                active_taccounts = db.query(TAccount).filter(TAccount.is_active == True).all()
                return templates.TemplateResponse(
                    request,
                    "requests/new.html",
                    {
                        "current_user": current_user,
                        "projects": active_projects,
                        "taccounts": active_taccounts,
                        "errors": errors,
                        "form_data": {
                            "request_type": request_type,
                            "project_id": project_id,
                            "destination": destination,
                            "start_date": start_date,
                            "end_date": end_date,
                            "purpose": purpose,
                            "estimated_cost": estimated_cost,
                            "taccount_id": taccount_id,
                        },
                    "unread_count": get_unread_count(current_user, db),
                    },
                    status_code=422,
                )
            if not project.team_lead_id:
                errors["approver"] = "Selected project has no team lead assigned. Please contact an administrator."
                active_projects = db.query(Project).filter(Project.is_active == True).all()
                active_taccounts = db.query(TAccount).filter(TAccount.is_active == True).all()
                return templates.TemplateResponse(
                    request,
                    "requests/new.html",
                    {
                        "current_user": current_user,
                        "projects": active_projects,
                        "taccounts": active_taccounts,
                        "errors": errors,
                        "form_data": {
                            "request_type": request_type,
                            "project_id": project_id,
                            "destination": destination,
                            "start_date": start_date,
                            "end_date": end_date,
                            "purpose": purpose,
                            "estimated_cost": estimated_cost,
                            "taccount_id": taccount_id,
                        },
                    "unread_count": get_unread_count(current_user, db),
                    },
                    status_code=422,
                )
            approver_id = project.team_lead_id

        # Create the travel request
        new_request = TravelRequest(
            requester_id=current_user.id,
            request_type=travel_request_data.request_type,
            project_id=travel_request_data.project_id,
            destination=travel_request_data.destination,
            start_date=travel_request_data.start_date,
            end_date=travel_request_data.end_date,
            purpose=travel_request_data.purpose,
            estimated_cost=travel_request_data.estimated_cost,
            taccount_id=travel_request_data.taccount_id,
            approver_id=approver_id,
            status="pending",
        )

        db.add(new_request)
        db.commit()
        db.refresh(new_request)

        # Send notification to approver
        notification_service.notify_request_submitted(new_request, db)

        # Redirect to dashboard with success message
        # TODO: Add flash message support in future
        return RedirectResponse(url="/dashboard", status_code=303)

    except Exception as e:
        db.rollback()
        errors["general"] = f"An error occurred while creating the request: {str(e)}"
        active_projects = db.query(Project).filter(Project.is_active == True).all()
        active_taccounts = db.query(TAccount).filter(TAccount.is_active == True).all()
        return templates.TemplateResponse(
            request,
            "requests/new.html",
            {
                "current_user": current_user,
                "projects": active_projects,
                "taccounts": active_taccounts,
                "errors": errors,
                "form_data": {
                    "request_type": request_type,
                    "project_id": project_id,
                    "destination": destination,
                    "start_date": start_date,
                    "end_date": end_date,
                    "purpose": purpose,
                    "estimated_cost": estimated_cost,
                    "taccount_id": taccount_id,
                },
                    "unread_count": get_unread_count(current_user, db),
            },
            status_code=500,
        )


@router.get("/{request_id}", response_class=HTMLResponse)
async def view_travel_request(
    request: Request,
    request_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """View a travel request detail."""
    travel_request = (
        db.query(TravelRequest)
        .options(
            joinedload(TravelRequest.requester),
            joinedload(TravelRequest.approver),
            joinedload(TravelRequest.project),
            joinedload(TravelRequest.taccount)
        )
        .filter(TravelRequest.id == request_id)
        .first()
    )

    if not travel_request:
        raise HTTPException(status_code=404, detail="Travel request not found")

    # Check authorization: user must be the requester or approver
    if (
        travel_request.requester_id != current_user.id
        and travel_request.approver_id != current_user.id
        and current_user.role not in ["admin", "accounting"]
    ):
        raise HTTPException(status_code=403, detail="Not authorized to view this request")

    return templates.TemplateResponse(
        request,
        "requests/detail.html",
        {
            "current_user": current_user,
            "travel_request": travel_request,
            "errors": {},
            "unread_count": get_unread_count(current_user, db),
        },
    )


@router.post("/{request_id}/approve")
async def approve_travel_request(
    request: Request,
    request_id: int,
    comments: str = Form(None),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Approve a travel request."""
    from datetime import datetime

    travel_request = (
        db.query(TravelRequest)
        .options(
            joinedload(TravelRequest.requester),
            joinedload(TravelRequest.approver)
        )
        .filter(TravelRequest.id == request_id)
        .first()
    )

    if not travel_request:
        raise HTTPException(status_code=404, detail="Travel request not found")

    # Verify user is the approver
    if travel_request.approver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the designated approver can approve this request")

    # Verify request is still pending
    if travel_request.status != "pending":
        raise HTTPException(status_code=400, detail="This request has already been processed")

    # Update the travel request
    travel_request.status = "approved"
    travel_request.approval_date = datetime.utcnow()
    travel_request.approval_comments = comments if comments else None

    db.commit()

    # Log the approval action
    audit_service.log_action(
        user_id=current_user.id,
        action="approve",
        entity_type="travel_request",
        entity_id=travel_request.id,
        details={
            "request_id": travel_request.id,
            "requester_id": travel_request.requester_id,
            "destination": travel_request.destination,
            "estimated_cost": str(travel_request.estimated_cost),
            "comments": comments,
        },
        db=db,
    )

    # Send notifications
    notification_service.notify_request_approved(travel_request, db)

    # Redirect to approvals page
    return RedirectResponse(url="/approvals", status_code=303)


@router.post("/{request_id}/reject")
async def reject_travel_request(
    request: Request,
    request_id: int,
    reason: str = Form(...),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Reject a travel request."""
    from datetime import datetime

    travel_request = (
        db.query(TravelRequest)
        .options(
            joinedload(TravelRequest.requester),
            joinedload(TravelRequest.approver)
        )
        .filter(TravelRequest.id == request_id)
        .first()
    )

    if not travel_request:
        raise HTTPException(status_code=404, detail="Travel request not found")

    # Verify user is the approver
    if travel_request.approver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the designated approver can reject this request")

    # Verify request is still pending
    if travel_request.status != "pending":
        raise HTTPException(status_code=400, detail="This request has already been processed")

    # Verify reason is provided and not empty
    if not reason or not reason.strip():
        # Return to detail page with error
        return templates.TemplateResponse(
            request,
            "requests/detail.html",
            {
                "current_user": current_user,
                "travel_request": travel_request,
                "errors": {"rejection_reason": "Rejection reason is required"},
                "unread_count": get_unread_count(current_user, db),
            },
            status_code=422,
        )

    # Update the travel request
    travel_request.status = "rejected"
    travel_request.approval_date = datetime.utcnow()
    travel_request.rejection_reason = reason.strip()

    db.commit()

    # Log the rejection action
    audit_service.log_action(
        user_id=current_user.id,
        action="reject",
        entity_type="travel_request",
        entity_id=travel_request.id,
        details={
            "request_id": travel_request.id,
            "requester_id": travel_request.requester_id,
            "destination": travel_request.destination,
            "estimated_cost": str(travel_request.estimated_cost),
            "rejection_reason": reason.strip(),
        },
        db=db,
    )

    # Send notification
    notification_service.notify_request_rejected(travel_request, db)

    # Redirect to approvals page
    return RedirectResponse(url="/approvals", status_code=303)
