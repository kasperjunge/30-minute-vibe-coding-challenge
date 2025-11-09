"""Project schemas for validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProjectBase(BaseModel):
    """Base project schema."""

    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    team_lead_id: int


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    name: Optional[str] = None
    description: Optional[str] = None
    team_lead_id: Optional[int] = None


class ProjectResponse(ProjectBase):
    """Schema for project response."""

    id: int
    team_lead_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
