import pytest
from sqlalchemy.orm import Session

from app.services.todo.models import Todo


def test_database_session(test_db):
    """Test that database session is created"""
    assert test_db is not None
    assert isinstance(test_db, Session)


def test_create_todo(test_db):
    """Test creating a todo"""
    todo = Todo(
        title="Test Todo",
        description="Test Description"
    )
    test_db.add(todo)
    test_db.commit()
    test_db.refresh(todo)
    
    assert todo.id is not None
    assert todo.title == "Test Todo"
    assert todo.description == "Test Description"
    assert todo.completed is False
    assert todo.created_at is not None


def test_query_todos(test_db):
    """Test querying todos"""
    # Create multiple todos
    todo1 = Todo(title="First")
    todo2 = Todo(title="Second")
    test_db.add_all([todo1, todo2])
    test_db.commit()
    
    # Query all
    todos = test_db.query(Todo).all()
    assert len(todos) == 2


def test_update_todo(test_db):
    """Test updating a todo"""
    todo = Todo(title="Original")
    test_db.add(todo)
    test_db.commit()
    
    # Update
    todo.title = "Updated"
    todo.completed = True
    test_db.commit()
    
    # Verify
    updated = test_db.query(Todo).filter(Todo.id == todo.id).first()
    assert updated.title == "Updated"
    assert updated.completed is True


def test_delete_todo(test_db):
    """Test deleting a todo"""
    todo = Todo(title="To Delete")
    test_db.add(todo)
    test_db.commit()
    todo_id = todo.id
    
    # Delete
    test_db.delete(todo)
    test_db.commit()
    
    # Verify
    deleted = test_db.query(Todo).filter(Todo.id == todo_id).first()
    assert deleted is None


def test_todo_defaults(test_db):
    """Test todo default values"""
    todo = Todo(title="Test")
    test_db.add(todo)
    test_db.commit()
    test_db.refresh(todo)
    
    assert todo.completed is False
    assert todo.description is None
    assert todo.created_at is not None

