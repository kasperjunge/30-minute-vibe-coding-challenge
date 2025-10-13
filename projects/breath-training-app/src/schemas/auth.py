"""
Pydantic schemas for authentication requests and responses
"""

from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    """Request schema for user registration"""

    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password meets security requirements:
        - At least 8 characters
        - Contains at least one number
        - Contains at least one special character
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one number")

        special_chars = set("!@#$%^&*()_+-=[]{}|;:,.<>?")
        if not any(char in special_chars for char in v):
            raise ValueError("Password must contain at least one special character")

        return v


class LoginRequest(BaseModel):
    """Request schema for user login"""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response schema for user data"""

    id: int
    email: str
    created_at: str

    model_config = {"from_attributes": True}
