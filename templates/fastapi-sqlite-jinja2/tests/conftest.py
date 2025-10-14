import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.shared.database import Base, get_db
from main import create_app

# Import models to register them with Base before creating tables
from app.services.todo.models import Todo  # noqa: F401


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
    from app.services.todo.routes import router as todo_router
    
    # Create app without lifespan (no migrations in tests)
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Setup templates
    template_dirs = ["app/shared/templates", "app/services/todo/templates"]
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
    
    # Include service routers
    app.include_router(todo_router)
    
    # Override get_db dependency
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    return TestClient(app)


@pytest.fixture
def sample_todo(test_db):
    """Create a sample todo for tests"""
    from app.services.todo.models import Todo
    
    todo = Todo(
        title="Test Todo",
        description="Test Description",
        completed=False
    )
    test_db.add(todo)
    test_db.commit()
    test_db.refresh(todo)
    
    return todo

