import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from alembic import command
from alembic.config import Config

from app.shared.config import settings
from app.shared.middleware import UserContextMiddleware
from app.services.auth.routes import router as auth_router


# Setup template directories
template_dirs = [
    "app/shared/templates",
    "app/services/auth/templates"
]
templates = Jinja2Templates(directory=template_dirs)


def run_migrations():
    """Run Alembic migrations on startup (dev mode only)"""
    if settings.debug:
        print("Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Migrations complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    os.makedirs("data", exist_ok=True)
    run_migrations()
    yield
    # Shutdown (nothing to do)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan
    )
    
    # Add middleware (order matters - UserContext needs SessionMiddleware)
    app.add_middleware(UserContextMiddleware)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret_key,
        max_age=settings.session_max_age,
        session_cookie="app_session"
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Homepage route
    @app.get("/", response_class=HTMLResponse)
    async def homepage(request: Request):
        return templates.TemplateResponse("home.html", {"request": request, "settings": settings})
    
    # Error handlers
    @app.exception_handler(401)
    async def unauthorized_handler(request: Request, exc):
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/auth/login", status_code=307)
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return templates.TemplateResponse(
            "404.html", 
            {"request": request}, 
            status_code=404
        )
    
    @app.exception_handler(500)
    async def server_error_handler(request: Request, exc):
        return templates.TemplateResponse(
            "500.html", 
            {"request": request}, 
            status_code=500
        )
    
    # Include service routers
    app.include_router(auth_router)
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
