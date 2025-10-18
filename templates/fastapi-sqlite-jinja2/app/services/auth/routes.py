from typing import Annotated
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.auth.models import User
from app.services.auth.utils import hash_password, verify_password
from app.services.auth.dependencies import get_current_user, require_auth
from app.shared.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
template_dirs = [
    "app/shared/templates",
    "app/services/auth/templates"
]
templates = Jinja2Templates(directory=template_dirs)


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": None
    })


@router.post("/register")
async def register(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    confirm_password: Annotated[str, Form()],
    db: Annotated[Session, Depends(get_db)]
):
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
    
    hashed_password = hash_password(password)
    
    try:
        user = User(
            email=email,
            hashed_password=hashed_password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        request.session["user_id"] = user.id
        
        return RedirectResponse("/", status_code=303)
        
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email address is already registered"
        }, status_code=400)


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
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
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid email or password"
        }, status_code=401)
    
    request.session["user_id"] = user.id
    
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@router.get("/profile/{email}", response_class=HTMLResponse)
async def user_profile(
    email: str,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_auth)]
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile_user": user
    })

