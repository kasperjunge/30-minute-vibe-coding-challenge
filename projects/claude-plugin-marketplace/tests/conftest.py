import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.shared.database import Base, get_db
from main import create_app

# Import models to register them with Base before creating tables
from app.services.auth.models import User  # noqa: F401
from app.services.plugin.models import Plugin, PluginVersion  # noqa: F401


# Test database URL (temp file SQLite for connection sharing)
import tempfile
import os
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db")
TEST_DATABASE_URL = f"sqlite:///{_test_db_path}"


@pytest.fixture(scope="function")
def test_db():
    """
    Create a fresh database for each test.
    Uses in-memory SQLite for speed.
    """
    # Create test engine
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factory
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create session
    session = TestSessionLocal()
    
    # Store engine in session for client to use
    session._test_engine = engine
    session._test_session_factory = TestSessionLocal
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """
    FastAPI TestClient that uses test database.
    """
    # Create app
    from fastapi import FastAPI, Request, Depends
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from sqlalchemy.orm import Session
    from app.shared.config import settings
    
    # Create app without lifespan (no migrations in tests)
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug
    )
    
    # Add session middleware
    from starlette.middleware.sessions import SessionMiddleware
    app.add_middleware(
        SessionMiddleware,
        secret_key="test-secret-key",
        max_age=30 * 24 * 60 * 60,
        session_cookie="plugin_marketplace_session"
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Setup templates
    template_dirs = [
        "app/shared/templates",
        "app/services/auth/templates",
        "app/services/plugin/templates"
    ]
    templates = Jinja2Templates(directory=template_dirs)
    
    # Homepage route (replicate main.py logic for tests)
    @app.get("/", response_class=HTMLResponse)
    async def homepage(
        request: Request,
        page: int = 1,
        search: str = "",
        sort: str = "newest",
        db: Session = Depends(get_db)
    ):
        """Homepage with plugin listing, search, and pagination."""
        from app.services.plugin.models import Plugin, PluginVersion
        
        # Base query: published plugins only
        query = db.query(Plugin).filter(Plugin.is_published == True)
        
        # Apply search filter
        if search:
            query = query.filter(
                (Plugin.name.ilike(f"%{search}%")) |
                (Plugin.display_name.ilike(f"%{search}%")) |
                (Plugin.description.ilike(f"%{search}%"))
            )
        
        # Apply sorting
        if sort == "alphabetical":
            query = query.order_by(Plugin.name)
        else:  # newest (default)
            query = query.order_by(Plugin.created_at.desc())
        
        # Pagination
        per_page = 30
        total = query.count()
        total_pages = max(1, (total + per_page - 1) // per_page)
        
        # Ensure page is within bounds
        page = max(1, min(page, total_pages))
        
        offset = (page - 1) * per_page
        plugins = query.offset(offset).limit(per_page).all()
        
        # Get latest version and author for each plugin
        plugin_data = []
        for plugin in plugins:
            latest = db.query(PluginVersion).filter(
                PluginVersion.plugin_id == plugin.id,
                PluginVersion.is_latest == True
            ).first()
            plugin_data.append({
                "plugin": plugin,
                "latest_version": latest,
                "author": plugin.author
            })
        
        return templates.TemplateResponse("home.html", {
            "request": request,
            "settings": settings,
            "plugin_data": plugin_data,
            "page": page,
            "total_pages": total_pages,
            "search": search,
            "sort": sort,
            "total": total
        })
    
    # Error handlers
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    @app.exception_handler(500)
    async def server_error_handler(request: Request, exc):
        return templates.TemplateResponse("500.html", {"request": request}, status_code=500)
    
    
    # Include auth router
    from app.services.auth.routes import router as auth_router
    app.include_router(auth_router)
    
    # Include plugin router
    from app.services.plugin.routes import router as plugin_router
    app.include_router(plugin_router)
    
    # Override get_db dependency
    # Use the test engine to create new sessions for each request
    def override_get_db():
        db = test_db._test_session_factory()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    return TestClient(app)


@pytest.fixture
def db_session(test_db):
    """Alias for test_db to match common naming convention."""
    return test_db


@pytest.fixture
def authenticated_user(test_db, client):
    """
    Create an authenticated user and return user object with session cookie.
    """
    from app.services.auth.models import User
    from app.services.auth.utils import hash_password
    
    # Create user
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=hash_password("password123")
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Login to get session cookie
    response = client.post("/auth/login", data={
        "email": "testuser@example.com",
        "password": "password123"
    }, follow_redirects=False)
    
    # Extract session cookie
    session_cookie = {}
    for cookie in response.cookies.jar:
        session_cookie[cookie.name] = cookie.value
    
    return user, session_cookie

