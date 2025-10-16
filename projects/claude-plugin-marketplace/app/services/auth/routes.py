"""Authentication routes for registration, login, and logout."""
from typing import Annotated
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.auth.models import User
from app.services.auth.utils import hash_password, verify_password
from app.services.auth.dependencies import get_current_user
from app.shared.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
# Templates are imported from shared config that includes all template directories
template_dirs = [
    "app/shared/templates",
    "app/services/auth/templates"
]
templates = Jinja2Templates(directory=template_dirs)


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    """Display registration form."""
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": None
    })


@router.post("/register")
async def register(
    request: Request,
    username: Annotated[str, Form()],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    confirm_password: Annotated[str, Form()],
    db: Annotated[Session, Depends(get_db)]
):
    """Handle user registration."""
    # Validate inputs
    if not username or len(username) < 3:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Username must be at least 3 characters long"
        }, status_code=400)
    
    if not email or "@" not in email:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Please enter a valid email address"
        }, status_code=400)
    
    if not password or len(password) < 6:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Password must be at least 6 characters long"
        }, status_code=400)
    
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Passwords do not match"
        }, status_code=400)
    
    # Hash password
    hashed_password = hash_password(password)
    
    # Create user
    try:
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Set session
        request.session["user_id"] = user.id
        
        # Redirect to homepage
        return RedirectResponse("/", status_code=303)
        
    except IntegrityError:
        db.rollback()
        # Check which field caused the error
        existing_email = db.query(User).filter(User.email == email).first()
        existing_username = db.query(User).filter(User.username == username).first()
        
        if existing_email:
            error_msg = "Email address is already registered"
        elif existing_username:
            error_msg = "Username is already taken"
        else:
            error_msg = "Registration failed. Please try again"
        
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": error_msg
        }, status_code=400)


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """Display login form."""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": None
    })


@router.post("/login")
async def login(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Annotated[Session, Depends(get_db)]
):
    """Handle user login."""
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    
    # Verify credentials
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid email or password"
        }, status_code=401)
    
    # Set session
    request.session["user_id"] = user.id
    
    # Redirect to homepage
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
async def logout(request: Request):
    """Handle user logout."""
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@router.get("/users/@{username}", response_class=HTMLResponse)
async def user_profile(
    username: str,
    request: Request,
    db: Annotated[Session, Depends(get_db)]
):
    """Display user profile page."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's plugins (placeholder for now - will be implemented in Phase 2)
    plugins = []
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile_user": user,
        "plugins": plugins
    })

