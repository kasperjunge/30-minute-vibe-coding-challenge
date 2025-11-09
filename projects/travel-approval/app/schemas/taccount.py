"""T-Account schemas for validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TAccountCreate(BaseModel):
    """Schema for creating a T-account."""

    account_code: str = Field(min_length=1, max_length=50)
    account_name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None


class TAccountUpdate(BaseModel):
    """Schema for updating a T-account."""

    account_code: Optional[str] = Field(None, min_length=1, max_length=50)
    account_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class TAccountResponse(BaseModel):
    """Schema for T-account response."""

    id: int
    account_code: str
    account_name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
