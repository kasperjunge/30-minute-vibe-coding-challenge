# Remove TODO Example Service - Implementation Plan

## Overview

Remove the TODO example service from the FastAPI template to create a cleaner, more generic starting point. This eliminates cognitive overhead for AI assistants who currently need to distinguish between core template patterns (auth) and example code (todo). The auth service will remain as the primary demonstration of the service-based architecture pattern.

## Current State Analysis

The TODO service is fully integrated throughout the template with 7 CRUD endpoints, 2 Jinja2 templates, database migration, comprehensive test coverage, and navigation links. The research document (`research.md`) has identified all integration points across 8 files that require changes, plus 3 files/directories that need deletion.

### Key Discoveries:
- Todo migration `d8eafd73eb5b` incorrectly has `down_revision: None` - research.md:231
- Users migration `69aa68f0fca8` depends on the todo migration - migrations/versions/69aa68f0fca8_add_users_table.py:16
- All TODO routes require authentication, demonstrating the auth pattern - research.md:61
- Test fixtures in conftest.py are tightly coupled to todo service - research.md:148-152
- 5 out of 6 tests in test_database.py use the Todo model - research.md:140-142

## Desired End State

After completion, the template will:
- Contain only the auth service as a core feature
- Have a clean migration history with users table as the initial migration
- Display a simple, welcoming homepage without example service references
- Have passing tests that don't depend on todo functionality
- Include updated README that focuses on extending the template rather than removing examples

### Verification:
1. Application starts without errors: `uv run python main.py`
2. All tests pass: `uv run pytest`
3. Homepage displays cleanly at http://localhost:8000
4. Navigation contains only Home/Login/Register links
5. Database migrations apply cleanly from scratch

## What We're NOT Doing

- NOT removing the auth service (it's a core template feature)
- NOT changing the service-based architecture pattern
- NOT modifying the database connection or ORM setup
- NOT changing the Jinja2 templating approach
- NOT updating deployment configuration (Dockerfile)
- NOT changing test infrastructure beyond todo-specific code

## Implementation Approach

We'll proceed in 7 phases, starting with file deletions and working through integration points systematically. Each phase is designed to maintain a working state (though tests may fail temporarily). The final phase updates documentation to reflect the cleaner template state.

---

## Phase 1: Delete TODO Service Files

### Overview
Remove the entire TODO service directory and its database migration file. This is the foundation for all subsequent changes.

### Changes Required:

#### 1. Service Directory
**Directory**: `app/services/todo/`
**Action**: Delete entire directory including:
- `models.py` (Todo SQLAlchemy model)
- `routes.py` (7 CRUD route handlers)
- `templates/form.html`
- `templates/list.html`
- `__init__.py`

#### 2. Migration File
**File**: `migrations/versions/d8eafd73eb5b_initial_migration_add_todos_table.py`
**Action**: Delete file

#### 3. Test File
**File**: `tests/test_todo_routes.py`
**Action**: Delete file (9 test functions covering todo CRUD operations)

### Success Criteria:

#### Automated Verification:
- [x] Directory does not exist: `test ! -d app/services/todo && echo "PASS" || echo "FAIL"`
- [x] Migration file deleted: `test ! -f migrations/versions/d8eafd73eb5b_initial_migration_add_todos_table.py && echo "PASS" || echo "FAIL"`
- [x] Test file deleted: `test ! -f tests/test_todo_routes.py && echo "PASS" || echo "FAIL"`

#### Manual Verification:
- [x] Files are no longer visible in file explorer
- [x] Git status shows deletions if using version control

**Implementation Note**: After completing this phase, the application and tests will fail due to import errors. This is expected - proceed to Phase 2 to fix integration points.

---

## Phase 2: Update Main Application (main.py)

### Overview
Remove todo service integration from the main application file - imports, template directory registration, and router inclusion.

### Changes Required:

#### 1. Remove Import Statement
**File**: `main.py`
**Line**: 15

```python
# REMOVE THIS LINE:
from app.services.todo.routes import router as todo_router
```

#### 2. Remove Template Directory
**File**: `main.py`
**Lines**: 20-24

```python
# CHANGE FROM:
template_dirs = [
    "app/shared/templates",
    "app/services/todo/templates",
    "app/services/auth/templates"
]

# CHANGE TO:
template_dirs = [
    "app/shared/templates",
    "app/services/auth/templates"
]
```

#### 3. Remove Router Inclusion
**File**: `main.py`
**Line**: 90

```python
# REMOVE THIS LINE:
app.include_router(todo_router)
```

### Success Criteria:

#### Automated Verification:
- [x] Application starts successfully: `timeout 5 uv run python main.py || echo "PASS"`
- [x] No import errors in main.py: `uv run python -c "from main import app; print('PASS')"`
- [x] Template directories configured correctly: `uv run python -c "from main import templates; assert len(templates.env.loader.searchpath) == 2; print('PASS')"`

#### Manual Verification:
- [x] Application runs without crashes
- [x] No todo-related import errors in console

**Implementation Note**: After this phase, the application should start successfully, but the homepage and tests will still reference todo functionality.

---

## Phase 3: Update Templates

### Overview
Remove todo references from navigation and homepage, replacing them with a clean, welcoming landing page.

### Changes Required:

#### 1. Base Template - Remove Navigation Link
**File**: `app/shared/templates/base.html`
**Line**: 27

```html
<!-- REMOVE THIS LINE: -->
<li><a href="/todos" class="hover:text-blue-100">Todos</a></li>
```

#### 2. Base Template - Update Footer
**File**: `app/shared/templates/base.html`
**Line**: 68

```html
<!-- CHANGE FROM: -->
<p class="text-sm text-gray-400 mt-2">Remove the TODO service to start your project</p>

<!-- CHANGE TO: -->
<p class="text-sm text-gray-400 mt-2">Built with FastAPI, SQLite, and Jinja2</p>
```

#### 3. Homepage - Complete Replacement
**File**: `app/shared/templates/home.html`
**Lines**: 1-68

Replace entire content with:

```html
{% extends "base.html" %}

{% block title %}Home - FastAPI Template{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto">
    <div class="bg-white rounded-lg shadow-md p-8">
        <h2 class="text-3xl font-bold text-gray-800 mb-4">
            Welcome to FastAPI Template
        </h2>
        
        <p class="text-gray-600 mb-6">
            A minimal, production-ready web application template using FastAPI, SQLite, and Jinja2.
            This template provides clear patterns and structure that make it easy for AI coding 
            assistants to understand and extend functionality.
        </p>
        
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
            <h3 class="font-semibold text-blue-900 mb-2">🔐 Authentication Included</h3>
            <p class="text-blue-800 mb-3">
                User registration and login are already implemented. Try creating an account to see 
                the authentication system in action.
            </p>
            <div class="space-x-3">
                <a href="/auth/register" 
                   class="inline-block bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition">
                    Create Account →
                </a>
                <a href="/auth/login" 
                   class="inline-block bg-white text-blue-600 border border-blue-600 px-6 py-2 rounded hover:bg-blue-50 transition">
                    Sign In →
                </a>
            </div>
        </div>
        
        <div class="grid md:grid-cols-3 gap-4">
            <div class="border rounded-lg p-4">
                <h4 class="font-semibold text-gray-800 mb-2">🚀 Quick Start</h4>
                <p class="text-sm text-gray-600">
                    Run <code class="bg-gray-100 px-1 rounded">uv sync</code>, 
                    then <code class="bg-gray-100 px-1 rounded">uv run python main.py</code>
                </p>
            </div>
            
            <div class="border rounded-lg p-4">
                <h4 class="font-semibold text-gray-800 mb-2">🏗️ Service-Based Architecture</h4>
                <p class="text-sm text-gray-600">
                    Add new features by creating services in <code class="bg-gray-100 px-1 rounded">app/services/</code>
                </p>
            </div>
            
            <div class="border rounded-lg p-4">
                <h4 class="font-semibold text-gray-800 mb-2">🧪 Test Ready</h4>
                <p class="text-sm text-gray-600">
                    Includes pytest setup with fixtures for database and authenticated requests
                </p>
            </div>
        </div>
        
        <div class="mt-6 p-4 bg-gray-50 rounded border border-gray-200">
            <h4 class="font-semibold text-gray-700 mb-2">What's Included:</h4>
            <ul class="text-sm text-gray-600 space-y-1">
                <li>✓ User authentication with session management</li>
                <li>✓ SQLite database with Alembic migrations</li>
                <li>✓ Jinja2 templates with Tailwind CSS</li>
                <li>✓ Service-based architecture pattern</li>
                <li>✓ Comprehensive test suite</li>
                <li>✓ Docker deployment configuration</li>
            </ul>
        </div>
    </div>
</div>
{% endblock %}
```

### Success Criteria:

#### Automated Verification:
- [x] No references to `/todos` in templates: `! grep -r "/todos" app/shared/templates/ && echo "PASS" || echo "FAIL"`
- [x] No references to "TODO" in base.html: `! grep -i "todo" app/shared/templates/base.html && echo "PASS" || echo "FAIL"`
- [x] Homepage renders without errors: `uv run python -c "from main import app; from fastapi.testclient import TestClient; client = TestClient(app); response = client.get('/'); assert response.status_code == 200; print('PASS')"`

#### Manual Verification:
- [x] Homepage displays new welcome message
- [x] Navigation bar shows only: Home, Login, Register (when logged out)
- [x] Footer shows updated text without todo reference
- [x] Authentication links work correctly
- [x] Page styling looks clean and professional

**Implementation Note**: After this phase, the user-facing application should be fully functional and clean. Tests will still need updates in the next phases.

---

## Phase 4: Update Test Configuration (conftest.py)

### Overview
Remove todo-related imports, router inclusion, and fixtures from the test configuration file.

### Changes Required:

#### 1. Remove Model Import
**File**: `tests/conftest.py`
**Line**: 10

```python
# REMOVE THIS LINE:
from app.services.todo.models import Todo  # noqa: F401
```

#### 2. Remove Router Import in client Fixture
**File**: `tests/conftest.py`
**Line**: 61

```python
# REMOVE THIS LINE (inside client fixture):
from app.services.todo.routes import router as todo_router
```

#### 3. Remove Template Directory
**File**: `tests/conftest.py`
**Line**: 73

```python
# CHANGE FROM:
template_dirs = ["app/shared/templates", "app/services/todo/templates"]

# CHANGE TO:
template_dirs = ["app/shared/templates", "app/services/auth/templates"]
```

#### 4. Remove Router Inclusion
**File**: `tests/conftest.py`
**Line**: 91

```python
# REMOVE THIS LINE (inside client fixture):
app.include_router(todo_router)
```

#### 5. Remove sample_todo Fixture
**File**: `tests/conftest.py`
**Lines**: 105-119

```python
# REMOVE THIS ENTIRE FIXTURE:
@pytest.fixture
def sample_todo(test_db):
    """Create a sample todo for tests"""
    from app.services.todo.models import Todo
    
    todo = Todo(
        title="Test Todo",
        description="Test Description",
        completed=False
    )
    test_db.add(todo)
    test_db.commit()
    test_db.refresh(todo)
    
    return todo
```

### Success Criteria:

#### Automated Verification:
- [x] Conftest imports successfully: `uv run python -c "import tests.conftest; print('PASS')"`
- [x] No references to Todo model: `! grep -i "from app.services.todo" tests/conftest.py && echo "PASS" || echo "FAIL"`
- [x] Test fixtures load correctly: `uv run pytest --collect-only tests/ && echo "PASS" || echo "FAIL"`

#### Manual Verification:
- [x] No import errors when running pytest
- [x] Fixtures are available for remaining tests

**Implementation Note**: After this phase, the test infrastructure is clean but some test files still reference todo functionality.

---

## Phase 5: Update Remaining Test Files

### Overview
Remove or update todo-specific tests in test_database.py and test_auth.py.

### Changes Required:

#### 1. Update test_database.py - Remove Todo Import
**File**: `tests/test_database.py`
**Line**: 4

```python
# REMOVE THIS LINE:
from app.services.todo.models import Todo
```

#### 2. Update test_database.py - Remove Todo Tests
**File**: `tests/test_database.py`
**Lines**: 13-85

Remove these 5 test functions:
- `test_create_todo(test_db)`
- `test_read_todo(test_db)`
- `test_update_todo(test_db)`
- `test_delete_todo(test_db)`
- `test_query_todos(test_db)`

Keep only: `test_database_connection(test_db)`

After changes, the file should look like:

```python
"""
Database operation tests
"""
from app.shared.database import Base


def test_database_connection(test_db):
    """Test that we can connect to the database"""
    # If we got a test_db fixture, connection works
    assert test_db is not None
    assert test_db.bind is not None
    
    # Verify Base metadata is configured
    assert Base.metadata is not None
```

#### 3. Update test_auth.py - Fix Protected Route Test
**File**: `tests/test_auth.py`
**Line**: 172

```python
# CHANGE FROM:
response = client.get("/todos")

# CHANGE TO:
response = client.get("/auth/profile/test@example.com")
```

The full test should look like:

```python
def test_require_auth_redirects(client):
    """Test that require_auth decorator redirects to login"""
    # Use auth profile as example of protected route
    response = client.get("/auth/profile/test@example.com")
    
    # Should redirect to login
    assert response.status_code == 307
    assert "/auth/login" in response.headers["location"]
```

### Success Criteria:

#### Automated Verification:
- [x] All tests pass: `uv run pytest tests/ -v`
- [x] No todo imports in test files: `! grep -r "from app.services.todo" tests/ && echo "PASS" || echo "FAIL"`
- [x] No references to `/todos` endpoint: `! grep -r '"/todos"' tests/ && echo "PASS" || echo "FAIL"`
- [x] Test coverage shows only auth and database tests: `uv run pytest --collect-only tests/`

#### Manual Verification:
- [x] Test suite runs without errors
- [x] Test output shows only auth and database tests
- [x] No skipped tests due to missing fixtures

**Implementation Note**: After this phase, all tests should pass successfully and the application is fully functional without todo references.

---

## Phase 6: Fix Migration History

### Overview
Update the users migration to have `down_revision: None`, making it the true initial migration for a clean template foundation.

### Changes Required:

#### 1. Update Users Migration
**File**: `migrations/versions/69aa68f0fca8_add_users_table.py`
**Line**: 16

```python
# CHANGE FROM:
down_revision: Union[str, Sequence[str], None] = 'd8eafd73eb5b'

# CHANGE TO:
down_revision: Union[str, Sequence[str], None] = None
```

#### 2. Update Migration Comment (Optional but Recommended)
**File**: `migrations/versions/69aa68f0fca8_add_users_table.py`
**Lines**: 1-6

```python
# CHANGE FROM:
"""add users table

Revision ID: 69aa68f0fca8
Revises: d8eafd73eb5b
Create Date: 2025-10-17 08:27:20.411457

"""

# CHANGE TO:
"""Initial migration - add users table

Revision ID: 69aa68f0fca8
Revises: 
Create Date: 2025-10-17 08:27:20.411457

"""
```

### Success Criteria:

#### Automated Verification:
- [x] Migration history is clean: `uv run alembic history | head -n 5`
- [x] Only one migration exists: `test $(ls -1 migrations/versions/*.py | wc -l) -eq 1 && echo "PASS" || echo "FAIL"`
- [x] Migration applies to fresh database: `rm -f data/app.db && uv run alembic upgrade head && echo "PASS"`
- [x] Application starts with fresh database: `uv run python main.py & sleep 3 && kill %1 && echo "PASS"`

#### Manual Verification:
- [x] Delete `data/app.db` and restart application - users table is created
- [x] Can register new user successfully
- [x] No migration errors in console output
- [x] `alembic current` shows correct migration

**Implementation Note**: After this phase, the migration history is clean. Consider deleting `data/app.db` in your development environment to test the clean migration path.

---

## Phase 7: Update Documentation (README.md)

### Overview
Update the README to reflect the cleaner template state, removing instructions about removing the todo example.

### Changes Required:

#### 1. Update Project Structure Section
**File**: `README.md`
**Line**: 117 (approximate)

```markdown
<!-- CHANGE FROM: -->
│   │   └── todo/           # Example service (remove this)

<!-- CHANGE TO: -->
│   │   └── auth/           # Authentication service
```

#### 2. Remove "Removing Example Code" Section
**File**: `README.md`
**Lines**: 165-182 (approximate)

Remove the entire "Removing Example Code" section that explains how to delete the todo service.

#### 3. Update Feature List (if present)
Search for any bullet points or feature descriptions that mention "TODO example" and update them to focus on the template's core capabilities:

```markdown
<!-- If there's a features section, ensure it says something like: -->
- ✅ User authentication and session management
- ✅ Service-based architecture for organizing features
- ✅ Database migrations with Alembic
- ✅ Jinja2 templates with Tailwind CSS
- ✅ Comprehensive test suite with pytest
```

#### 4. Add "Creating New Services" Section (Optional)
Consider adding a brief section that explains the service pattern:

```markdown
## Creating New Services

This template uses a service-based architecture. Each feature is organized as a self-contained service:

```
app/services/your_feature/
├── __init__.py
├── models.py          # SQLAlchemy models
├── routes.py          # FastAPI endpoints
├── templates/         # Jinja2 templates
└── dependencies.py    # (optional) Shared dependencies
```

To add a new service:
1. Create a new directory under `app/services/`
2. Define your models in `models.py`
3. Create your routes in `routes.py`
4. Register templates in `main.py` template_dirs
5. Include your router in `main.py`

See the `auth` service for a complete example.
```

### Success Criteria:

#### Automated Verification:
- [x] No references to "remove" in context of todo: `! grep -i "remove.*todo\|todo.*remove" README.md && echo "PASS" || echo "FAIL"`
- [x] No references to "example service" with removal context: `! grep -A 2 -B 2 "example.*service" README.md | grep -i remove && echo "PASS" || echo "FAIL"`
- [x] README renders correctly: `uv run python -c "import markdown; markdown.markdown(open('README.md').read()); print('PASS')"`

#### Manual Verification:
- [x] README accurately describes the template
- [x] No outdated instructions remain
- [x] Project structure diagram is accurate
- [x] Getting started instructions work correctly

**Implementation Note**: This is the final phase. After completion, the template is fully cleaned and ready for use as a generic starting point.

---

## Testing Strategy

### Unit Tests
After all phases complete, the test suite should include:
- **Database tests**: Basic connection test in `test_database.py`
- **Auth tests**: All authentication functionality tests in `test_auth.py`
- **Config tests**: Configuration validation in `test_config.py`

### Integration Tests
Manual testing should verify:
- Fresh database initialization works
- User registration and login flow
- Session persistence across requests
- Protected routes redirect correctly
- Error pages (404, 500) display correctly

### Manual Testing Steps
1. **Clean slate test**: Delete `data/app.db` and restart application
2. **Registration flow**: Create new user at `/auth/register`
3. **Login flow**: Sign in with created user
4. **Profile access**: View user profile
5. **Logout flow**: Log out and verify redirect
6. **Protected route**: Try accessing profile while logged out
7. **Homepage**: Verify clean, professional appearance
8. **Navigation**: Verify all nav links work correctly

## Performance Considerations

This change should have positive performance impacts:
- **Reduced bundle size**: Fewer route handlers and templates to load
- **Faster tests**: Fewer tests to run means faster CI/CD
- **Lower cognitive load**: Clearer codebase is easier to understand and extend

## Migration Notes

### For Existing Deployments
If you have an existing deployment with todo data:
1. **Backup data**: Export any important todos before proceeding
2. **Run migrations**: The old migration will be removed, but existing tables remain
3. **Manual cleanup**: Drop the `todos` table manually if desired: `DROP TABLE todos;`

### For Fresh Installs
Fresh installations will use the clean migration history with only the users table as the initial migration.

### Database Reset Option
To start completely fresh:
```bash
rm data/app.db
uv run alembic upgrade head
```

## References

- Original research: `tasks/001-2025-10-18-remove-todo-example/research.md`
- Service pattern example: `app/services/auth/` (remains as reference)
- Migration documentation: Alembic official docs

