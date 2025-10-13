"""
Tests for authentication service
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import auth_service
from src.utils.security import create_session_token, validate_session_token


@pytest.mark.asyncio
async def test_register_user_success(db_session: AsyncSession):
    """Test successful user registration"""
    email = "test@example.com"
    password = "SecurePass123!"

    user = await auth_service.register_user(db_session, email, password)

    assert user.id is not None
    assert user.email == email
    assert user.password_hash != password  # Password should be hashed
    assert user.password_hash.startswith("$2b$")  # bcrypt hash format


@pytest.mark.asyncio
async def test_register_user_duplicate_email(db_session: AsyncSession):
    """Test registration with duplicate email fails"""
    email = "duplicate@example.com"
    password = "SecurePass123!"

    # Register first user
    await auth_service.register_user(db_session, email, password)

    # Try to register with same email
    with pytest.raises(ValueError, match="Email already registered"):
        await auth_service.register_user(db_session, email, password)


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session: AsyncSession):
    """Test successful user authentication"""
    email = "auth@example.com"
    password = "SecurePass123!"

    # Register user
    registered_user = await auth_service.register_user(db_session, email, password)

    # Authenticate user
    authenticated_user = await auth_service.authenticate_user(
        db_session, email, password
    )

    assert authenticated_user is not None
    assert authenticated_user.id == registered_user.id
    assert authenticated_user.email == email


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db_session: AsyncSession):
    """Test authentication with incorrect password fails"""
    email = "wrongpass@example.com"
    password = "SecurePass123!"

    # Register user
    await auth_service.register_user(db_session, email, password)

    # Try to authenticate with wrong password
    authenticated_user = await auth_service.authenticate_user(
        db_session, email, "WrongPassword123!"
    )

    assert authenticated_user is None


@pytest.mark.asyncio
async def test_authenticate_user_nonexistent(db_session: AsyncSession):
    """Test authentication with non-existent email fails"""
    authenticated_user = await auth_service.authenticate_user(
        db_session, "nonexistent@example.com", "SomePassword123!"
    )

    assert authenticated_user is None


def test_create_session_token():
    """Test session token creation"""
    user_id = 42
    token = create_session_token(user_id)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_validate_session_token():
    """Test session token validation"""
    user_id = 42
    token = create_session_token(user_id)

    validated_user_id = validate_session_token(token)

    assert validated_user_id == user_id


def test_validate_session_token_invalid():
    """Test validation of invalid session token"""
    invalid_token = "invalid.token.string"

    validated_user_id = validate_session_token(invalid_token)

    assert validated_user_id is None


@pytest.mark.asyncio
async def test_validate_session_with_database(db_session: AsyncSession):
    """Test full session validation with database lookup"""
    email = "session@example.com"
    password = "SecurePass123!"

    # Register user
    user = await auth_service.register_user(db_session, email, password)

    # Create session
    token = auth_service.create_session(user.id)

    # Validate session
    validated_user = await auth_service.validate_session(db_session, token)

    assert validated_user is not None
    assert validated_user.id == user.id
    assert validated_user.email == email


@pytest.mark.asyncio
async def test_validate_session_invalid_token(db_session: AsyncSession):
    """Test session validation with invalid token"""
    invalid_token = "invalid.token.string"

    validated_user = await auth_service.validate_session(db_session, invalid_token)

    assert validated_user is None


@pytest.mark.asyncio
async def test_user_stats_created_on_registration(db_session: AsyncSession):
    """Test that UserStats is created when user registers"""
    email = "stats@example.com"
    password = "SecurePass123!"

    user = await auth_service.register_user(db_session, email, password)

    # Refresh to load relationships
    await db_session.refresh(user, ["stats"])

    assert user.stats is not None
    assert user.stats.total_sessions == 0
    assert user.stats.total_minutes == 0
    assert user.stats.current_streak == 0


@pytest.mark.asyncio
async def test_user_preferences_created_on_registration(db_session: AsyncSession):
    """Test that UserPreference is created when user registers"""
    email = "prefs@example.com"
    password = "SecurePass123!"

    user = await auth_service.register_user(db_session, email, password)

    # Refresh to load relationships
    await db_session.refresh(user, ["preferences"])

    assert user.preferences is not None
    assert user.preferences.audio_enabled is True
    assert user.preferences.reminder_enabled is False
    assert user.preferences.has_completed_onboarding is False
