from typing import Annotated

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.shared.database import get_db
from app.shared.config import settings
from app.services.todo.models import Todo

router = APIRouter(prefix="/todos", tags=["todos"])

# Templates for this service
templates = Jinja2Templates(directory=[
    "app/shared/templates",
    "app/services/todo/templates"
])


@router.get("/", response_class=HTMLResponse)
async def list_todos(
    request: Request,
    db: Session = Depends(get_db)
):
    """List all todos"""
    todos = db.query(Todo).order_by(Todo.created_at.desc()).all()
    return templates.TemplateResponse(
        "list.html",
        {"request": request, "todos": todos, "settings": settings}
    )


@router.get("/new", response_class=HTMLResponse)
async def new_todo_form(request: Request):
    """Show form for creating new todo"""
    return templates.TemplateResponse(
        "form.html",
        {"request": request, "todo": None, "action": "/todos", "settings": settings}
    )


@router.post("/", response_class=RedirectResponse)
async def create_todo(
    title: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    db: Session = Depends(get_db)
):
    """Create new todo from form data"""
    # Validate
    if not title or not title.strip():
        # TODO: Add flash message support
        return RedirectResponse(url="/todos/new", status_code=303)
    
    # Create todo
    todo = Todo(
        title=title.strip(),
        description=description.strip() if description else None
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    
    return RedirectResponse(url="/todos", status_code=303)


@router.get("/{todo_id}/edit", response_class=HTMLResponse)
async def edit_todo_form(
    request: Request,
    todo_id: int,
    db: Session = Depends(get_db)
):
    """Show form for editing existing todo"""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if not todo:
        return RedirectResponse(url="/todos", status_code=303)
    
    return templates.TemplateResponse(
        "form.html",
        {
            "request": request,
            "todo": todo,
            "action": f"/todos/{todo_id}",
            "settings": settings
        }
    )


@router.post("/{todo_id}", response_class=RedirectResponse)
async def update_todo(
    todo_id: int,
    title: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    completed: Annotated[str, Form()] = "",
    db: Session = Depends(get_db)
):
    """Update existing todo from form data"""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if not todo:
        return RedirectResponse(url="/todos", status_code=303)
    
    # Validate
    if not title or not title.strip():
        return RedirectResponse(url=f"/todos/{todo_id}/edit", status_code=303)
    
    # Update fields
    todo.title = title.strip()
    todo.description = description.strip() if description else None
    todo.completed = completed == "true"
    
    db.commit()
    
    return RedirectResponse(url="/todos", status_code=303)


@router.post("/{todo_id}/toggle", response_class=RedirectResponse)
async def toggle_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """Toggle todo completion status"""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if todo:
        todo.completed = not todo.completed
        db.commit()
    
    return RedirectResponse(url="/todos", status_code=303)


@router.post("/{todo_id}/delete", response_class=RedirectResponse)
async def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    """Delete a todo"""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if todo:
        db.delete(todo)
        db.commit()
    
    return RedirectResponse(url="/todos", status_code=303)

