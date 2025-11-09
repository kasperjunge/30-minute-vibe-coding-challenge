"""FastAPI application initialization and configuration."""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Set up logging to both file and stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Travel approval system for managing pre-trip approvals",
    version="0.1.0",
    debug=settings.debug,
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def root():
    """Root endpoint - redirect to login or dashboard."""
    return {
        "message": "Travel Approval System API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Exception handlers
@app.exception_handler(404)
@app.exception_handler(StarletteHTTPException)
async def not_found_handler(request: Request, exc: Exception):
    """Handle 404 Not Found errors."""
    if isinstance(exc, StarletteHTTPException) and exc.status_code != 404:
        # Re-raise if not a 404
        raise exc

    logger.warning(f"404 Not Found: {request.url}")

    # Check if it's an API request (for future JSON API endpoints)
    if request.url.path.startswith("/api/"):
        return {"detail": "Not found"}

    return templates.TemplateResponse(
        request,
        "404.html",
        {"request": request},
        status_code=404,
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    """Handle 500 Internal Server Error."""
    logger.error(f"Server error on {request.url}: {exc}", exc_info=True)

    # Check if it's an API request
    if request.url.path.startswith("/api/"):
        return {"detail": "Internal server error"}

    return templates.TemplateResponse(
        request,
        "500.html",
        {"request": request},
        status_code=500,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException errors."""
    logger.warning(f"HTTP {exc.status_code} on {request.url}: {exc.detail}")

    # For specific error codes, use custom templates
    if exc.status_code == 404:
        return await not_found_handler(request, exc)
    elif exc.status_code == 500:
        return await server_error_handler(request, exc)

    # For other HTTP exceptions, re-raise to let FastAPI handle them
    raise exc


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unexpected errors."""
    logger.error(f"Unexpected error on {request.url}: {exc}", exc_info=True)

    return templates.TemplateResponse(
        request,
        "500.html",
        {"request": request},
        status_code=500,
    )


# Import and include routers
from app.routers import admin, approvals, auth, dashboard, notifications, reports, travel_requests

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(travel_requests.router)
app.include_router(approvals.router)
app.include_router(notifications.router)
app.include_router(reports.router)
app.include_router(admin.router)
