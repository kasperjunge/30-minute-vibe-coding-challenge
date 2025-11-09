"""Pytest fixtures for testing."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User, TravelRequest, Project, TAccount, Notification


# Use in-memory SQLite for testing with StaticPool to keep same connection
TEST_DATABASE_URL = "sqlite:///:memory:"

# Global test engine and session maker for sharing across TestClient
test_engine = None
TestSessionLocal = None


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    global test_engine, TestSessionLocal

    # Use StaticPool to keep the same connection across all threads
    # This is important for in-memory SQLite databases in tests
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    session = TestSessionLocal()

    # Override the get_db dependency to use our test session
    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield session
    finally:
        # Clean up
        app.dependency_overrides.clear()
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


@pytest.fixture
def sample_manager(db_session):
    """Create a sample manager user."""
    manager = User(
        email="manager@test.com",
        password_hash="hashed_password",
        full_name="Test Manager",
        role="manager",
        is_active=True
    )
    db_session.add(manager)
    db_session.commit()
    db_session.refresh(manager)
    return manager


@pytest.fixture
def sample_employee(db_session, sample_manager):
    """Create a sample employee user."""
    employee = User(
        email="employee@test.com",
        password_hash="hashed_password",
        full_name="Test Employee",
        role="employee",
        manager_id=sample_manager.id,
        is_active=True
    )
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    return employee


@pytest.fixture
def sample_taccount(db_session):
    """Create a sample T-account."""
    taccount = TAccount(
        account_code="T-1234",
        account_name="Test Account",
        description="Test T-account",
        is_active=True
    )
    db_session.add(taccount)
    db_session.commit()
    db_session.refresh(taccount)
    return taccount


@pytest.fixture
def sample_project(db_session, sample_manager):
    """Create a sample project."""
    project = Project(
        name="Test Project",
        description="Test project description",
        team_lead_id=sample_manager.id,
        is_active=True
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def sample_admin(db_session):
    """Create a sample admin user."""
    from app.auth.password import hash_password

    admin = User(
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        full_name="Test Admin",
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def client(db_session):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def admin_user_session(db_session, sample_admin):
    """Create session cookies for admin user."""
    from app.auth.session import session_manager

    session_token = session_manager.create_session(sample_admin.id)
    return {"travel_approval_session": session_token}


@pytest.fixture
def employee_user_session(db_session, sample_employee):
    """Create session cookies for employee user."""
    from app.auth.session import session_manager

    session_token = session_manager.create_session(sample_employee.id)
    return {"travel_approval_session": session_token}
