from typing import Annotated
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.auth.models import User
from app.shared.database import get_db


async def get_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)]
) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user


async def require_auth(
    user: Annotated[User | None, Depends(get_current_user)]
) -> User:
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    return user


async def require_admin(
    user: Annotated[User, Depends(require_auth)]
) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    return user

