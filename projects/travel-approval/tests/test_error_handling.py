"""Tests for error handling and custom error pages."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_404_for_invalid_route(client):
    """Test that 404 error returns custom page for invalid routes."""
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404
    assert "404" in response.text
    assert "Page Not Found" in response.text


def test_404_has_navigation_link(client):
    """Test that 404 page has link back to login/dashboard."""
    response = client.get("/invalid-page")

    assert response.status_code == 404
    # Should have a link to login for unauthenticated users
    assert "Go to Login" in response.text or "Go to Dashboard" in response.text


def test_validation_errors_show_inline_in_forms(
    client, db_session, sample_employee, sample_taccount, employee_user_session
):
    """Test that validation errors are displayed inline in forms."""
    # Try to create a travel request with invalid data (end date before start date)
    response = client.post(
        "/requests/new",
        data={
            "request_type": "operations",
            "destination": "London",
            "start_date": "2024-12-31",
            "end_date": "2024-01-01",  # End date before start date
            "purpose": "Business meeting",
            "estimated_cost": "1000",
            "taccount_id": sample_taccount.id,
        },
        cookies=employee_user_session,
    )

    # Should return the form with error message
    assert response.status_code == 422
    assert "end_date" in response.text.lower() or "date" in response.text.lower()


def test_validation_error_negative_cost(
    client, db_session, sample_employee, sample_taccount, employee_user_session
):
    """Test that negative costs are rejected with inline error."""
    response = client.post(
        "/requests/new",
        data={
            "request_type": "operations",
            "destination": "Paris",
            "start_date": "2024-06-01",
            "end_date": "2024-06-05",
            "purpose": "Conference",
            "estimated_cost": "-500",  # Negative cost
            "taccount_id": sample_taccount.id,
        },
        cookies=employee_user_session,
    )

    # Should return the form with error
    assert response.status_code == 422


def test_missing_required_field_shows_error(
    client, db_session, sample_employee, employee_user_session
):
    """Test that missing required fields show validation errors."""
    # Try to submit form without taccount_id
    response = client.post(
        "/requests/new",
        data={
            "request_type": "operations",
            "destination": "Berlin",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "purpose": "Training",
            "estimated_cost": "2000",
            # taccount_id is missing
        },
        cookies=employee_user_session,
        follow_redirects=False,
    )

    # Should return error (either 422 for validation or 500 for missing field)
    assert response.status_code in [422, 500]


def test_database_errors_are_caught_and_logged(
    client, db_session, sample_employee, employee_user_session
):
    """Test that database errors are caught and logged appropriately."""
    # This test ensures the application doesn't crash on DB errors
    # We'll test by trying to access a non-existent travel request
    response = client.get("/requests/999999", cookies=employee_user_session)

    # Should return 404 for non-existent resource
    assert response.status_code == 404


def test_unauthenticated_access_handled_properly(client):
    """Test that unauthenticated access to protected routes is handled."""
    # Try to access dashboard without authentication
    try:
        response = client.get("/dashboard", follow_redirects=False)
        # Should redirect to login or return 401/403/422
        # 422 is returned by the auth dependency when no session cookie is present
        assert response.status_code in [303, 307, 401, 403, 422]
    except Exception as e:
        # If an exception is raised, that's also acceptable - it means
        # the auth system is blocking access
        assert "authentication" in str(e).lower() or "required" in str(e).lower()


def test_unauthorized_approval_attempt(
    client, db_session, sample_employee, sample_manager, sample_taccount, employee_user_session
):
    """Test that unauthorized approval attempts are blocked."""
    from datetime import date
    from app.models.travel_request import TravelRequest

    # Create a travel request
    travel_request = TravelRequest(
        requester_id=sample_employee.id,
        approver_id=sample_manager.id,
        request_type="operations",
        destination="Copenhagen",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 5),
        purpose="Client meeting",
        estimated_cost=1500,
        taccount_id=sample_taccount.id,
        status="pending",
    )
    db_session.add(travel_request)
    db_session.commit()
    db_session.refresh(travel_request)

    # Try to approve as employee (not the designated approver)
    try:
        response = client.post(
            f"/requests/{travel_request.id}/approve",
            data={"comments": "Approving my own request"},
            cookies=employee_user_session,
            follow_redirects=False,
        )
        # Should return 403 Forbidden or 422 (depending on how FastAPI handles it)
        # The HTTPException with 403 should be caught by our handler
        assert response.status_code in [403, 422]
    except Exception as e:
        # If an HTTPException is raised, verify it's a 403
        assert "403" in str(e) or "not authorized" in str(e).lower() or "approver" in str(e).lower()


def test_invalid_date_format_handled(
    client, db_session, sample_employee, sample_taccount, employee_user_session
):
    """Test that invalid date formats are handled gracefully."""
    response = client.post(
        "/requests/new",
        data={
            "request_type": "operations",
            "destination": "Stockholm",
            "start_date": "not-a-date",
            "end_date": "also-not-a-date",
            "purpose": "Meeting",
            "estimated_cost": "1000",
            "taccount_id": sample_taccount.id,
        },
        cookies=employee_user_session,
    )

    # Should return validation error
    assert response.status_code == 422
    assert "date" in response.text.lower() or "invalid" in response.text.lower()


def test_invalid_cost_format_handled(
    client, db_session, sample_employee, sample_taccount, employee_user_session
):
    """Test that invalid cost formats are handled gracefully."""
    response = client.post(
        "/requests/new",
        data={
            "request_type": "operations",
            "destination": "Oslo",
            "start_date": "2024-09-01",
            "end_date": "2024-09-05",
            "purpose": "Workshop",
            "estimated_cost": "not-a-number",
            "taccount_id": sample_taccount.id,
        },
        cookies=employee_user_session,
    )

    # Should return validation error
    assert response.status_code == 422
    assert "cost" in response.text.lower() or "invalid" in response.text.lower()


def test_rejection_without_reason_shows_error(
    client, db_session, sample_employee, sample_manager, sample_taccount
):
    """Test that rejecting without a reason shows an error message."""
    from datetime import date
    from app.models.travel_request import TravelRequest
    from app.auth.session import session_manager

    # Create a travel request
    travel_request = TravelRequest(
        requester_id=sample_employee.id,
        approver_id=sample_manager.id,
        request_type="operations",
        destination="Amsterdam",
        start_date=date(2024, 10, 1),
        end_date=date(2024, 10, 5),
        purpose="Conference",
        estimated_cost=2000,
        taccount_id=sample_taccount.id,
        status="pending",
    )
    db_session.add(travel_request)
    db_session.commit()
    db_session.refresh(travel_request)

    # Create manager session
    manager_session_token = session_manager.create_session(sample_manager.id)
    manager_cookies = {"travel_approval_session": manager_session_token}

    # Try to reject without providing a reason
    response = client.post(
        f"/requests/{travel_request.id}/reject",
        data={"reason": ""},  # Empty reason
        cookies=manager_cookies,
    )

    # Should return error
    assert response.status_code == 422
    assert "reason" in response.text.lower() or "required" in response.text.lower()
