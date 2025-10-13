"""
Breath Training App - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Create FastAPI application instance
app = FastAPI(
    title="Breath Training App",
    description="A web-based breath training application for stress relief",
    version="0.1.0",
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="src/templates")


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the application is running.

    Returns:
        dict: Status message
    """
    return {"status": "ok"}
