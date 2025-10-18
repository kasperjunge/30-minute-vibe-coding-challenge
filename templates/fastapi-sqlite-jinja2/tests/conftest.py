import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.shared.database import Base, get_db
from main import create_app


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"


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
    
    # Bind the engine to Base metadata
    Base.metadata.bind = engine
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()
    
    #  Bind session to the engine explicitly
    session.bind = engine
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.bind = None


@pytest.fixture(scope="function")
def client(test_db):
    """
    FastAPI TestClient that uses test database.
    """
    # Create app
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from app.shared.config import settings
    
    # Create app without lifespan (no migrations in tests)
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug
    )
    
    # Add middleware
    from starlette.middleware.sessions import SessionMiddleware
    app.add_middleware(
        SessionMiddleware,
        secret_key="test-secret-key-for-testing",
        max_age=3600
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Setup templates
    template_dirs = ["app/shared/templates", "app/services/auth/templates"]
    templates = Jinja2Templates(directory=template_dirs)
    
    # Homepage route
    @app.get("/", response_class=HTMLResponse)
    async def homepage(request: Request):
        return templates.TemplateResponse("home.html", {"request": request, "settings": settings})
    
    # Error handlers
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    @app.exception_handler(500)
    async def server_error_handler(request: Request, exc):
        return templates.TemplateResponse("500.html", {"request": request}, status_code=500)
    
    # Include routers
    from app.services.auth.routes import router as auth_router
    app.include_router(auth_router)
    
    # Override get_db dependency
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    return TestClient(app)

