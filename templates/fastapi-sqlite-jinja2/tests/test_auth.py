import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.shared.database import Base, get_db
from app.services.auth.models import User
from app.services.auth.utils import hash_password
from unittest.mock import patch
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    # Patch SessionLocal in middleware to use test database
    with patch('app.shared.middleware.SessionLocal', TestingSessionLocal):
        yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def test_register_page_loads(client):
    response = client.get("/auth/register")
    assert response.status_code == 200
    assert b"Create Account" in response.content


def test_login_page_loads(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Login" in response.content


def test_register_success(client):
    response = client.post("/auth/register", data={
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_register_password_mismatch(client):
    response = client.post("/auth/register", data={
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "different"
    })
    assert response.status_code == 400
    assert b"Passwords do not match" in response.content


def test_register_short_password(client):
    response = client.post("/auth/register", data={
        "email": "test@example.com",
        "password": "123",
        "confirm_password": "123"
    })
    assert response.status_code == 400
    assert b"at least 6 characters" in response.content


def test_register_invalid_email(client):
    response = client.post("/auth/register", data={
        "email": "notanemail",
        "password": "password123",
        "confirm_password": "password123"
    })
    assert response.status_code == 400
    assert b"valid email" in response.content


def test_register_duplicate_email(client):
    client.post("/auth/register", data={
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    response = client.post("/auth/register", data={
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    assert response.status_code == 400
    assert b"already registered" in response.content


def test_login_success(client):
    client.post("/auth/register", data={
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "password123"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_login_wrong_password(client):
    client.post("/auth/register", data={
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert b"Invalid email or password" in response.content


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", data={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    assert response.status_code == 401
    assert b"Invalid email or password" in response.content


def test_logout(client):
    client.post("/auth/register", data={
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    response = client.post("/auth/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_profile_page(client):
    # Register and login first
    client.post("/auth/register", data={
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    
    # Now access profile (should work since we're logged in)
    response = client.get("/auth/profile/test@example.com")
    assert response.status_code == 200
    assert b"test@example.com" in response.content


def test_profile_not_found(client):
    # Register and login first
    client.post("/auth/register", data={
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    
    # Now try to access non-existent profile (should get 404 since we're authenticated)
    response = client.get("/auth/profile/nonexistent@example.com")
    assert response.status_code == 404


def test_require_auth_redirects(client):
    """Test that require_auth decorator redirects to login"""
    # Use auth profile as example of protected route
    response = client.get("/auth/profile/test@example.com", follow_redirects=False)
    
    # Should redirect to login
    assert response.status_code == 307
    assert "/auth/login" in response.headers["location"]


def test_require_admin_dependency(client):
    db = TestingSessionLocal()
    user = User(email="user@example.com", hashed_password=hash_password("password"), is_admin=False)
    db.add(user)
    db.commit()
    db.close()
    
    with client:
        client.post("/auth/login", data={
            "email": "user@example.com",
            "password": "password"
        })

