"""
Tests for database models and connections
"""

import pytest
import pytest_asyncio
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, init_db
from src.models import User, BreathingPattern, Session, UserStats, UserPreference


@pytest_asyncio.fixture
async def db_engine():
    """
    Create an in-memory SQLite database engine for testing.
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """
    Create a database session for testing.
    """
    async_session_maker = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session


@pytest.mark.asyncio
async def test_database_initialization(db_engine):
    """
    Test that database tables are created successfully.
    """
    async with db_engine.begin() as conn:
        # Check that tables exist by querying metadata
        result = await conn.run_sync(
            lambda sync_conn: Base.metadata.tables.keys()
        )
        assert "users" in result
        assert "breathing_patterns" in result
        assert "sessions" in result
        assert "user_stats" in result
        assert "user_preferences" in result


@pytest.mark.asyncio
async def test_create_user(db_session):
    """
    Test creating a user in the database.
    """
    user = User(
        email="test@example.com",
        password_hash="hashed_password_123"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.password_hash == "hashed_password_123"
    assert user.created_at is not None
    assert user.updated_at is not None


@pytest.mark.asyncio
async def test_create_breathing_pattern(db_session):
    """
    Test creating a breathing pattern.
    """
    pattern = BreathingPattern(
        name="Box Breathing",
        slug="box-breathing",
        description="Equal breathing for calm focus",
        inhale_duration=4,
        inhale_hold_duration=4,
        exhale_duration=4,
        exhale_hold_duration=4,
        is_preset=True
    )
    db_session.add(pattern)
    await db_session.commit()
    await db_session.refresh(pattern)

    assert pattern.id is not None
    assert pattern.name == "Box Breathing"
    assert pattern.slug == "box-breathing"
    assert pattern.inhale_duration == 4
    assert pattern.is_preset is True


@pytest.mark.asyncio
async def test_create_session(db_session):
    """
    Test creating a breathing session with relationships.
    """
    # Create user
    user = User(email="session@example.com", password_hash="hash123")
    db_session.add(user)

    # Create pattern
    pattern = BreathingPattern(
        name="Test Pattern",
        slug="test-pattern",
        description="Test",
        inhale_duration=4,
        inhale_hold_duration=0,
        exhale_duration=4,
        exhale_hold_duration=0,
        is_preset=True
    )
    db_session.add(pattern)
    await db_session.commit()

    # Create session
    session = Session(
        user_id=user.id,
        pattern_id=pattern.id,
        target_duration=300,
        actual_duration=300,
        completed_at=datetime.utcnow(),
        is_completed=True,
        timezone="UTC"
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    assert session.id is not None
    assert session.user_id == user.id
    assert session.pattern_id == pattern.id
    assert session.target_duration == 300
    assert session.is_completed is True


@pytest.mark.asyncio
async def test_user_stats_relationship(db_session):
    """
    Test user statistics relationship with user.
    """
    # Create user
    user = User(email="stats@example.com", password_hash="hash123")
    db_session.add(user)
    await db_session.commit()

    # Create user stats
    stats = UserStats(
        user_id=user.id,
        total_sessions=5,
        total_minutes=25,
        current_streak=3,
        longest_streak=7,
        last_practice_date=date.today()
    )
    db_session.add(stats)
    await db_session.commit()

    # Refresh and check relationship
    await db_session.refresh(user)
    assert user.stats is not None
    assert user.stats.total_sessions == 5
    assert user.stats.current_streak == 3


@pytest.mark.asyncio
async def test_user_preferences_relationship(db_session):
    """
    Test user preferences relationship with user.
    """
    # Create user
    user = User(email="prefs@example.com", password_hash="hash123")
    db_session.add(user)
    await db_session.commit()

    # Create preferences
    prefs = UserPreference(
        user_id=user.id,
        audio_enabled=False,
        reminder_enabled=True,
        has_completed_onboarding=True
    )
    db_session.add(prefs)
    await db_session.commit()

    # Refresh and check relationship
    await db_session.refresh(user)
    assert user.preferences is not None
    assert user.preferences.audio_enabled is False
    assert user.preferences.has_completed_onboarding is True


@pytest.mark.asyncio
async def test_custom_pattern_relationship(db_session):
    """
    Test custom breathing pattern relationship with user.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    # Create user
    user = User(email="custom@example.com", password_hash="hash123")
    db_session.add(user)
    await db_session.commit()

    # Create custom pattern for user
    custom_pattern = BreathingPattern(
        name="My Custom Pattern",
        slug="my-custom",
        description="Custom breathing pattern",
        inhale_duration=5,
        inhale_hold_duration=2,
        exhale_duration=7,
        exhale_hold_duration=1,
        is_preset=False,
        user_id=user.id
    )
    db_session.add(custom_pattern)
    await db_session.commit()

    # Query user with eagerly loaded custom_patterns
    result = await db_session.execute(
        select(User).where(User.id == user.id).options(selectinload(User.custom_patterns))
    )
    user_with_patterns = result.scalar_one()

    assert len(user_with_patterns.custom_patterns) == 1
    assert user_with_patterns.custom_patterns[0].name == "My Custom Pattern"
    assert user_with_patterns.custom_patterns[0].is_preset is False
