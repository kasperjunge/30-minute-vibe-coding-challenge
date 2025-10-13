"""
Database connection and session management for Breath Training App
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database URL - SQLite with async support
DATABASE_URL = "sqlite+aiosqlite:///./breath_training.db"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging during development
    future=True,
)

# Create async session factory
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for all database models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize the database by creating all tables.
    This should be called once when the application starts.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
