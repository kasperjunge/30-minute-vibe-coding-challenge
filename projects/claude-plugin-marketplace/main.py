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
from app.shared.database import get_db
from app.services.auth.routes import router as auth_router
from app.services.plugin.routes import router as plugin_router
from app.services.skill.routes import router as skill_router
from app.services.plugin.models import Plugin, PluginVersion
from sqlalchemy.orm import Session
from fastapi import Depends


# Setup template directories
template_dirs = [
    "app/shared/templates",
    "app/services/auth/templates",
    "app/services/plugin/templates"
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
    
    # Add user context middleware first (executes after SessionMiddleware due to reverse order)
    app.add_middleware(UserContextMiddleware)
    
    # Add session middleware for authentication (executes first due to reverse order)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret_key,
        max_age=settings.session_max_age,
        session_cookie="plugin_marketplace_session"
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Homepage route
    @app.get("/", response_class=HTMLResponse)
    async def homepage(
        request: Request,
        page: int = 1,
        search: str = "",
        sort: str = "newest",
        db: Session = Depends(get_db)
    ):
        """
        Homepage with plugin listing, search, and pagination.
        
        Query params:
        - page: Page number (default 1)
        - search: Search term for name/description
        - sort: "newest" or "alphabetical"
        """
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
    app.include_router(plugin_router)
    app.include_router(skill_router)
    
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
