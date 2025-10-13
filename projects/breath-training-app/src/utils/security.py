"""
Security utilities for password hashing and session management
"""

from datetime import datetime, timedelta
from typing import Any

from itsdangerous import BadSignature, SignatureExpired, TimestampSigner
from passlib.context import CryptContext

# Password hashing context using bcrypt with 12 rounds
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# Session signing key (should be from environment in production)
# For development, using a constant key
SECRET_KEY = "your-secret-key-change-in-production-use-env-var"
signer = TimestampSigner(SECRET_KEY)

# Session expiry: 7 days
SESSION_EXPIRY_DAYS = 7


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with 12 rounds.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_session_token(user_id: int) -> str:
    """
    Create a cryptographically signed session token for a user.

    Args:
        user_id: ID of the user to create session for

    Returns:
        Signed session token string
    """
    data = f"{user_id}"
    return signer.sign(data).decode()


def validate_session_token(token: str) -> int | None:
    """
    Validate a session token and extract user ID.

    Args:
        token: Session token to validate

    Returns:
        User ID if valid, None otherwise
    """
    try:
        # max_age is in seconds
        max_age = SESSION_EXPIRY_DAYS * 24 * 60 * 60
        unsigned = signer.unsign(token, max_age=max_age)
        user_id = int(unsigned.decode())
        return user_id
    except (BadSignature, SignatureExpired, ValueError):
        return None
