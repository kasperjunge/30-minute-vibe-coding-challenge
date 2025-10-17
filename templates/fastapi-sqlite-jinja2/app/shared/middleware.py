from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.services.auth.models import User
from app.shared.database import SessionLocal


class UserContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        
        user_id = request.session.get("user_id")
        if user_id:
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    request.state.user = user
            finally:
                db.close()
        
        response = await call_next(request)
        return response

