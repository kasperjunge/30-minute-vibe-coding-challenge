"""Report schemas for filtering and exporting travel requests."""

from datetime import date
from typing import Optional

from pydantic import BaseModel


class ReportFilters(BaseModel):
    """Schema for filtering travel request reports."""

    date_from: Optional[date] = None
    date_to: Optional[date] = None
    taccount_id: Optional[int] = None
    project_id: Optional[int] = None
    status: str = "approved"  # Default to approved status

    class Config:
        from_attributes = True
