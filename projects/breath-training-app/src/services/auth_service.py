"""
Authentication service for user registration, login, and session management
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.user_preference import UserPreference
from src.models.user_stats import UserStats
from src.utils.security import (
    create_session_token,
    hash_password,
    validate_session_token,
    verify_password,
)


async def register_user(db: AsyncSession, email: str, password: str) -> User:
    """
    Register a new user with email and password.

    Args:
        db: Database session
        email: User email address
        password: Plain text password

    Returns:
        Created User object

    Raises:
        ValueError: If email already exists
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ValueError("Email already registered")

    # Hash password
    password_hash = hash_password(password)

    # Create user
    user = User(email=email, password_hash=password_hash)
    db.add(user)
    await db.flush()  # Flush to get user.id

    # Create associated UserStats record
    user_stats = UserStats(user_id=user.id)
    db.add(user_stats)

    # Create associated UserPreference record
    user_pref = UserPreference(user_id=user.id)
    db.add(user_pref)

    await db.commit()
    await db.refresh(user)

    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    """
    Authenticate a user with email and password.

    Args:
        db: Database session
        email: User email address
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Verify password
    if not verify_password(password, user.password_hash):
        return None

    return user


def create_session(user_id: int) -> str:
    """
    Create a session token for a user.

    Args:
        user_id: ID of the user

    Returns:
        Session token string
    """
    return create_session_token(user_id)


async def validate_session(db: AsyncSession, token: str) -> User | None:
    """
    Validate a session token and return the user.

    Args:
        db: Database session
        token: Session token to validate

    Returns:
        User object if session valid, None otherwise
    """
    user_id = validate_session_token(token)

    if user_id is None:
        return None

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    return user


async def delete_session(token: str) -> None:
    """
    Delete a session (logout).

    For session-based auth with signed cookies, we don't need to do anything
    server-side. The client will delete the cookie.

    Args:
        token: Session token to delete
    """
    # With signed cookies, we don't maintain server-side session storage
    # The token itself contains all needed information
    # Logout is handled by clearing the cookie on the client side
    pass
