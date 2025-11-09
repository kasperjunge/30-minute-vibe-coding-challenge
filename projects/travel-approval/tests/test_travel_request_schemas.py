"""Tests for travel request schemas and validation."""

import pytest
from datetime import date
from decimal import Decimal
from pydantic import ValidationError

from app.schemas.travel_request import TravelRequestCreate


def test_valid_operations_request_passes_validation():
    """Test that valid operations request data passes validation."""
    request_data = TravelRequestCreate(
        request_type="operations",
        project_id=None,
        destination="Copenhagen",
        start_date=date(2025, 12, 1),
        end_date=date(2025, 12, 5),
        purpose="Client meeting and business development",
        estimated_cost=Decimal("5000.00"),
        taccount_id=1,
    )

    assert request_data.request_type == "operations"
    assert request_data.project_id is None
    assert request_data.destination == "Copenhagen"
    assert request_data.estimated_cost == Decimal("5000.00")


def test_valid_project_request_passes_validation():
    """Test that valid project request data passes validation."""
    request_data = TravelRequestCreate(
        request_type="project",
        project_id=1,
        destination="London",
        start_date=date(2025, 12, 1),
        end_date=date(2025, 12, 5),
        purpose="Project kickoff meeting",
        estimated_cost=Decimal("7500.50"),
        taccount_id=2,
    )

    assert request_data.request_type == "project"
    assert request_data.project_id == 1
    assert request_data.destination == "London"
    assert request_data.estimated_cost == Decimal("7500.50")


def test_end_date_before_start_date_raises_error():
    """Test that end_date before start_date raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        TravelRequestCreate(
            request_type="operations",
            project_id=None,
            destination="Paris",
            start_date=date(2025, 12, 10),
            end_date=date(2025, 12, 5),  # End before start
            purpose="Conference attendance",
            estimated_cost=Decimal("4000.00"),
            taccount_id=1,
        )

    # Check that the error message mentions the date validation
    error_message = str(exc_info.value)
    assert "End date must be on or after start date" in error_message


def test_negative_cost_raises_error():
    """Test that negative estimated cost raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        TravelRequestCreate(
            request_type="operations",
            project_id=None,
            destination="Berlin",
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 5),
            purpose="Training workshop",
            estimated_cost=Decimal("-500.00"),  # Negative cost
            taccount_id=1,
        )

    # Check that the error message mentions cost validation
    error_message = str(exc_info.value)
    assert "Estimated cost must be greater than 0" in error_message or "greater than 0" in error_message


def test_zero_cost_raises_error():
    """Test that zero estimated cost raises validation error."""
    with pytest.raises(ValidationError) as exc_info:
        TravelRequestCreate(
            request_type="operations",
            project_id=None,
            destination="Brussels",
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 5),
            purpose="EU meetings",
            estimated_cost=Decimal("0.00"),  # Zero cost
            taccount_id=1,
        )

    # Check that the error message mentions cost validation
    error_message = str(exc_info.value)
    assert "greater than 0" in error_message


def test_project_type_requires_project_id():
    """Test that project type requests require project_id to be set."""
    with pytest.raises(ValidationError) as exc_info:
        TravelRequestCreate(
            request_type="project",
            project_id=None,  # Missing project_id for project type
            destination="Amsterdam",
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 5),
            purpose="Project milestone review",
            estimated_cost=Decimal("3000.00"),
            taccount_id=1,
        )

    # Check that the error message mentions project_id requirement
    error_message = str(exc_info.value)
    assert "Project ID is required for project-type requests" in error_message


def test_operations_type_does_not_require_project_id():
    """Test that operations type requests work without project_id."""
    request_data = TravelRequestCreate(
        request_type="operations",
        project_id=None,  # No project_id for operations
        destination="Stockholm",
        start_date=date(2025, 12, 1),
        end_date=date(2025, 12, 5),
        purpose="Annual operations review",
        estimated_cost=Decimal("6000.00"),
        taccount_id=1,
    )

    assert request_data.request_type == "operations"
    assert request_data.project_id is None


def test_operations_type_should_not_have_project_id():
    """Test that operations type requests should not have project_id set."""
    with pytest.raises(ValidationError) as exc_info:
        TravelRequestCreate(
            request_type="operations",
            project_id=5,  # project_id set for operations (should not be)
            destination="Oslo",
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 5),
            purpose="Operations meeting",
            estimated_cost=Decimal("4500.00"),
            taccount_id=1,
        )

    # Check that the error message mentions project_id should not be set
    error_message = str(exc_info.value)
    assert "Project ID should not be set for operations-type requests" in error_message


def test_same_start_and_end_date_is_valid():
    """Test that having same start and end date is valid (same day trip)."""
    request_data = TravelRequestCreate(
        request_type="operations",
        project_id=None,
        destination="Aarhus",
        start_date=date(2025, 12, 1),
        end_date=date(2025, 12, 1),  # Same day
        purpose="One-day workshop",
        estimated_cost=Decimal("1500.00"),
        taccount_id=1,
    )

    assert request_data.start_date == request_data.end_date


def test_empty_destination_raises_error():
    """Test that empty destination raises validation error."""
    with pytest.raises(ValidationError):
        TravelRequestCreate(
            request_type="operations",
            project_id=None,
            destination="",  # Empty destination
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 5),
            purpose="Meeting",
            estimated_cost=Decimal("2000.00"),
            taccount_id=1,
        )


def test_empty_purpose_raises_error():
    """Test that empty purpose raises validation error."""
    with pytest.raises(ValidationError):
        TravelRequestCreate(
            request_type="operations",
            project_id=None,
            destination="Munich",
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 5),
            purpose="",  # Empty purpose
            estimated_cost=Decimal("2000.00"),
            taccount_id=1,
        )


def test_invalid_request_type_raises_error():
    """Test that invalid request_type raises validation error."""
    with pytest.raises(ValidationError):
        TravelRequestCreate(
            request_type="invalid_type",  # Invalid type
            project_id=None,
            destination="Vienna",
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 5),
            purpose="Conference",
            estimated_cost=Decimal("3500.00"),
            taccount_id=1,
        )
