"""Travel Request Service - Core business logic for travel request lifecycle."""

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.travel_request import TravelRequest
from app.models.user import User
from app.schemas.travel_request import TravelRequestCreate


def determine_approver(request: TravelRequest, db: Session) -> User:
    """
    Determine the approver for a travel request based on request type.

    Args:
        request: TravelRequest object (with relationships loaded)
        db: Database session

    Returns:
        User object representing the approver

    Raises:
        HTTPException: 400 if manager or team_lead is not assigned
    """
    if request.request_type == "operations":
        # Operations requests route to the requester's manager
        if request.requester.manager_id is None:
            raise HTTPException(
                status_code=400,
                detail="Cannot route request: employee has no manager assigned. Please contact admin."
            )

        manager = db.query(User).filter(User.id == request.requester.manager_id).first()
        if manager is None:
            raise HTTPException(
                status_code=400,
                detail="Cannot route request: assigned manager not found in system."
            )
        return manager

    elif request.request_type == "project":
        # Project requests route to the project's team lead
        if request.project is None:
            raise HTTPException(
                status_code=400,
                detail="Cannot route request: project not found."
            )

        if request.project.team_lead_id is None:
            raise HTTPException(
                status_code=400,
                detail="Cannot route request: project has no team lead assigned. Please contact admin."
            )

        team_lead = db.query(User).filter(User.id == request.project.team_lead_id).first()
        if team_lead is None:
            raise HTTPException(
                status_code=400,
                detail="Cannot route request: assigned team lead not found in system."
            )
        return team_lead

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request type: {request.request_type}"
        )


def create_request(request_data: TravelRequestCreate, user: User, db: Session) -> TravelRequest:
    """
    Create a new travel request with automatic approver routing.

    Args:
        request_data: TravelRequestCreate schema with validated data
        user: User object (requester)
        db: Database session

    Returns:
        Created TravelRequest object with approver assigned

    Raises:
        HTTPException: 400 if routing fails (no manager/team_lead)
    """
    # Create travel request with status="pending"
    travel_request = TravelRequest(
        requester_id=user.id,
        request_type=request_data.request_type,
        project_id=request_data.project_id,
        destination=request_data.destination,
        start_date=request_data.start_date,
        end_date=request_data.end_date,
        purpose=request_data.purpose,
        estimated_cost=request_data.estimated_cost,
        taccount_id=request_data.taccount_id,
        status="pending"
    )

    db.add(travel_request)
    db.flush()  # Get the ID without committing

    # Load relationships needed for determine_approver
    db.refresh(travel_request)
    travel_request.requester = user

    if request_data.request_type == "project" and request_data.project_id:
        # Load project relationship properly
        from app.models.project import Project
        travel_request.project = db.query(Project).filter(Project.id == request_data.project_id).first()
        if travel_request.project is None:
            raise HTTPException(
                status_code=400,
                detail=f"Project with ID {request_data.project_id} not found"
            )

    # Determine and set approver
    approver = determine_approver(travel_request, db)
    travel_request.approver_id = approver.id

    db.commit()
    db.refresh(travel_request)

    return travel_request


def get_pending_requests_for_approver(user: User, db: Session) -> list[TravelRequest]:
    """
    Get all pending travel requests where the user is the designated approver.

    Args:
        user: User object (approver)
        db: Database session

    Returns:
        List of TravelRequest objects with eager-loaded relationships
    """
    requests = db.query(TravelRequest).options(
        joinedload(TravelRequest.requester),
        joinedload(TravelRequest.project),
        joinedload(TravelRequest.taccount)
    ).filter(
        TravelRequest.approver_id == user.id,
        TravelRequest.status == "pending"
    ).all()

    return requests


def approve_request(
    request_id: int,
    approver: User,
    comments: str | None,
    db: Session
) -> TravelRequest:
    """
    Approve a travel request.

    Args:
        request_id: ID of the travel request
        approver: User object (must be the designated approver)
        comments: Optional approval comments
        db: Database session

    Returns:
        Updated TravelRequest object

    Raises:
        HTTPException: 403 if user is not the designated approver
        HTTPException: 400 if request is not in pending status
        HTTPException: 404 if request not found
    """
    # Get the travel request
    travel_request = db.query(TravelRequest).filter(
        TravelRequest.id == request_id
    ).first()

    if travel_request is None:
        raise HTTPException(status_code=404, detail="Travel request not found")

    # Verify approver_id matches
    if travel_request.approver_id != approver.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized: you are not the designated approver for this request"
        )

    # Verify status is pending
    if travel_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve: request is already {travel_request.status}"
        )

    # Update request
    travel_request.status = "approved"
    travel_request.approval_date = datetime.utcnow()
    travel_request.approval_comments = comments

    db.commit()
    db.refresh(travel_request)

    return travel_request


def reject_request(
    request_id: int,
    approver: User,
    reason: str,
    db: Session
) -> TravelRequest:
    """
    Reject a travel request.

    Args:
        request_id: ID of the travel request
        approver: User object (must be the designated approver)
        reason: Rejection reason (required, must not be empty)
        db: Database session

    Returns:
        Updated TravelRequest object

    Raises:
        HTTPException: 400 if reason is empty
        HTTPException: 403 if user is not the designated approver
        HTTPException: 400 if request is not in pending status
        HTTPException: 404 if request not found
    """
    # Verify reason is not empty
    if not reason or not reason.strip():
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required and cannot be empty"
        )

    # Get the travel request
    travel_request = db.query(TravelRequest).filter(
        TravelRequest.id == request_id
    ).first()

    if travel_request is None:
        raise HTTPException(status_code=404, detail="Travel request not found")

    # Verify approver_id matches
    if travel_request.approver_id != approver.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized: you are not the designated approver for this request"
        )

    # Verify status is pending
    if travel_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reject: request is already {travel_request.status}"
        )

    # Update request
    travel_request.status = "rejected"
    travel_request.approval_date = datetime.utcnow()
    travel_request.rejection_reason = reason.strip()

    db.commit()
    db.refresh(travel_request)

    return travel_request
