"""Travel request schemas for validation."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class TravelRequestCreate(BaseModel):
    """Schema for creating a travel request."""

    request_type: Literal["operations", "project"]
    project_id: Optional[int] = None
    destination: str = Field(min_length=1, max_length=255)
    start_date: date
    end_date: date
    purpose: str = Field(min_length=1)
    estimated_cost: Decimal = Field(gt=0, decimal_places=2)
    taccount_id: int

    @field_validator("estimated_cost")
    @classmethod
    def validate_positive_cost(cls, v: Decimal) -> Decimal:
        """Validate that estimated cost is positive."""
        if v <= 0:
            raise ValueError("Estimated cost must be greater than 0")
        return v

    @model_validator(mode="after")
    def validate_dates_and_project(self):
        """Validate end date is after start date and project_id is set for project requests."""
        # Validate end_date >= start_date
        if self.end_date < self.start_date:
            raise ValueError("End date must be on or after start date")

        # Validate project_id is set for project requests
        if self.request_type == "project" and self.project_id is None:
            raise ValueError("Project ID is required for project-type requests")

        # Validate project_id is not set for operations requests
        if self.request_type == "operations" and self.project_id is not None:
            raise ValueError("Project ID should not be set for operations-type requests")

        return self


class TravelRequestUpdate(BaseModel):
    """Schema for updating a travel request (limited fields)."""

    destination: Optional[str] = Field(None, min_length=1, max_length=255)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    purpose: Optional[str] = Field(None, min_length=1)
    estimated_cost: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    taccount_id: Optional[int] = None


class TravelRequestResponse(BaseModel):
    """Schema for travel request response."""

    id: int
    requester_id: int
    request_type: str
    project_id: Optional[int] = None
    destination: str
    start_date: date
    end_date: date
    purpose: str
    estimated_cost: Decimal
    taccount_id: int
    status: str
    approver_id: Optional[int] = None
    approval_date: Optional[datetime] = None
    approval_comments: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
