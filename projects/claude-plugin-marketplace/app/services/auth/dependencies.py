"""Authentication dependencies for protected routes."""
from typing import Annotated
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.auth.models import User
from app.shared.database import get_db


async def get_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)]
) -> User | None:
    """
    Get the currently authenticated user from session.
    
    Returns None if no user is logged in.
    
    Args:
        request: FastAPI request object with session data
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user


async def require_auth(
    user: Annotated[User | None, Depends(get_current_user)]
) -> User:
    """
    Require authentication for a route.
    
    Raises 401 if user is not authenticated.
    
    Args:
        user: Current user from get_current_user dependency
        
    Returns:
        User object
        
    Raises:
        HTTPException: 401 if not authenticated
    """
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    return user


async def require_admin(
    user: Annotated[User, Depends(require_auth)]
) -> User:
    """
    Require admin privileges for a route.
    
    Raises 403 if user is not an admin.
    
    Args:
        user: Current authenticated user
        
    Returns:
        User object (guaranteed to be admin)
        
    Raises:
        HTTPException: 403 if not admin
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    return user

