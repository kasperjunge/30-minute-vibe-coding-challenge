"""FastAPI dependencies for authentication and authorization."""

from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.session import session_manager
from app.database import get_db
from app.models.user import User


def get_unread_count(current_user: User, db: Session) -> int:
    """
    Get the count of unread notifications for a user.

    Args:
        current_user: The current authenticated user
        db: Database session

    Returns:
        Count of unread notifications
    """
    from app.services.notification_service import get_unread_notifications

    unread_notifications = get_unread_notifications(current_user, db)
    return len(unread_notifications)


def get_current_user(
    session: Optional[str] = Cookie(None, alias="travel_approval_session"),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Get the current authenticated user from session cookie.

    Args:
        session: Session cookie value
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if not session:
        return None

    user_id = session_manager.verify_session(session)
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    return user


def require_auth(current_user: Optional[User] = Depends(get_current_user)) -> User:
    """
    Dependency that requires authentication.

    Args:
        current_user: Current user from session

    Returns:
        User object

    Raises:
        HTTPException: 401 if not authenticated
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return current_user


def require_role(*allowed_roles: str):
    """
    Dependency factory that requires specific roles.

    Args:
        *allowed_roles: Roles that are allowed to access

    Returns:
        Dependency function

    Example:
        @router.get("/admin")
        async def admin_page(user: User = Depends(require_role("admin"))):
            ...
    """

    def role_checker(current_user: User = Depends(require_auth)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker
