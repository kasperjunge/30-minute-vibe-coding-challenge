---
date: 2025-10-18T08:07:14+0200
researcher: Kasper Junge
git_commit: fdcadc19667562402840aed3335fa26c4f80cef6
branch: main
repository: 30-minute-vibe-coding-challenge
topic: "Remove TODO Example to Create Generic Template"
tags: [research, codebase, todo, template, cleanup]
status: complete
last_updated: 2025-10-18
last_updated_by: Kasper Junge
---

# Research: Remove TODO Example to Create Generic Template

**Date**: 2025-10-18 08:07:14 +0200  
**Researcher**: Kasper Junge  
**Git Commit**: fdcadc19667562402840aed3335fa26c4f80cef6  
**Branch**: main  
**Repository**: 30-minute-vibe-coding-challenge

## Research Question

What components make up the TODO example service in this FastAPI template, and what needs to be removed to create a more generic template where AI assistants don't have to remember to remove the todo app?

## Summary

The TODO example service is fully integrated throughout the template and consists of multiple interconnected components:

1. **Service directory** with models, routes, and templates
2. **Database migration** creating the todos table
3. **Router registration** in main.py
4. **Template directory** references in main.py
5. **Navigation links** in base template and home page
6. **Test suite** with comprehensive tests for todo functionality
7. **Test fixtures** and imports in conftest.py

The README already contains removal instructions (lines 165-182), but the presence of the TODO example adds cognitive overhead for AI assistants building new features, as they need to distinguish between template patterns (auth) and example code (todo).

## Detailed Findings

### 1. Service Directory Structure

**Location**: `app/services/todo/`

The todo service follows the standard service-based architecture pattern:

- `models.py` - Contains the Todo SQLAlchemy model with fields: id, title, description, completed, created_at
- `routes.py` - Contains 7 route handlers for CRUD operations:
  - GET `/todos/` - List all todos (requires auth)
  - GET `/todos/new` - Show create form (requires auth)
  - POST `/todos/` - Create new todo (requires auth)
  - GET `/todos/{id}/edit` - Show edit form (requires auth)
  - POST `/todos/{id}` - Update existing todo (requires auth)
  - POST `/todos/{id}/toggle` - Toggle completion status (requires auth)
  - POST `/todos/{id}/delete` - Delete todo (requires auth)
- `templates/` - Contains two Jinja2 templates:
  - `form.html` - Reusable form for creating/editing todos
  - `list.html` - List view with empty state and action buttons

All routes require authentication using the `require_auth` dependency from the auth service.

### 2. Main Application Integration

**Location**: `main.py`

The todo service is integrated into the main application at multiple points:

**Line 15**: Import statement
```python
from app.services.todo.routes import router as todo_router
```

**Line 22**: Template directory registration
```python
template_dirs = [
    "app/shared/templates",
    "app/services/todo/templates",  # This line
    "app/services/auth/templates"
]
```

**Line 90**: Router inclusion
```python
app.include_router(todo_router)
```

### 3. Navigation and Homepage References

**Location**: `app/shared/templates/base.html`

**Line 27**: Navigation link in header
```html
<li><a href="/todos" class="hover:text-blue-100">Todos</a></li>
```

**Line 68**: Footer reminder text
```html
<p class="text-sm text-gray-400 mt-2">Remove the TODO service to start your project</p>
```

**Location**: `app/shared/templates/home.html`

**Lines 18-27**: Featured example section with call-to-action
- Blue info box highlighting the TODO list as an example feature
- Button linking to `/todos`

**Lines 29-39**: Getting started instructions
- Yellow warning box with step-by-step removal instructions
- Mentions deleting `app/services/todo/` directory

### 4. Database Migration

**Location**: `migrations/versions/d8eafd73eb5b_initial_migration_add_todos_table.py`

**Created**: 2025-10-14 07:12:07
**Revision ID**: d8eafd73eb5b
**Down Revision**: None (this is the first migration)

Creates the `todos` table with columns:
- id (Integer, Primary Key)
- title (String(200), Not Null)
- description (Text, Nullable)
- completed (Boolean, Server Default '0', Not Null)
- created_at (DateTime, Not Null)

**Note**: This migration has `down_revision: None`, making it the initial migration. However, there's also a users table migration (`69aa68f0fca8_add_users_table.py`) that should be the actual initial migration for a clean template.

### 5. Test Suite Integration

**Location**: `tests/`

The TODO service has extensive test coverage across multiple test files:

**tests/test_todo_routes.py** (entire file dedicated to todo tests):
- 9 test functions covering all CRUD operations
- Tests for authentication requirement (redirects to login when not authenticated)
- Edge case testing (empty titles, non-existent todos)

**tests/test_database.py** (5 out of 6 tests are todo-specific):
- Lines 4, 13-85: Database operation tests using Todo model
- Tests CRUD operations at the database level

**tests/test_auth.py**:
- Line 172: Uses `/todos` endpoint to verify authentication redirect

**tests/conftest.py**:
- Line 10: Import of Todo model
- Line 61: Import of todo_router in test_client fixture
- Line 73: Template directory registration for tests
- Line 91: Router inclusion in test app
- Lines 106-119: `sample_todo` fixture for test data

### 6. Documentation

**Location**: `README.md`

**Lines 117-122**: Project structure section explicitly labels todo as example
```markdown
│   │   └── todo/           # Example service (remove this)
```

**Lines 165-182**: "Removing Example Code" section
- Provides bash command to remove directory
- Lists specific lines to delete from main.py
- Mentions removing the migration file
- Notes to update navigation in base.html

## Architecture Documentation

### Service-Based Pattern

The template demonstrates a service-based architecture where each feature is organized as a self-contained service module under `app/services/`. Each service contains:

1. **models.py** - SQLAlchemy models
2. **routes.py** - FastAPI router with endpoints
3. **templates/** - Jinja2 templates specific to the service
4. **dependencies.py** (optional) - Shared dependencies for the service

### Template Directory Configuration

The template uses Jinja2Templates with multiple directory support. Services can have their own template directories that are registered in main.py alongside shared templates. This allows templates to extend base templates while keeping service-specific templates organized within the service.

### Authentication Integration

The TODO service demonstrates how to protect routes with authentication by using the `require_auth` dependency from the auth service. All TODO routes require an authenticated user, showing the pattern for building protected features.

## Files Requiring Changes to Remove TODO Example

### Files to Delete:
1. `app/services/todo/` (entire directory with all contents)
2. `migrations/versions/d8eafd73eb5b_initial_migration_add_todos_table.py`
3. `tests/test_todo_routes.py`

### Files to Modify:

**main.py**:
- Remove line 15: `from app.services.todo.routes import router as todo_router`
- Remove `"app/services/todo/templates"` from line 22 template_dirs list
- Remove line 90: `app.include_router(todo_router)`

**app/shared/templates/base.html**:
- Remove line 27: `<li><a href="/todos" class="hover:text-blue-100">Todos</a></li>`
- Remove or update line 68: Footer text about removing TODO service

**app/shared/templates/home.html**:
- Remove or update lines 18-27: Blue info box about TODO example
- Remove or update lines 29-39: Getting started instructions (keep the concept, remove todo-specific references)

**tests/conftest.py**:
- Remove line 10: `from app.services.todo.models import Todo  # noqa: F401`
- Remove line 61: `from app.services.todo.routes import router as todo_router`
- Remove `"app/services/todo/templates"` from line 73
- Remove line 91: `app.include_router(todo_router)`
- Remove lines 106-119: `sample_todo` fixture

**tests/test_database.py**:
- Remove line 4: `from app.services.todo.models import Todo`
- Remove lines 13-85: All todo-related database tests
- Keep only the `test_database_connection` test

**tests/test_auth.py**:
- Update line 172: Change from `client.get("/todos")` to a different protected endpoint or remove the test

**README.md**:
- Update line 117: Remove "(remove this)" comment
- Remove or update lines 165-182: "Removing Example Code" section no longer needed

## Migration Ordering Issue

**Important Finding**: The todo migration `d8eafd73eb5b` has `down_revision: None`, indicating it's treated as the initial migration. However, the users table migration `69aa68f0fca8_add_users_table.py` should actually be the first migration since auth is the core template feature, not todo.

After removing the todo migration, the users migration will need to have its `down_revision` set to `None` to become the true initial migration.

## Open Questions

1. Should we create a new clean migration history after removing todo, or keep the existing users migration?
2. Should the home page retain "example service" instructions, or become a simpler landing page?
3. Should we keep any minimal example of adding a new service, or make it completely clean?

## Recommendations

Based on the research findings, here's the cleanest approach to create a generic template:

1. **Complete Removal**: Delete all todo-related code, tests, and migrations
2. **Reset Migration History**: Make the users table migration the initial migration
3. **Update Documentation**: Simplify the README to focus on how to add new services rather than how to remove the todo example
4. **Simplify Homepage**: Make home.html a clean landing page that demonstrates the auth system without referencing any example service
5. **Keep Auth Service**: The auth service should remain as it's a core template feature that most web apps need

This approach eliminates the cognitive overhead for AI assistants, who can focus on understanding the auth patterns and building new features without needing to filter out example code.

