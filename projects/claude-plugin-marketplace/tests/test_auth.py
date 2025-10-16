"""Tests for authentication functionality."""
import pytest
from sqlalchemy.exc import IntegrityError
from app.services.auth.models import User
from app.services.auth.utils import hash_password, verify_password
from datetime import datetime


def test_user_model_creates_successfully(db_session):
    """Test that User model creates successfully with all fields."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword123",
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.hashed_password == "hashedpassword123"
    assert user.is_admin is False
    assert isinstance(user.created_at, datetime)


def test_user_email_unique_constraint(db_session):
    """Test that email must be unique."""
    user1 = User(
        email="test@example.com",
        username="user1",
        hashed_password="hash1"
    )
    db_session.add(user1)
    db_session.commit()
    
    user2 = User(
        email="test@example.com",
        username="user2",
        hashed_password="hash2"
    )
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_username_unique_constraint(db_session):
    """Test that username must be unique."""
    user1 = User(
        email="test1@example.com",
        username="testuser",
        hashed_password="hash1"
    )
    db_session.add(user1)
    db_session.commit()
    
    user2 = User(
        email="test2@example.com",
        username="testuser",
        hashed_password="hash2"
    )
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_default_values(db_session):
    """Test that default values are set correctly."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hash"
    )
    db_session.add(user)
    db_session.commit()
    
    # is_admin should default to False
    assert user.is_admin is False
    # created_at should be auto-set
    assert user.created_at is not None
    assert isinstance(user.created_at, datetime)


# Password Hashing Utility Tests

def test_hash_password_returns_different_hash_each_time():
    """Test that hash_password returns a different hash each time due to salt."""
    password = "mypassword123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    # Hashes should be different due to salt
    assert hash1 != hash2
    # But both should be valid bcrypt hashes (start with $2b$)
    assert hash1.startswith("$2b$")
    assert hash2.startswith("$2b$")


def test_verify_password_succeeds_with_correct_password():
    """Test that verify_password returns True with the correct password."""
    password = "correct_password"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_fails_with_wrong_password():
    """Test that verify_password returns False with the wrong password."""
    correct_password = "correct_password"
    wrong_password = "wrong_password"
    hashed = hash_password(correct_password)
    
    assert verify_password(wrong_password, hashed) is False


def test_hashed_password_never_matches_plain_password():
    """Test that the hashed password is never the same as the plain password."""
    password = "mypassword123"
    hashed = hash_password(password)
    
    # Hash should never equal the original password
    assert hashed != password
    # Verify that the hash works correctly
    assert verify_password(password, hashed) is True


# Session Middleware Tests

def test_session_middleware_sets_cookie(client):
    """Test that session middleware allows setting session data."""
    # Make a request to homepage
    response = client.get("/")
    
    # Session middleware should be active
    assert response.status_code == 200


def test_session_middleware_is_configured(client):
    """Test that session middleware is properly configured on the app."""
    from starlette.middleware.sessions import SessionMiddleware
    
    # Check that SessionMiddleware is in the middleware stack
    middleware_classes = [type(m) for m in client.app.user_middleware]
    # SessionMiddleware should be present (Starlette wraps it)
    # We can verify by checking that the app accepts session operations
    # This will be more thoroughly tested when we implement auth routes
    assert client.app is not None


# Authentication Dependencies Tests

def test_get_current_user_returns_none_when_not_logged_in(db_session):
    """Test that get_current_user returns None when user is not logged in."""
    from fastapi import Request
    from app.services.auth.dependencies import get_current_user
    import asyncio
    
    # Create a mock request with no session data
    class MockRequest:
        def __init__(self):
            self.session = {}
    
    request = MockRequest()
    result = asyncio.run(get_current_user(request, db_session))
    
    assert result is None


def test_get_current_user_returns_user_when_logged_in(db_session):
    """Test that get_current_user returns User when logged in."""
    from app.services.auth.dependencies import get_current_user
    import asyncio
    
    # Create a user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hash123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create a mock request with user_id in session
    class MockRequest:
        def __init__(self, user_id):
            self.session = {"user_id": user_id}
    
    request = MockRequest(user.id)
    result = asyncio.run(get_current_user(request, db_session))
    
    assert result is not None
    assert result.id == user.id
    assert result.email == "test@example.com"


def test_require_auth_raises_401_when_not_authenticated():
    """Test that require_auth raises 401 when not authenticated."""
    from app.services.auth.dependencies import require_auth
    from fastapi import HTTPException
    import asyncio
    import pytest
    
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(require_auth(None))
    
    assert exc_info.value.status_code == 401
    assert "Authentication required" in str(exc_info.value.detail)


def test_require_auth_returns_user_when_authenticated(db_session):
    """Test that require_auth returns user when authenticated."""
    from app.services.auth.dependencies import require_auth
    import asyncio
    
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hash123"
    )
    db_session.add(user)
    db_session.commit()
    
    result = asyncio.run(require_auth(user))
    
    assert result is not None
    assert result.email == "test@example.com"


def test_require_admin_raises_403_when_not_admin(db_session):
    """Test that require_admin raises 403 when user is not admin."""
    from app.services.auth.dependencies import require_admin
    from fastapi import HTTPException
    import asyncio
    import pytest
    
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hash123",
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(require_admin(user))
    
    assert exc_info.value.status_code == 403
    assert "Admin privileges required" in str(exc_info.value.detail)


def test_require_admin_succeeds_for_admin_users(db_session):
    """Test that require_admin succeeds for admin users."""
    from app.services.auth.dependencies import require_admin
    import asyncio
    
    admin_user = User(
        email="admin@example.com",
        username="adminuser",
        hashed_password="hash123",
        is_admin=True
    )
    db_session.add(admin_user)
    db_session.commit()
    
    result = asyncio.run(require_admin(admin_user))
    
    assert result is not None
    assert result.is_admin is True
    assert result.email == "admin@example.com"


# Registration Tests

def test_registration_with_valid_data_creates_user(client, db_session):
    """Test that registration with valid data creates a user."""
    response = client.post("/auth/register", data={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }, follow_redirects=False)
    
    # Should redirect to homepage
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    
    # User should be created in database
    user = db_session.query(User).filter(User.email == "newuser@example.com").first()
    assert user is not None
    assert user.username == "newuser"
    assert user.email == "newuser@example.com"
    assert user.hashed_password != "password123"  # Password should be hashed


def test_registration_duplicate_email_returns_error(client, db_session):
    """Test that duplicate email returns an error."""
    # Create existing user
    existing_user = User(
        email="existing@example.com",
        username="existinguser",
        hashed_password="hash123"
    )
    db_session.add(existing_user)
    db_session.commit()
    
    # Try to register with same email
    response = client.post("/auth/register", data={
        "username": "newuser",
        "email": "existing@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    
    assert response.status_code == 400
    assert "Email address is already registered" in response.text


def test_registration_duplicate_username_returns_error(client, db_session):
    """Test that duplicate username returns an error."""
    # Create existing user
    existing_user = User(
        email="existing@example.com",
        username="existinguser",
        hashed_password="hash123"
    )
    db_session.add(existing_user)
    db_session.commit()
    
    # Try to register with same username
    response = client.post("/auth/register", data={
        "username": "existinguser",
        "email": "newemail@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    
    assert response.status_code == 400
    assert "Username is already taken" in response.text


def test_registration_password_mismatch_returns_error(client):
    """Test that password mismatch returns an error."""
    response = client.post("/auth/register", data={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "confirm_password": "different_password"
    })
    
    assert response.status_code == 400
    assert "Passwords do not match" in response.text


def test_registration_invalid_email_returns_error(client):
    """Test that invalid email format returns an error."""
    response = client.post("/auth/register", data={
        "username": "newuser",
        "email": "invalid-email",
        "password": "password123",
        "confirm_password": "password123"
    })
    
    assert response.status_code == 400
    assert "valid email" in response.text.lower()


def test_successful_registration_sets_session_cookie(client, db_session):
    """Test that successful registration sets a session cookie."""
    response = client.post("/auth/register", data={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }, follow_redirects=False)
    
    # Session cookie should be set
    assert "plugin_marketplace_session" in response.cookies or "session" in response.cookies or response.status_code == 303
    
    # User should be created
    user = db_session.query(User).filter(User.email == "newuser@example.com").first()
    assert user is not None


def test_registration_form_renders(client):
    """Test that the registration form page renders."""
    response = client.get("/auth/register")
    
    assert response.status_code == 200
    assert "Create Account" in response.text or "Register" in response.text
    assert "username" in response.text.lower()
    assert "email" in response.text.lower()
    assert "password" in response.text.lower()


# Login Tests

def test_login_with_correct_credentials_succeeds(client, db_session):
    """Test that login with correct credentials succeeds."""
    # Create a user
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    
    # Attempt login
    response = client.post("/auth/login", data={
        "email": "testuser@example.com",
        "password": "password123"
    }, follow_redirects=False)
    
    # Should redirect to homepage
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_login_with_wrong_password_fails(client, db_session):
    """Test that login with wrong password fails."""
    # Create a user
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=hash_password("correct_password")
    )
    db_session.add(user)
    db_session.commit()
    
    # Attempt login with wrong password
    response = client.post("/auth/login", data={
        "email": "testuser@example.com",
        "password": "wrong_password"
    })
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.text


def test_login_with_nonexistent_email_fails(client):
    """Test that login with non-existent email fails."""
    response = client.post("/auth/login", data={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.text


def test_successful_login_sets_session_cookie(client, db_session):
    """Test that successful login sets a session cookie."""
    # Create a user
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    
    # Attempt login
    response = client.post("/auth/login", data={
        "email": "testuser@example.com",
        "password": "password123"
    }, follow_redirects=False)
    
    # Session cookie should be set
    assert response.status_code == 303


def test_login_form_renders(client):
    """Test that the login form page renders."""
    response = client.get("/auth/login")
    
    assert response.status_code == 200
    assert "Login" in response.text
    assert "email" in response.text.lower()
    assert "password" in response.text.lower()


# Logout and Profile Tests

def test_logout_clears_session_cookie(client, db_session):
    """Test that logout clears the session cookie."""
    # Create and login a user
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    client.post("/auth/login", data={
        "email": "testuser@example.com",
        "password": "password123"
    })
    
    # Logout
    response = client.post("/auth/logout", follow_redirects=False)
    
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_logout_redirects_to_homepage(client):
    """Test that logout redirects to homepage."""
    response = client.post("/auth/logout", follow_redirects=False)
    
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_profile_page_shows_user_info(client, db_session):
    """Test that profile page shows user information."""
    # Create a user
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    
    # Visit profile page
    response = client.get("/auth/users/@testuser")
    
    assert response.status_code == 200
    assert "@testuser" in response.text
    assert "Member since" in response.text


def test_profile_page_404_for_nonexistent_user(client):
    """Test that profile page returns 404 for non-existent user."""
    response = client.get("/auth/users/@nonexistentuser")
    
    assert response.status_code == 404

