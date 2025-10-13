"""
Pytest fixtures for testing
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base


@pytest_asyncio.fixture
async def db_session():
    """
    Create a fresh in-memory database session for each test.
    """
    # Create in-memory SQLite database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", echo=False, future=True
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Yield session for test
    async with async_session_maker() as session:
        yield session

    # Cleanup
    await engine.dispose()
