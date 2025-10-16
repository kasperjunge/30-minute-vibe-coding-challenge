"""Middleware for session management and request context.

This module uses Starlette's SessionMiddleware for signed cookie-based sessions.
The middleware is configured in main.py with a secret key and 30-day duration.

Session data is stored in signed cookies and includes:
- user_id: ID of authenticated user (if logged in)
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.services.auth.models import User
from app.shared.database import SessionLocal


class UserContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that loads the current user and attaches it to request.state.
    
    This allows templates to access the current user via request.state.user.
    """
    async def dispatch(self, request: Request, call_next):
        # Initialize user as None
        request.state.user = None
        
        # Try to get user_id from session
        user_id = request.session.get("user_id")
        if user_id:
            # Load user from database
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    request.state.user = user
            finally:
                db.close()
        
        response = await call_next(request)
        return response

