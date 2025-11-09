"""Reporting service for generating travel request reports."""

import csv
import io
from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.travel_request import TravelRequest
from app.models.user import User
from app.models.project import Project
from app.models.taccount import TAccount


def get_approved_requests(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    taccount_id: Optional[int] = None,
    project_id: Optional[int] = None,
    status: str = "approved"
) -> list[TravelRequest]:
    """
    Get travel requests with optional filters.

    Args:
        db: Database session
        date_from: Filter by approval_date >= date_from
        date_to: Filter by approval_date <= date_to
        taccount_id: Filter by T-account ID
        project_id: Filter by project ID
        status: Filter by status (default: "approved")

    Returns:
        List of TravelRequest objects matching filters with eager loaded relationships
    """
    # Start with base query including eager loading
    query = db.query(TravelRequest).options(
        joinedload(TravelRequest.requester),
        joinedload(TravelRequest.approver),
        joinedload(TravelRequest.project),
        joinedload(TravelRequest.taccount)
    )

    # Apply status filter
    query = query.filter(TravelRequest.status == status)

    # Apply date range filters
    if date_from:
        query = query.filter(TravelRequest.approval_date >= date_from)
    if date_to:
        query = query.filter(TravelRequest.approval_date <= date_to)

    # Apply T-account filter
    if taccount_id:
        query = query.filter(TravelRequest.taccount_id == taccount_id)

    # Apply project filter
    if project_id:
        query = query.filter(TravelRequest.project_id == project_id)

    # Order by approval_date descending (most recent first)
    query = query.order_by(TravelRequest.approval_date.desc())

    return query.all()


def export_to_csv(requests: list[TravelRequest]) -> str:
    """
    Export travel requests to CSV format.

    Args:
        requests: List of TravelRequest objects to export

    Returns:
        CSV content as a string
    """
    # Create string buffer for CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header row
    headers = [
        "Request ID",
        "Employee Name",
        "Department",
        "Request Type",
        "Project Name",
        "Destination",
        "Start Date",
        "End Date",
        "Purpose",
        "Estimated Cost",
        "T-Account",
        "Status",
        "Approved By",
        "Approval Date"
    ]
    writer.writerow(headers)

    # Write data rows
    for request in requests:
        # Determine department (could be manager's name or "N/A")
        department = request.requester.manager.full_name if request.requester.manager else "N/A"

        # Get project name or "N/A" for operations requests
        project_name = request.project.name if request.project else "N/A"

        # Get approver name
        approver_name = request.approver.full_name if request.approver else "N/A"

        # Format approval date
        approval_date_str = request.approval_date.strftime("%Y-%m-%d %H:%M:%S") if request.approval_date else "N/A"

        # Format T-account info
        taccount_info = f"{request.taccount.account_code} - {request.taccount.account_name}"

        row = [
            request.id,
            request.requester.full_name,
            department,
            request.request_type.capitalize(),
            project_name,
            request.destination,
            request.start_date.strftime("%Y-%m-%d"),
            request.end_date.strftime("%Y-%m-%d"),
            request.purpose,
            f"{float(request.estimated_cost):.2f}",
            taccount_info,
            request.status.capitalize(),
            approver_name,
            approval_date_str
        ]
        writer.writerow(row)

    # Get the CSV content
    csv_content = output.getvalue()
    output.close()

    return csv_content


def get_summary_by_taccount(
    db: Session,
    date_from: date,
    date_to: date
) -> dict:
    """
    Get summary of approved travel requests grouped by T-account.

    Args:
        db: Database session
        date_from: Start date for filtering
        date_to: End date for filtering

    Returns:
        Dictionary mapping T-account names to total costs
        Example: {"T-1234 - Marketing": 15000.00, "T-5678 - Engineering": 25000.00}
    """
    # Query to aggregate costs by T-account
    results = db.query(
        TAccount.account_code,
        TAccount.account_name,
        func.sum(TravelRequest.estimated_cost).label("total_cost")
    ).join(
        TravelRequest, TAccount.id == TravelRequest.taccount_id
    ).filter(
        TravelRequest.status == "approved",
        TravelRequest.approval_date >= date_from,
        TravelRequest.approval_date <= date_to
    ).group_by(
        TAccount.id,
        TAccount.account_code,
        TAccount.account_name
    ).order_by(
        func.sum(TravelRequest.estimated_cost).desc()
    ).all()

    # Convert to dictionary
    summary = {}
    for account_code, account_name, total_cost in results:
        key = f"{account_code} - {account_name}"
        summary[key] = float(total_cost) if total_cost else 0.0

    return summary
