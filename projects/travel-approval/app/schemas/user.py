"""User schemas for validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str
    role: str


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str
    manager_id: Optional[int] = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    manager_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Schema for login request."""

    email: EmailStr
    password: str
