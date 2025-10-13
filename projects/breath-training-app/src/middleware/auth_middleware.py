"""
Authentication middleware for validating sessions
"""

from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.database import async_session_maker
from src.services.auth_service import validate_session

# Routes that don't require authentication
PUBLIC_ROUTES = {
    "/",
    "/login",
    "/register",
    "/health",
    "/static",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate user sessions"""

    async def dispatch(self, request: Request, call_next):
        # Check if route is public
        path = request.url.path

        # Allow public routes and static files
        if path in PUBLIC_ROUTES or path.startswith("/static/"):
            return await call_next(request)

        # Check for session cookie
        session_token = request.cookies.get("session")

        if not session_token:
            # No session cookie, redirect to login
            if path.startswith("/api/"):
                # For API routes, return 401
                return Response(status_code=401, content="Unauthorized")
            else:
                # For page routes, redirect to login
                return RedirectResponse(url="/login", status_code=303)

        # Validate session
        async with async_session_maker() as db:
            user = await validate_session(db, session_token)

        if not user:
            # Invalid session, redirect to login
            if path.startswith("/api/"):
                return Response(status_code=401, content="Unauthorized")
            else:
                return RedirectResponse(url="/login", status_code=303)

        # Valid session, attach user to request state
        request.state.user = user

        return await call_next(request)
