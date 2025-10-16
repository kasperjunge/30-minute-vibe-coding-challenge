# Implementation Plan: Claude Plugin Marketplace

## Overview
Building a public web-based marketplace for Claude Code plugins where creators can upload/share plugins and users can discover/install them via Claude Code's `/plugin marketplace add` command. The platform uses FastAPI with SQLite, local file storage, and generates Claude Code-compatible marketplace.json.

## Current State
- Basic FastAPI project structure exists with:
  - Todo service (example/template)
  - Shared config, database, templates
  - SQLite database with Alembic migrations
  - Tailwind CSS via CDN
  - Test setup with pytest
- Starting point: Need to build auth, plugin, and report services from scratch

## Desired End State
A fully functional marketplace where:
- Plugin creators register, upload, and manage their plugins
- Users browse, search, discover plugins without authentication
- Plugins install seamlessly in Claude Code via marketplace.json
- Admins moderate reported plugins
- All acceptance criteria from requirements.md are met

**Success Criteria:**
- [ ] All 7 user stories from requirements.md are implemented
- [ ] All functional requirements (FR1-FR12) are met
- [ ] marketplace.json is valid and Claude Code-compatible
- [ ] Code passes all automated tests
- [ ] Application runs without errors
- [ ] Non-functional requirements met (performance, security, usability)

## What We're NOT Doing
From requirements.md out-of-scope section:
- GitHub integration or auto-sync
- OAuth login (Google, GitHub)
- Plugin ratings/reviews/favorites
- Usage statistics or download counts
- Featured/trending sections
- Tags or categories
- Plugin dependencies management
- Automated testing of uploaded plugins
- Paid/premium plugins
- Team/organization accounts
- Plugin analytics for creators
- Email notifications for updates
- API for programmatic access
- Multiple marketplaces
- Plugin editing in web UI
- Mobile app or mobile-optimized views
- Advanced admin features (bulk actions, analytics)

## Implementation Approach
We'll build in 5 phases, each independently verifiable:

1. **Phase 1: Authentication Foundation** - Users must be able to register/login before uploading plugins
2. **Phase 2: Plugin Upload Core** - Once authenticated, creators need to upload and validate plugins
3. **Phase 3: Plugin Discovery** - Users need to find plugins via browse/search
4. **Phase 4: Marketplace Integration** - Connect to Claude Code via marketplace.json
5. **Phase 5: Moderation System** - Enable community reporting and admin moderation

Each phase builds on previous ones. We implement services incrementally, testing as we go.

---

## Phase 1: Authentication Foundation

### Overview
Implement user registration, login, logout, and session management to enable plugin creators to authenticate before uploading.

### Tasks

#### 1.1 Add Authentication Dependencies
**Action**:
- Add `passlib[bcrypt]`, `python-multipart`, and `itsdangerous` to dependencies
- Install packages with uv

**Files Modified**:
- `pyproject.toml` - add to `[project.dependencies]`

**Command to Run**:
```bash
uv add "passlib[bcrypt]>=1.7.4" "itsdangerous>=2.2.0"
```

**Verification Steps**:
1. Run: `uv sync`
2. Verify packages installed without errors
3. Expected: Clean installation, all dependencies resolved

**Success Criteria**:
- [x] Dependencies added to pyproject.toml
- [x] Packages installed successfully
- [x] uv.lock updated

#### 1.2 Create User Model and Migration
**File**: `app/services/auth/models.py`
**Action**:
- Create auth service directory structure
- Implement User model with fields from design.md
- Generate Alembic migration

**Code Structure**:
```python
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.shared.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

**Files Created**:
- `app/services/auth/__init__.py`
- `app/services/auth/models.py`
- Migration file: `migrations/versions/[hash]_add_users_table.py`

**Test Requirements**:
- [ ] Write test to verify User model creates successfully
- [ ] Test unique constraints on email and username
- [ ] Test default values (is_admin=False, created_at auto-set)
- [ ] Tests pass: `uv run pytest tests/test_auth.py::test_user_model -v`

**Verification Steps**:
1. Generate migration: `uv run alembic revision --autogenerate -m "Add users table"`
2. Apply migration: `uv run alembic upgrade head`
3. Verify table created: `sqlite3 data/app.db ".schema users"`
4. Run model tests
5. Expected: Users table exists with all columns, indexes created

**Success Criteria**:
- [x] User model implemented with all fields
- [x] Migration generated and applied
- [x] Database table created with indexes
- [x] Model tests written and passing

#### 1.3 Implement Password Hashing Utilities
**File**: `app/services/auth/utils.py`
**Action**:
- Create password hashing and verification functions using passlib/bcrypt
- Use bcrypt cost factor 12 (from design.md security requirements)

**Code Structure**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

**Files Created**:
- `app/services/auth/utils.py`

**Test Requirements**:
- [ ] Test hash_password returns different hash each time (salt)
- [ ] Test verify_password succeeds with correct password
- [ ] Test verify_password fails with wrong password
- [ ] Test hashed password never matches plain password
- [ ] Tests pass: `uv run pytest tests/test_auth.py::test_password_utils -v`

**Verification Steps**:
1. Run password utility tests
2. Manually test in Python REPL: hash a password, verify it
3. Expected: All tests passing, passwords hash correctly

**Success Criteria**:
- [x] Password hashing functions implemented
- [x] Bcrypt cost factor set to 12
- [x] Unit tests written and passing
- [x] Functions work correctly in manual test

#### 1.4 Implement Session Middleware
**File**: `app/shared/middleware.py`
**Action**:
- Create session middleware using itsdangerous for signed cookies
- Store user_id in session cookie
- Session duration: 30 days (from design.md)
- Cookie name: `plugin_marketplace_session`

**Code Structure**:
```python
from starlette.middleware.base import BaseHTTPMiddleware
from itsdangerous import URLSafeSerializer, BadSignature
from fastapi import Request
from app.services.auth.models import User
from app.shared.database import get_db

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Read and verify session cookie
        # Inject request.state.user if valid session
        # Continue request
        pass
```

**Files Created/Modified**:
- `app/shared/middleware.py` (create)
- `main.py` (add middleware)

**Test Requirements**:
- [ ] Test middleware sets session cookie after login
- [ ] Test middleware reads valid session cookie
- [ ] Test middleware rejects invalid/tampered cookie
- [ ] Test middleware handles missing cookie gracefully
- [ ] Tests pass: `uv run pytest tests/test_auth.py::test_session_middleware -v`

**Verification Steps**:
1. Run middleware tests
2. Manual test: Register, check cookie set in browser dev tools
3. Expected: Cookie signed, session persists across requests

**Success Criteria**:
- [x] Session middleware implemented and added to app
- [x] Signed cookies working correctly
- [x] Session duration configured to 30 days
- [x] Tests written and passing

#### 1.5 Create Authentication Dependencies
**File**: `app/services/auth/dependencies.py`
**Action**:
- Create `get_current_user()` dependency for protected routes
- Create `require_admin()` dependency for admin-only routes
- Handle redirects to login page when not authenticated

**Code Structure**:
```python
from fastapi import Request, HTTPException, Depends
from app.services.auth.models import User
from sqlalchemy.orm import Session
from app.shared.database import get_db

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Get current authenticated user from session."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()

async def require_auth(user: User | None = Depends(get_current_user)) -> User:
    """Require authentication, raise 401 if not authenticated."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

async def require_admin(user: User = Depends(require_auth)) -> User:
    """Require admin privileges."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user
```

**Files Created**:
- `app/services/auth/dependencies.py`

**Test Requirements**:
- [ ] Test get_current_user returns None when not logged in
- [ ] Test get_current_user returns User when logged in
- [ ] Test require_auth raises 401 when not authenticated
- [ ] Test require_admin raises 403 when not admin
- [ ] Test require_admin succeeds for admin users
- [ ] Tests pass: `uv run pytest tests/test_auth.py::test_auth_dependencies -v`

**Verification Steps**:
1. Run dependency tests
2. Test protected route rejects unauthenticated requests
3. Expected: Dependencies work correctly in routes

**Success Criteria**:
- [x] Authentication dependencies implemented
- [x] Admin check working correctly
- [x] Unit tests written and passing

#### 1.6 Create Registration Page and Route
**Files**: 
- `app/services/auth/routes.py`
- `app/services/auth/templates/register.html`

**Action**:
- Create registration form (username, email, password, confirm password)
- Implement POST /auth/register endpoint
- Validate inputs (email format, password match, unique email/username)
- Hash password and create user
- Set session cookie and redirect to homepage

**Implements User Story**: Story 1 (acceptance: create account with email/password)

**Code Structure**:
```python
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.services.auth.models import User
from app.services.auth.utils import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/services/auth/templates")

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Validate inputs
    # Check duplicate email/username
    # Hash password
    # Create user
    # Set session
    # Redirect
    pass
```

**Template Structure** (register.html):
- Extend base.html
- Form with fields: username, email, password, confirm_password
- Submit button
- Link to login page
- Error message display area

**Test Requirements**:
- [ ] Test registration with valid data creates user
- [ ] Test duplicate email returns error
- [ ] Test duplicate username returns error
- [ ] Test password mismatch returns error
- [ ] Test invalid email format returns error
- [ ] Test successful registration sets session cookie
- [ ] Test successful registration redirects to homepage
- [ ] Tests pass: `uv run pytest tests/test_auth.py::test_registration -v`

**Verification Steps**:
1. Run registration tests
2. Manual test: Visit /auth/register, fill form, submit
3. Check database: `sqlite3 data/app.db "SELECT * FROM users;"`
4. Expected: User created, password hashed, session set

**Success Criteria**:
- [x] Registration form renders correctly
- [x] Registration endpoint validates inputs
- [x] Password hashing works
- [x] Session cookie set after registration
- [x] Tests written and passing
- [x] Manual verification successful

#### 1.7 Create Login Page and Route
**Files**: 
- `app/services/auth/routes.py` (add to existing)
- `app/services/auth/templates/login.html`

**Action**:
- Create login form (email, password)
- Implement POST /auth/login endpoint
- Verify credentials against database
- Set session cookie on success
- Redirect to homepage or originally requested page

**Implements User Story**: Story 1 (acceptance: log in to account)

**Code Structure**:
```python
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Find user by email
    # Verify password
    # Set session
    # Redirect
    pass
```

**Template Structure** (login.html):
- Extend base.html
- Form with fields: email, password
- Submit button
- Link to register page
- Error message display area

**Test Requirements**:
- [ ] Test login with correct credentials succeeds
- [ ] Test login with wrong password fails
- [ ] Test login with non-existent email fails
- [ ] Test successful login sets session cookie
- [ ] Test successful login redirects to homepage
- [ ] Tests pass: `uv run pytest tests/test_auth.py::test_login -v`

**Verification Steps**:
1. Run login tests
2. Manual test: Register user, logout, login again
3. Verify session cookie set in browser
4. Expected: Login works, session persists

**Success Criteria**:
- [x] Login form renders correctly
- [x] Login endpoint verifies credentials
- [x] Session cookie set after login
- [x] Tests written and passing
- [x] Manual verification successful

#### 1.8 Create Logout Route and User Profile Page
**Files**: 
- `app/services/auth/routes.py` (add to existing)
- `app/services/auth/templates/profile.html`

**Action**:
- Implement POST /auth/logout endpoint (clears session)
- Create GET /users/@{username} profile page (public)
- Profile shows username, member since date, list of plugins (placeholder for now)

**Implements User Story**: Story 2 (view public profile)

**Code Structure**:
```python
@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

@router.get("/users/@{username}", response_class=HTMLResponse)
async def user_profile(username: str, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Get user's plugins (placeholder for now)
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "plugins": []
    })
```

**Test Requirements**:
- [ ] Test logout clears session cookie
- [ ] Test logout redirects to homepage
- [ ] Test profile page shows user info
- [ ] Test profile page 404s for non-existent user
- [ ] Tests pass: `uv run pytest tests/test_auth.py::test_logout_and_profile -v`

**Verification Steps**:
1. Run logout and profile tests
2. Manual test: Login, logout, verify session cleared
3. Visit profile page: /users/@testuser
4. Expected: Logout works, profile page displays

**Success Criteria**:
- [x] Logout route clears session
- [x] Profile page renders user info
- [x] 404 handling for missing users
- [x] Tests written and passing

#### 1.9 Update Base Template with Auth Navigation
**File**: `app/shared/templates/base.html`
**Action**:
- Add navigation header
- Show "Login | Register" when not authenticated
- Show "Upload Plugin | My Plugins | Logout" when authenticated
- Show "Admin Dashboard" link for admins

**Template Changes**:
```html
<nav class="bg-gray-800 text-white p-4">
  <div class="container mx-auto flex justify-between">
    <a href="/" class="text-xl font-bold">Plugin Marketplace</a>
    <div>
      {% if request.state.user %}
        <a href="/plugins/upload">Upload Plugin</a>
        <a href="/plugins/my-plugins">My Plugins</a>
        {% if request.state.user.is_admin %}
          <a href="/admin/reports">Admin</a>
        {% endif %}
        <a href="/users/@{{ request.state.user.username }}">@{{ request.state.user.username }}</a>
        <form method="post" action="/auth/logout" class="inline">
          <button type="submit">Logout</button>
        </form>
      {% else %}
        <a href="/auth/login">Login</a>
        <a href="/auth/register">Register</a>
      {% endif %}
    </div>
  </div>
</nav>
```

**Verification Steps**:
1. Run app: `uv run uvicorn main:app --reload`
2. Visit homepage, verify navigation shows login/register
3. Login, verify navigation changes to authenticated view
4. Expected: Navigation displays correctly based on auth state

**Success Criteria**:
- [x] Navigation header added to base template
- [x] Conditional display based on authentication
- [x] Admin link shows only for admins
- [x] Manual verification successful

#### 1.10 Register Auth Routes in Main App
**File**: `main.py`
**Action**:
- Import and include auth router
- Add session middleware to app
- Configure session secret key

**Code Changes**:
```python
from app.services.auth.routes import router as auth_router
from app.shared.middleware import SessionMiddleware
from starlette.middleware.sessions import SessionMiddleware as StarletteSessionMiddleware

app.add_middleware(
    StarletteSessionMiddleware,
    secret_key="your-secret-key-here",  # TODO: Move to config
    max_age=30 * 24 * 60 * 60  # 30 days
)

app.include_router(auth_router)
```

**Verification Steps**:
1. Run app: `uv run uvicorn main:app --reload`
2. Visit /auth/register
3. Complete registration flow
4. Expected: Routes accessible, no errors

**Success Criteria**:
- [x] Auth routes registered
- [x] Session middleware added
- [x] App runs without errors
- [x] Auth flow works end-to-end

---

## Phase 2: Plugin Upload & Validation Core

### Overview
Implement plugin upload, validation, file storage, and version management so creators can publish plugins to the marketplace.

### Tasks

#### 2.1 Create Plugin and PluginVersion Models
**File**: `app/services/plugin/models.py`
**Action**:
- Create plugin service directory structure
- Implement Plugin and PluginVersion models from design.md
- Set up relationships with User model
- Generate migration

**Code Structure**:
```python
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.shared.database import Base

class Plugin(Base):
    __tablename__ = "plugins"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    author = relationship("User", backref="plugins")
    versions = relationship("PluginVersion", back_populates="plugin")

class PluginVersion(Base):
    __tablename__ = "plugin_versions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("plugins.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    readme_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    plugin = relationship("Plugin", back_populates="versions")
```

**Files Created**:
- `app/services/plugin/__init__.py`
- `app/services/plugin/models.py`
- Migration file: `migrations/versions/[hash]_add_plugins_tables.py`

**Test Requirements**:
- [x] Test Plugin model creates successfully
- [x] Test PluginVersion model creates successfully
- [x] Test relationships between Plugin, PluginVersion, User
- [ ] Test unique constraint on (author_id, name)
- [ ] Test unique constraint on (plugin_id, version)
- [x] Tests pass: `uv run pytest tests/test_plugin.py::test_plugin_models -v`

**Verification Steps**:
1. Generate migration: `uv run alembic revision --autogenerate -m "Add plugins and plugin_versions tables"`
2. Apply migration: `uv run alembic upgrade head`
3. Verify tables: `sqlite3 data/app.db ".schema plugins"`
4. Run model tests
5. Expected: Tables created with indexes and foreign keys

**Success Criteria**:
- [x] Plugin and PluginVersion models implemented
- [x] Migration generated and applied
- [x] Database tables created with relationships
- [x] Model tests written and passing

#### 2.2 Implement Plugin Validation Logic
**File**: `app/services/plugin/validation.py`
**Action**:
- Create validation functions for plugin structure
- Check for .claude-plugin/plugin.json
- Validate JSON schema (name, version, description)
- Check semantic versioning format
- Reject executable file extensions (.exe, .sh, .bat, .cmd)

**Code Structure**:
```python
import zipfile
import json
from pathlib import Path
from typing import Dict, Tuple

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_plugin_zip(zip_path: Path) -> Dict:
    """
    Validate plugin zip structure and return metadata.
    
    Returns:
        Dict containing plugin.json contents
        
    Raises:
        ValidationError with user-friendly message
    """
    # Check if zip is valid
    # Check for .claude-plugin/plugin.json
    # Parse and validate JSON
    # Check required fields
    # Validate version format
    # Check for forbidden files
    # Return metadata dict
    pass

def validate_version_format(version: str) -> bool:
    """Check if version follows semantic versioning (x.y.z)."""
    import re
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))

def check_forbidden_files(zip_file: zipfile.ZipFile) -> None:
    """Check for executable or forbidden file types."""
    forbidden_extensions = {'.exe', '.sh', '.bat', '.cmd', '.dll', '.so'}
    # Raise ValidationError if found
    pass
```

**Files Created**:
- `app/services/plugin/validation.py`

**Implements User Story**: Story 1 (acceptance: system validates plugin structure)

**Test Requirements**:
- [x] Test validation accepts valid plugin structure
- [x] Test validation rejects missing plugin.json
- [x] Test validation rejects malformed JSON
- [x] Test validation rejects missing required fields (name, version, description)
- [x] Test validation rejects invalid version format
- [x] Test validation rejects executable files
- [x] Test validation extracts correct metadata
- [x] Tests pass: `uv run pytest tests/test_plugin_validation.py -v`

**Verification Steps**:
1. Create test fixtures: valid and invalid plugin zips
2. Run validation tests
3. Expected: All validation rules enforced correctly

**Success Criteria**:
- [x] Validation functions implemented
- [x] All validation rules from design.md enforced
- [x] Clear error messages for each validation failure
- [x] Unit tests written and passing

#### 2.3 Implement File Storage Logic
**File**: `app/services/plugin/storage.py`
**Action**:
- Create functions to store plugin zips and metadata
- Implement directory structure: data/plugins/username/plugin-name/
- Store zip files: version.zip
- Extract and store metadata: metadata/version/plugin.json, README.md
- Handle file cleanup on errors

**Code Structure**:
```python
from pathlib import Path
import zipfile
import shutil
from typing import Dict

PLUGINS_DIR = Path("data/plugins")

def get_plugin_directory(username: str, plugin_name: str) -> Path:
    """Get or create plugin storage directory."""
    plugin_dir = PLUGINS_DIR / username / plugin_name
    plugin_dir.mkdir(parents=True, exist_ok=True)
    return plugin_dir

def store_plugin_zip(
    zip_path: Path,
    username: str,
    plugin_name: str,
    version: str
) -> Path:
    """
    Store plugin zip file in permanent location.
    
    Returns:
        Path to stored zip file
    """
    plugin_dir = get_plugin_directory(username, plugin_name)
    dest_path = plugin_dir / f"{version}.zip"
    shutil.copy(zip_path, dest_path)
    return dest_path

def extract_plugin_metadata(
    zip_path: Path,
    username: str,
    plugin_name: str,
    version: str
) -> Dict:
    """
    Extract plugin.json and README.md to metadata directory.
    
    Returns:
        Dict with extracted metadata including readme_content
    """
    plugin_dir = get_plugin_directory(username, plugin_name)
    metadata_dir = plugin_dir / "metadata" / version
    metadata_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract plugin.json and README.md
    # Return metadata dict
    pass

def delete_plugin_files(username: str, plugin_name: str) -> None:
    """Delete all files for a plugin (when unpublished)."""
    plugin_dir = PLUGINS_DIR / username / plugin_name
    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)
```

**Files Created**:
- `app/services/plugin/storage.py`

**Test Requirements**:
- [x] Test store_plugin_zip creates correct directory structure
- [x] Test extract_plugin_metadata extracts files correctly
- [x] Test metadata extraction reads README.md if present
- [x] Test cleanup deletes files correctly
- [x] Test storage handles missing data/plugins directory
- [x] Tests pass: `uv run pytest tests/test_plugin_storage.py -v`

**Verification Steps**:
1. Run storage tests with temp directories
2. Verify file structure matches design.md
3. Expected: Files stored in correct locations

**Success Criteria**:
- [x] Storage functions implemented
- [x] Directory structure matches design.md
- [x] Error handling for file operations
- [x] Unit tests written and passing

#### 2.4 Create Plugin Upload Form and Route
**Files**: 
- `app/services/plugin/routes.py`
- `app/services/plugin/templates/upload.html`

**Action**:
- Create upload form (file input, optional plugin name field)
- Implement POST /plugins/upload endpoint
- Handle multipart file upload
- Validate uploaded zip file
- Create Plugin and PluginVersion records
- Store files using storage.py
- Redirect to plugin detail page with success message

**Implements User Story**: Story 1 (acceptance: upload plugin directory as zip, system validates, plugin appears in marketplace)

**Code Structure**:
```python
from fastapi import APIRouter, Request, File, UploadFile, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.services.auth.dependencies import require_auth
from app.services.auth.models import User
from app.services.plugin.models import Plugin, PluginVersion
from app.services.plugin.validation import validate_plugin_zip, ValidationError
from app.services.plugin.storage import store_plugin_zip, extract_plugin_metadata
from pathlib import Path
import tempfile
import shutil

router = APIRouter(prefix="/plugins", tags=["plugins"])
templates = Jinja2Templates(directory="app/services/plugin/templates")

@router.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request, user: User = Depends(require_auth)):
    return templates.TemplateResponse("upload.html", {"request": request, "user": user})

@router.post("/upload")
async def upload_plugin(
    request: Request,
    file: UploadFile = File(...),
    plugin_name: str = Form(""),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    # Save uploaded file to temp location
    # Validate plugin zip
    # Check for duplicate plugin name from this user
    # Create Plugin and PluginVersion records
    # Store files permanently
    # Redirect to plugin detail page
    pass
```

**Template Structure** (upload.html):
- Extend base.html
- Form with enctype="multipart/form-data"
- File input for zip file
- Optional text input for plugin name
- Requirements checklist display
- Submit button
- Error display area

**Edge Cases from Requirements**:
- Missing plugin.json → Show error with path
- Malformed JSON → Show specific JSON error
- Duplicate plugin name → Show error
- Upload failure → Show error, rollback

**Test Requirements**:
- [ ] Test upload with valid plugin succeeds
- [ ] Test upload creates Plugin and PluginVersion records
- [ ] Test upload stores files in correct location
- [ ] Test upload extracts and stores metadata
- [ ] Test upload rejects invalid plugin structure
- [ ] Test upload rejects duplicate plugin name
- [ ] Test upload redirects to plugin detail on success
- [ ] Test upload requires authentication
- [ ] Tests pass: `uv run pytest tests/test_plugin_upload.py -v`

**Verification Steps**:
1. Run upload tests
2. Manual test: Login, visit /plugins/upload, upload valid plugin
3. Check database: `sqlite3 data/app.db "SELECT * FROM plugins;"`
4. Check file system: `ls -la data/plugins/`
5. Expected: Plugin created, files stored, redirect works

**Success Criteria**:
- [x] Upload form renders correctly
- [x] Upload endpoint handles multipart file upload
- [x] Validation integrated and working
- [x] Files stored correctly
- [x] Database records created
- [x] Tests written and passing
- [ ] Manual verification successful

#### 2.5 Add Version Management for Updates
**File**: `app/services/plugin/routes.py` (extend)
**Action**:
- Add logic to detect if plugin already exists
- Compare versions (reject downgrades)
- Update is_latest flag (set old to False, new to True)
- Update Plugin.updated_at timestamp

**Implements User Story**: Story 2 (upload new version of existing plugin)

**Code Changes**:
In upload_plugin function:
```python
# Check if plugin exists
existing_plugin = db.query(Plugin).filter(
    Plugin.author_id == user.id,
    Plugin.name == plugin_name
).first()

if existing_plugin:
    # Check version is higher than latest
    latest_version = db.query(PluginVersion).filter(
        PluginVersion.plugin_id == existing_plugin.id,
        PluginVersion.is_latest == True
    ).first()
    
    if latest_version:
        # Compare versions
        if not is_version_higher(new_version, latest_version.version):
            raise HTTPException(400, "Version must be higher than current")
        
        # Update is_latest flags
        latest_version.is_latest = False
    
    # Create new version for existing plugin
    plugin = existing_plugin
else:
    # Create new plugin
    plugin = Plugin(...)
```

**Test Requirements**:
- [ ] Test uploading new version updates is_latest flag
- [ ] Test uploading lower version fails with error
- [ ] Test version comparison works correctly (1.0.0 < 1.0.1 < 1.1.0)
- [ ] Test updated_at timestamp updates
- [ ] Tests pass: `uv run pytest tests/test_plugin_upload.py::test_version_management -v`

**Verification Steps**:
1. Run version management tests
2. Manual test: Upload v1.0.0, then v1.0.1
3. Check database: verify is_latest flags
4. Expected: Version updates work correctly

**Success Criteria**:
- [x] Version comparison logic implemented
- [x] is_latest flag management working
- [x] Downgrade prevention working
- [x] Tests written and passing

#### 2.6 Create "My Plugins" Management Page
**Files**: 
- `app/services/plugin/routes.py` (add route)
- `app/services/plugin/templates/my_plugins.html`

**Action**:
- Create GET /plugins/my-plugins page
- List all plugins owned by authenticated user
- Show plugin name, latest version, status (Published/Unpublished)
- Add "Upload New Version" button for each plugin
- Add "Upload New Plugin" button at top

**Implements User Story**: Story 2 (view all my published plugins)

**Code Structure**:
```python
@router.get("/my-plugins", response_class=HTMLResponse)
async def my_plugins(
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    plugins = db.query(Plugin).filter(Plugin.author_id == user.id).all()
    
    # Get latest version for each plugin
    plugin_data = []
    for plugin in plugins:
        latest = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin.id,
            PluginVersion.is_latest == True
        ).first()
        plugin_data.append({
            "plugin": plugin,
            "latest_version": latest
        })
    
    return templates.TemplateResponse("my_plugins.html", {
        "request": request,
        "user": user,
        "plugin_data": plugin_data
    })
```

**Template Structure** (my_plugins.html):
- Extend base.html
- Table with columns: Name, Version, Status, Actions
- Each row has link to plugin detail and "Upload New Version" button
- Empty state: "You haven't uploaded any plugins yet"

**Test Requirements**:
- [x] Test page shows user's plugins only
- [x] Test page shows latest version for each plugin
- [x] Test page shows empty state when no plugins
- [x] Test page requires authentication
- [x] Tests pass: `uv run pytest tests/test_plugin.py::test_my_plugins -v`

**Verification Steps**:
1. Run tests
2. Manual test: Upload 2 plugins, visit /plugins/my-plugins
3. Expected: Both plugins listed with correct info

**Success Criteria**:
- [x] My Plugins page renders correctly
- [x] Shows user's plugins with latest version
- [x] Empty state displays when no plugins
- [x] Tests written and passing

---

## Phase 3: Plugin Discovery & Browsing

### Overview
Build public-facing pages for browsing, searching, and viewing plugin details so users can discover plugins without authentication.

### Tasks

#### 3.1 Update Homepage with Plugin Listing
**Files**: 
- `app/shared/templates/home.html` (modify)
- `main.py` (update route)

**Action**:
- Transform homepage to show plugin grid/list
- Display all published plugins (is_published=True)
- Show plugin card with: name, author, latest version, description
- Implement pagination (30 per page)
- Add search box (form submission for now)
- Add sort dropdown (Newest first, Alphabetical)

**Implements User Story**: Story 3 (browse available plugins)

**Code Changes in main.py**:
```python
@app.get("/", response_class=HTMLResponse)
async def homepage(
    request: Request,
    page: int = 1,
    search: str = "",
    sort: str = "newest",
    db: Session = Depends(get_db)
):
    # Base query: published plugins only
    query = db.query(Plugin).filter(Plugin.is_published == True)
    
    # Apply search filter
    if search:
        query = query.filter(
            (Plugin.name.ilike(f"%{search}%")) |
            (Plugin.description.ilike(f"%{search}%"))
        )
    
    # Apply sorting
    if sort == "alphabetical":
        query = query.order_by(Plugin.name)
    else:  # newest
        query = query.order_by(Plugin.created_at.desc())
    
    # Pagination
    per_page = 30
    offset = (page - 1) * per_page
    plugins = query.offset(offset).limit(per_page).all()
    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    
    # Get latest version for each plugin
    plugin_data = []
    for plugin in plugins:
        latest = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin.id,
            PluginVersion.is_latest == True
        ).first()
        plugin_data.append({
            "plugin": plugin,
            "latest_version": latest,
            "author": plugin.author
        })
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "plugin_data": plugin_data,
        "page": page,
        "total_pages": total_pages,
        "search": search,
        "sort": sort,
        "total": total
    })
```

**Template Changes** (home.html):
- Hero section: "Discover Claude Code Plugins"
- Search form with text input and submit button
- Sort dropdown
- Plugin count display
- Grid of plugin cards (3 columns on desktop)
- Pagination controls at bottom
- Empty state: "No plugins yet. Be the first to upload!"

**Edge Cases from Requirements**:
- Zero plugins → Show empty state
- Search returns no results → Show "No plugins found matching..."
- Pagination beyond last page → Show last page

**Test Requirements**:
- [x] Test homepage shows published plugins only
- [x] Test homepage excludes unpublished plugins
- [x] Test search filters by name and description
- [x] Test sort by newest works
- [x] Test sort alphabetically works
- [x] Test pagination works correctly
- [x] Test empty state displays when no plugins
- [x] Test search with no results shows message
- [x] Tests pass: `uv run pytest tests/test_plugin.py::test_homepage -v`

**Verification Steps**:
1. Run homepage tests
2. Manual test: Visit /, try search, try sorting, try pagination
3. Expected: All features work smoothly

**Success Criteria**:
- [x] Homepage displays plugin grid
- [x] Search filters plugins correctly
- [x] Sorting works
- [x] Pagination works
- [x] Empty states handled
- [x] Tests written and passing

#### 3.2 Add Python Markdown Dependency and Rendering
**Action**:
- Add python-markdown to dependencies
- Create markdown rendering utility function

**Command**:
```bash
uv add "python-markdown>=3.7"
```

**File**: `app/services/plugin/utils.py` (create)
**Code**:
```python
import markdown
from markupsafe import Markup

def render_markdown(content: str | None) -> Markup:
    """
    Render markdown to HTML safely.
    
    Returns escaped HTML wrapped in Markup for Jinja2.
    """
    if not content:
        return Markup("")
    
    html = markdown.markdown(
        content,
        extensions=['fenced_code', 'tables', 'nl2br'],
        output_format='html5'
    )
    return Markup(html)
```

**Test Requirements**:
- [x] Test markdown renders headings correctly
- [x] Test markdown renders code blocks correctly
- [x] Test markdown renders links correctly
- [x] Test markdown escapes HTML tags (safety)
- [x] Test None input returns empty string
- [x] Tests pass: `uv run pytest tests/test_plugin.py::test_markdown -v`

**Verification Steps**:
1. Install python-markdown
2. Run markdown tests
3. Expected: Markdown renders safely

**Success Criteria**:
- [x] python-markdown added to dependencies
- [x] Markdown rendering function implemented
- [x] Safe HTML escaping working
- [x] Tests written and passing

#### 3.3 Create Plugin Detail Page
**Files**: 
- `app/services/plugin/routes.py` (add route)
- `app/services/plugin/templates/detail.html`

**Action**:
- Create GET /plugins/@{username}/{plugin_name} route
- Display comprehensive plugin information
- Show installation instructions with copy button
- Render README markdown
- List components (count commands, agents, skills, hooks, mcp_servers)
- Show version history (all versions, latest marked)
- Add Download ZIP button
- Add Report button (placeholder for Phase 5)

**Implements User Story**: Story 4 (view detailed plugin information)

**Code Structure**:
```python
@router.get("/@{username}/{plugin_name}", response_class=HTMLResponse)
async def plugin_detail(
    username: str,
    plugin_name: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # Find plugin by username and name
    author = db.query(User).filter(User.username == username).first()
    if not author:
        raise HTTPException(404, "User not found")
    
    plugin = db.query(Plugin).filter(
        Plugin.author_id == author.id,
        Plugin.name == plugin_name
    ).first()
    if not plugin or not plugin.is_published:
        raise HTTPException(404, "Plugin not found")
    
    # Get all versions, sorted newest first
    versions = db.query(PluginVersion).filter(
        PluginVersion.plugin_id == plugin.id
    ).order_by(PluginVersion.uploaded_at.desc()).all()
    
    latest = next((v for v in versions if v.is_latest), None)
    
    # Extract component counts from metadata
    components = latest.metadata.get("components", {}) if latest else {}
    
    # Render README
    readme_html = render_markdown(latest.readme_content) if latest else None
    
    return templates.TemplateResponse("detail.html", {
        "request": request,
        "plugin": plugin,
        "author": author,
        "latest_version": latest,
        "versions": versions,
        "components": components,
        "readme_html": readme_html,
        "marketplace_url": f"{request.base_url}marketplace.json",
        "install_command": f"/plugin install {username}-{plugin_name}"
    })
```

**Template Structure** (detail.html):
- Plugin header: name, author, version, upload date
- Action buttons: Download ZIP, Report
- Installation section with commands:
  - `/plugin marketplace add {url}/marketplace.json`
  - `/plugin install username-pluginname`
  - Copy button for each command
- Description section
- README section (rendered markdown)
- Components section (list counts)
- Version history section (collapsible list)

**Edge Cases from Requirements**:
- No README → Don't show README section
- Malformed markdown → Render safely, no crashes
- No components → Show "No standard components detected"

**Test Requirements**:
- [ ] Test plugin detail page renders correctly
- [ ] Test 404 for non-existent plugin
- [ ] Test 404 for unpublished plugin
- [ ] Test README renders as HTML
- [ ] Test installation commands generate correctly
- [ ] Test component counts display
- [ ] Test version history shows all versions
- [ ] Test page accessible without authentication
- [ ] Tests pass: `uv run pytest tests/test_plugin.py::test_plugin_detail -v`

**Verification Steps**:
1. Run detail page tests
2. Manual test: Visit plugin detail page
3. Verify README renders with proper formatting
4. Expected: Page displays all information correctly

**Success Criteria**:
- [ ] Plugin detail page implemented
- [ ] README markdown rendering working
- [ ] Installation instructions displayed
- [ ] Version history displayed
- [ ] Component counts shown
- [ ] Tests written and passing

#### 3.4 Add Plugin Download Endpoint
**File**: `app/services/plugin/routes.py` (add route)
**Action**:
- Create GET /plugins/@{username}/{plugin_name}/download/{version} route
- Stream zip file as download
- Track download (optional: could add download count later)
- Handle missing files gracefully

**Implements User Story**: Story 4 (download ZIP button)

**Code Structure**:
```python
from fastapi.responses import FileResponse

@router.get("/@{username}/{plugin_name}/download/{version}")
async def download_plugin(
    username: str,
    plugin_name: str,
    version: str,
    db: Session = Depends(get_db)
):
    # Find plugin and version
    author = db.query(User).filter(User.username == username).first()
    if not author:
        raise HTTPException(404, "User not found")
    
    plugin = db.query(Plugin).filter(
        Plugin.author_id == author.id,
        Plugin.name == plugin_name
    ).first()
    if not plugin or not plugin.is_published:
        raise HTTPException(404, "Plugin not found")
    
    plugin_version = db.query(PluginVersion).filter(
        PluginVersion.plugin_id == plugin.id,
        PluginVersion.version == version
    ).first()
    if not plugin_version:
        raise HTTPException(404, "Version not found")
    
    # Return file
    file_path = Path(plugin_version.file_path)
    if not file_path.exists():
        raise HTTPException(404, "Plugin file not found")
    
    return FileResponse(
        path=file_path,
        filename=f"{plugin_name}-{version}.zip",
        media_type="application/zip"
    )
```

**Test Requirements**:
- [ ] Test download returns zip file
- [ ] Test download sets correct filename
- [ ] Test download handles missing file
- [ ] Test download 404s for unpublished plugin
- [ ] Test download 404s for non-existent version
- [ ] Tests pass: `uv run pytest tests/test_plugin.py::test_download -v`

**Verification Steps**:
1. Run download tests
2. Manual test: Click download button on plugin detail page
3. Verify zip downloads correctly
4. Expected: Download works, file is valid zip

**Success Criteria**:
- [ ] Download endpoint implemented
- [ ] File streaming working
- [ ] Error handling for missing files
- [ ] Tests written and passing

#### 3.5 Update User Profile Page with Plugins
**File**: `app/services/auth/routes.py` (update profile route)
**Action**:
- Query user's published plugins
- Display plugin cards on profile page
- Link to each plugin detail page

**Code Changes**:
```python
@router.get("/users/@{username}", response_class=HTMLResponse)
async def user_profile(
    username: str,
    request: Request,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's published plugins
    plugins = db.query(Plugin).filter(
        Plugin.author_id == user.id,
        Plugin.is_published == True
    ).all()
    
    # Get latest version for each
    plugin_data = []
    for plugin in plugins:
        latest = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin.id,
            PluginVersion.is_latest == True
        ).first()
        plugin_data.append({
            "plugin": plugin,
            "latest_version": latest
        })
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile_user": user,
        "plugin_data": plugin_data
    })
```

**Test Requirements**:
- [ ] Test profile shows user's published plugins
- [ ] Test profile hides unpublished plugins
- [ ] Test profile shows empty state when user has no plugins
- [ ] Tests pass: `uv run pytest tests/test_auth.py::test_profile_with_plugins -v`

**Verification Steps**:
1. Run profile tests
2. Manual test: Visit user profile with plugins
3. Expected: Plugins display correctly

**Success Criteria**:
- [ ] Profile page shows published plugins
- [ ] Empty state handled
- [ ] Tests written and passing

---

## Phase 4: Marketplace Integration & Version Management

### Overview
Generate marketplace.json file compatible with Claude Code, enable plugin installation via `/plugin marketplace add` command, and ensure version management works correctly.

### Tasks

#### 4.1 Implement marketplace.json Generation
**File**: `app/services/plugin/marketplace.py`
**Action**:
- Create function to generate marketplace.json
- Query all published plugins with latest versions
- Build JSON structure per design.md schema
- Write to app/static/marketplace.json atomically (temp file + rename)
- Call this function after every plugin publish/unpublish/update

**Code Structure**:
```python
import json
from pathlib import Path
from typing import Dict, List
from sqlalchemy.orm import Session
from app.services.plugin.models import Plugin, PluginVersion

MARKETPLACE_FILE = Path("app/static/marketplace.json")

def generate_marketplace_json(db: Session) -> None:
    """
    Generate marketplace.json file with all published plugins.
    
    Uses atomic write (temp file + rename) for safety.
    """
    # Query all published plugins
    plugins = db.query(Plugin).filter(Plugin.is_published == True).all()
    
    plugin_entries = []
    for plugin in plugins:
        # Get latest version
        latest = db.query(PluginVersion).filter(
            PluginVersion.plugin_id == plugin.id,
            PluginVersion.is_latest == True
        ).first()
        
        if not latest:
            continue  # Skip if no latest version
        
        # Build plugin entry
        entry = {
            "name": f"{plugin.author.username}-{plugin.name}",
            "displayName": plugin.display_name,
            "description": plugin.description,
            "version": latest.version,
            "author": plugin.author.username,
            "downloadUrl": f"https://yoursite.com/plugins/@{plugin.author.username}/{plugin.name}/download/{latest.version}",
            "homepage": f"https://yoursite.com/plugins/@{plugin.author.username}/{plugin.name}",
            "metadata": {
                "components": latest.metadata.get("components", {})
            }
        }
        plugin_entries.append(entry)
    
    # Build marketplace structure
    marketplace = {
        "marketplaceId": "claude-plugin-marketplace",
        "name": "Claude Plugin Marketplace",
        "description": "Community-driven marketplace for Claude Code plugins",
        "version": "1.0.0",
        "plugins": plugin_entries
    }
    
    # Atomic write
    MARKETPLACE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_file = MARKETPLACE_FILE.with_suffix('.tmp')
    with open(temp_file, 'w') as f:
        json.dump(marketplace, f, indent=2)
    temp_file.rename(MARKETPLACE_FILE)
```

**Files Created**:
- `app/services/plugin/marketplace.py`
- `app/static/marketplace.json` (generated file)

**Implements User Story**: Story 5 (marketplace.json accessible at public URL)

**Test Requirements**:
- [ ] Test generation creates valid JSON file
- [ ] Test JSON contains all published plugins
- [ ] Test JSON excludes unpublished plugins
- [ ] Test JSON follows schema from design.md
- [ ] Test atomic write (temp file created first)
- [ ] Test empty marketplace (no plugins) produces valid JSON
- [ ] Tests pass: `uv run pytest tests/test_marketplace.py -v`

**Verification Steps**:
1. Run marketplace generation tests
2. Manually trigger generation and inspect file
3. Validate JSON schema: `python -m json.tool app/static/marketplace.json`
4. Expected: Valid JSON with correct structure

**Success Criteria**:
- [ ] marketplace.json generation implemented
- [ ] JSON schema matches design.md
- [ ] Atomic writes working
- [ ] Tests written and passing

#### 4.2 Integrate marketplace.json Generation into Upload Flow
**File**: `app/services/plugin/routes.py` (update upload route)
**Action**:
- Import generate_marketplace_json
- Call it after successful plugin upload
- Call it after version update
- Handle generation errors gracefully

**Code Changes**:
```python
from app.services.plugin.marketplace import generate_marketplace_json

@router.post("/upload")
async def upload_plugin(...):
    # ... existing upload logic ...
    
    # After successful plugin creation/update
    try:
        generate_marketplace_json(db)
    except Exception as e:
        # Log error but don't fail the upload
        print(f"Failed to generate marketplace.json: {e}")
    
    return RedirectResponse(f"/plugins/@{user.username}/{plugin_name}", status_code=303)
```

**Test Requirements**:
- [ ] Test upload triggers marketplace.json regeneration
- [ ] Test marketplace.json updates with new plugin
- [ ] Test upload succeeds even if generation fails
- [ ] Tests pass: `uv run pytest tests/test_plugin_upload.py::test_marketplace_integration -v`

**Verification Steps**:
1. Run integration tests
2. Manual test: Upload plugin, check marketplace.json updated
3. Expected: marketplace.json regenerates after each upload

**Success Criteria**:
- [ ] marketplace.json regenerates on upload
- [ ] Error handling prevents upload failures
- [ ] Tests written and passing

#### 4.3 Create marketplace.json Static File Endpoint
**File**: `main.py`
**Action**:
- Mount app/static directory to serve static files
- Ensure marketplace.json is accessible at /marketplace.json
- Set appropriate cache headers

**Code Changes**:
```python
from fastapi.staticfiles import StaticFiles

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Alternatively, create explicit route for marketplace.json with cache control
@app.get("/marketplace.json")
async def get_marketplace():
    from fastapi.responses import FileResponse
    return FileResponse(
        "app/static/marketplace.json",
        media_type="application/json",
        headers={"Cache-Control": "public, max-age=60"}  # Cache for 1 minute
    )
```

**Implements User Story**: Story 5 (marketplace.json accessible at public URL)

**Test Requirements**:
- [ ] Test /marketplace.json returns valid JSON
- [ ] Test /marketplace.json is publicly accessible (no auth)
- [ ] Test content-type is application/json
- [ ] Tests pass: `uv run pytest tests/test_marketplace.py::test_endpoint -v`

**Verification Steps**:
1. Run endpoint tests
2. Manual test: Visit http://localhost:8000/marketplace.json
3. Expected: JSON downloads/displays correctly

**Success Criteria**:
- [ ] marketplace.json endpoint working
- [ ] Publicly accessible
- [ ] Proper content-type headers
- [ ] Tests written and passing

#### 4.4 Test Claude Code Integration (Manual)
**Action**:
- Start local server: `uv run uvicorn main:app --reload`
- Upload a test plugin via web interface
- Open Claude Code
- Run: `/plugin marketplace add http://localhost:8000/marketplace.json`
- Verify marketplace appears in Claude Code
- Run: `/plugin install username-pluginname@localhost`
- Verify plugin downloads and installs

**Implements User Story**: Story 5 (install plugin via Claude Code)

**Verification Steps**:
1. Upload test plugin through web UI
2. Add marketplace in Claude Code
3. List plugins: `/plugin` - should show marketplace plugins
4. Install plugin: `/plugin install username-testplugin@localhost`
5. Verify plugin installed: check `.claude/plugins/` directory
6. Expected: Full integration works end-to-end

**Success Criteria**:
- [ ] Marketplace adds successfully in Claude Code
- [ ] Plugins appear in plugin list
- [ ] Plugin installs successfully
- [ ] Plugin works in Claude Code (manual verification)
- [ ] Document any issues discovered

#### 4.5 Extract and Store Component Counts
**File**: `app/services/plugin/storage.py` (update extract_plugin_metadata)
**Action**:
- When extracting metadata, scan plugin directories
- Count files in: commands/, agents/, skills/, hooks/, mcp_servers/
- Store counts in metadata JSON
- Use in marketplace.json generation

**Code Changes**:
```python
def extract_plugin_metadata(zip_path: Path, username: str, plugin_name: str, version: str) -> Dict:
    """Extract metadata and count components."""
    # ... existing extraction logic ...
    
    # Count components in zip
    with zipfile.ZipFile(zip_path) as zf:
        components = {
            "commands": count_files_in_dir(zf, "commands/"),
            "agents": count_files_in_dir(zf, "agents/"),
            "skills": count_files_in_dir(zf, "skills/"),
            "hooks": count_files_in_dir(zf, "hooks/"),
            "mcp_servers": count_files_in_dir(zf, "mcp_servers/")
        }
    
    # Add to metadata
    plugin_json["components"] = components
    
    return {
        "plugin_json": plugin_json,
        "readme_content": readme_content,
        "components": components
    }

def count_files_in_dir(zip_file: zipfile.ZipFile, directory: str) -> int:
    """Count files (not dirs) in a directory within zip."""
    count = 0
    for name in zip_file.namelist():
        if name.startswith(directory) and not name.endswith('/'):
            count += 1
    return count
```

**Test Requirements**:
- [ ] Test component counting extracts correct counts
- [ ] Test components stored in metadata JSON
- [ ] Test components appear in marketplace.json
- [ ] Test components appear on plugin detail page
- [ ] Tests pass: `uv run pytest tests/test_plugin_storage.py::test_component_counting -v`

**Verification Steps**:
1. Run component counting tests
2. Upload plugin with known component structure
3. Check metadata JSON has component counts
4. Check detail page displays counts
5. Expected: Counts accurate and displayed

**Success Criteria**:
- [ ] Component counting implemented
- [ ] Counts stored in metadata
- [ ] Counts displayed on detail page
- [ ] Tests written and passing

---

## Phase 5: Moderation System & Admin Dashboard

### Overview
Implement plugin reporting and admin moderation features so community can flag problematic plugins and admins can take action.

### Tasks

#### 5.1 Create Report Model and Migration
**File**: `app/services/report/models.py`
**Action**:
- Create report service directory structure
- Implement Report model from design.md
- Generate migration

**Code Structure**:
```python
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.shared.database import Base

class Report(Base):
    __tablename__ = "reports"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("plugins.id"), nullable=False)
    reason: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    reporter_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    plugin = relationship("Plugin", backref="reports")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
```

**Files Created**:
- `app/services/report/__init__.py`
- `app/services/report/models.py`
- Migration file: `migrations/versions/[hash]_add_reports_table.py`

**Test Requirements**:
- [ ] Test Report model creates successfully
- [ ] Test relationships with Plugin and User
- [ ] Test default values (status=pending, reported_at auto-set)
- [ ] Tests pass: `uv run pytest tests/test_report.py::test_report_model -v`

**Verification Steps**:
1. Generate migration: `uv run alembic revision --autogenerate -m "Add reports table"`
2. Apply migration: `uv run alembic upgrade head`
3. Verify table: `sqlite3 data/app.db ".schema reports"`
4. Run model tests
5. Expected: Reports table created with indexes and foreign keys

**Success Criteria**:
- [ ] Report model implemented
- [ ] Migration generated and applied
- [ ] Database table created
- [ ] Model tests written and passing

#### 5.2 Create Report Submission Form and Route
**Files**: 
- `app/services/report/routes.py`
- `app/services/report/templates/report_modal.html`

**Action**:
- Create POST /plugins/@{username}/{plugin_name}/report endpoint
- Accept reason dropdown and optional details
- Capture reporter IP address
- Implement rate limiting (5 reports per hour per IP)
- Check for duplicate reports (same IP, same plugin, within 24h)
- Show confirmation after submission

**Implements User Story**: Story 6 (report problematic plugin)

**Code Structure**:
```python
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.services.report.models import Report
from app.services.plugin.models import Plugin
from app.services.auth.models import User
from datetime import datetime, timedelta

router = APIRouter(prefix="/plugins", tags=["reports"])

@router.post("/@{username}/{plugin_name}/report")
async def submit_report(
    username: str,
    plugin_name: str,
    request: Request,
    reason: str = Form(...),
    details: str = Form(""),
    db: Session = Depends(get_db)
):
    # Get client IP
    client_ip = request.client.host
    
    # Find plugin
    author = db.query(User).filter(User.username == username).first()
    if not author:
        raise HTTPException(404, "User not found")
    
    plugin = db.query(Plugin).filter(
        Plugin.author_id == author.id,
        Plugin.name == plugin_name
    ).first()
    if not plugin:
        raise HTTPException(404, "Plugin not found")
    
    # Check rate limit (5 per hour per IP)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_reports = db.query(Report).filter(
        Report.reporter_ip == client_ip,
        Report.reported_at >= one_hour_ago
    ).count()
    
    if recent_reports >= 5:
        raise HTTPException(429, "Too many reports. Please try again later.")
    
    # Check for duplicate (same IP, same plugin, within 24h)
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    duplicate = db.query(Report).filter(
        Report.plugin_id == plugin.id,
        Report.reporter_ip == client_ip,
        Report.reported_at >= one_day_ago
    ).first()
    
    if duplicate:
        raise HTTPException(400, "You've already reported this plugin recently.")
    
    # Create report
    report = Report(
        plugin_id=plugin.id,
        reason=reason,
        details=details,
        reporter_ip=client_ip
    )
    db.add(report)
    db.commit()
    
    # Redirect back to plugin with success message
    return RedirectResponse(
        f"/plugins/@{username}/{plugin_name}?report_success=1",
        status_code=303
    )
```

**Update Plugin Detail Template**:
- Add Report button/modal
- Report form with reason dropdown and details textarea
- Reason options: "Broken/Non-functional", "Malicious/Suspicious", "Inappropriate content", "Copyright violation", "Other"
- Show success message if report_success=1 in query params

**Edge Cases from Requirements**:
- Spam reports → Rate limiting prevents abuse
- Multiple reports of same plugin → Allow but within limits
- No authentication required → Use IP for tracking

**Test Requirements**:
- [ ] Test report submission creates Report record
- [ ] Test report captures IP address
- [ ] Test rate limiting prevents spam (6th report in hour fails)
- [ ] Test duplicate detection (same IP, plugin, within 24h)
- [ ] Test report works without authentication
- [ ] Test report redirects with success message
- [ ] Tests pass: `uv run pytest tests/test_report.py::test_report_submission -v`

**Verification Steps**:
1. Run report submission tests
2. Manual test: Visit plugin detail, click Report, submit form
3. Check database: `sqlite3 data/app.db "SELECT * FROM reports;"`
4. Try submitting 6 reports rapidly, verify rate limit
5. Expected: Reports created, rate limiting works

**Success Criteria**:
- [ ] Report submission endpoint implemented
- [ ] Rate limiting working
- [ ] Duplicate detection working
- [ ] IP tracking working
- [ ] Tests written and passing

#### 5.3 Create Admin Dashboard
**Files**: 
- `app/services/report/routes.py` (add route)
- `app/services/report/templates/admin_dashboard.html`

**Action**:
- Create GET /admin/reports route (admin only)
- List all pending reports
- Show report details: plugin name, author, reason, details, date
- Add action buttons: View Plugin, Unpublish, Dismiss
- Sort by newest first

**Implements User Story**: Story 7 (admin reviews reports)

**Code Structure**:
```python
from app.services.auth.dependencies import require_admin

@router.get("/admin/reports", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Get all pending reports
    reports = db.query(Report).filter(
        Report.status == "pending"
    ).order_by(Report.reported_at.desc()).all()
    
    # Enrich with plugin and author info
    report_data = []
    for report in reports:
        plugin = report.plugin
        author = plugin.author
        report_data.append({
            "report": report,
            "plugin": plugin,
            "author": author
        })
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "user": user,
        "report_data": report_data
    })
```

**Template Structure** (admin_dashboard.html):
- Page title: "Admin Dashboard - Reported Plugins"
- Count of pending reports
- Table with columns: Report ID, Plugin, Author, Reason, Date, Actions
- Actions: View Plugin (link), Unpublish (button), Dismiss (button)
- Empty state: "No pending reports"

**Test Requirements**:
- [ ] Test admin dashboard requires admin privileges
- [ ] Test non-admin gets 403 error
- [ ] Test dashboard shows pending reports only
- [ ] Test dashboard shows report details correctly
- [ ] Test empty state when no reports
- [ ] Tests pass: `uv run pytest tests/test_report.py::test_admin_dashboard -v`

**Verification Steps**:
1. Run admin dashboard tests
2. Create admin user: set is_admin=True in database
3. Login as admin, visit /admin/reports
4. Expected: Dashboard displays pending reports

**Success Criteria**:
- [ ] Admin dashboard implemented
- [ ] Admin-only access enforced
- [ ] Reports display correctly
- [ ] Empty state handled
- [ ] Tests written and passing

#### 5.4 Implement Plugin Unpublish Action
**File**: `app/services/report/routes.py` (add route)
**Action**:
- Create POST /admin/reports/{report_id}/unpublish route
- Set Plugin.is_published = False
- Set Report.status = "resolved"
- Set Report.reviewed_by and reviewed_at
- Regenerate marketplace.json (exclude unpublished)
- Show confirmation message

**Implements User Story**: Story 7 (unpublish plugin to remove from marketplace)

**Code Structure**:
```python
@router.post("/admin/reports/{report_id}/unpublish")
async def unpublish_plugin(
    report_id: int,
    request: Request,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Find report
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    
    # Unpublish plugin
    plugin = report.plugin
    plugin.is_published = False
    
    # Mark report as resolved
    report.status = "resolved"
    report.reviewed_by = user.id
    report.reviewed_at = datetime.utcnow()
    
    db.commit()
    
    # Regenerate marketplace.json
    try:
        generate_marketplace_json(db)
    except Exception as e:
        print(f"Failed to regenerate marketplace.json: {e}")
    
    return RedirectResponse("/admin/reports?unpublish_success=1", status_code=303)
```

**Edge Cases from Requirements**:
- Plugin already unpublished → Disable button, show message
- Creator re-upload → Allow (creator can upload again)

**Test Requirements**:
- [ ] Test unpublish sets is_published to False
- [ ] Test unpublish marks report as resolved
- [ ] Test unpublish sets reviewed_by and reviewed_at
- [ ] Test unpublish regenerates marketplace.json
- [ ] Test unpublished plugin removed from marketplace.json
- [ ] Test unpublish requires admin privileges
- [ ] Tests pass: `uv run pytest tests/test_report.py::test_unpublish -v`

**Verification Steps**:
1. Run unpublish tests
2. Manual test: Report plugin, login as admin, unpublish
3. Check database: plugin.is_published should be False
4. Check marketplace.json: plugin should be gone
5. Try visiting plugin detail page: should 404
6. Expected: Unpublish works correctly, plugin removed from public

**Success Criteria**:
- [ ] Unpublish action implemented
- [ ] Plugin hidden from marketplace
- [ ] Report marked as resolved
- [ ] marketplace.json regenerated
- [ ] Tests written and passing

#### 5.5 Implement Report Dismiss Action
**File**: `app/services/report/routes.py` (add route)
**Action**:
- Create POST /admin/reports/{report_id}/dismiss route
- Set Report.status = "dismissed"
- Set Report.reviewed_by and reviewed_at
- Don't change plugin publication status

**Code Structure**:
```python
@router.post("/admin/reports/{report_id}/dismiss")
async def dismiss_report(
    report_id: int,
    request: Request,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    
    report.status = "dismissed"
    report.reviewed_by = user.id
    report.reviewed_at = datetime.utcnow()
    
    db.commit()
    
    return RedirectResponse("/admin/reports?dismiss_success=1", status_code=303)
```

**Test Requirements**:
- [ ] Test dismiss marks report as dismissed
- [ ] Test dismiss sets reviewed_by and reviewed_at
- [ ] Test dismiss doesn't change plugin status
- [ ] Test dismiss requires admin privileges
- [ ] Tests pass: `uv run pytest tests/test_report.py::test_dismiss -v`

**Verification Steps**:
1. Run dismiss tests
2. Manual test: Dismiss a report
3. Verify report status changed but plugin still published
4. Expected: Dismiss works correctly

**Success Criteria**:
- [ ] Dismiss action implemented
- [ ] Report marked as dismissed
- [ ] Plugin status unchanged
- [ ] Tests written and passing

#### 5.6 Add Report Button to Plugin Detail Page
**File**: `app/services/plugin/templates/detail.html` (update)
**Action**:
- Add Report button next to Download button
- Show modal on click with report form
- Include CSRF protection if needed
- Show success message after submission

**Template Changes**:
- Add button: "Report Plugin"
- Modal with form (use Tailwind for styling)
- Form posts to /plugins/@{username}/{plugin_name}/report
- Success message if ?report_success=1

**Verification Steps**:
1. Manual test: Visit plugin detail, click Report
2. Fill form, submit
3. Verify modal closes, success message shows
4. Expected: Report flow works smoothly

**Success Criteria**:
- [ ] Report button added to detail page
- [ ] Report modal works
- [ ] Form submission works
- [ ] Success message displays
- [ ] Manual verification successful

---

## Phase 6: Polish, Testing & Deployment

### Overview
Final cleanup, comprehensive testing, error handling improvements, and deployment preparation.

### Tasks

#### 6.1 Add Configuration Management
**File**: `app/shared/config.py` (update)
**Action**:
- Add configuration for session secret key
- Add configuration for base URL (for marketplace.json URLs)
- Add configuration for file upload limits (optional, design says no limit)
- Use environment variables with defaults

**Code Structure**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///data/app.db"
    session_secret_key: str = "change-this-in-production"
    session_max_age: int = 30 * 24 * 60 * 60  # 30 days
    base_url: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**Files Created/Modified**:
- `app/shared/config.py` (update)
- `.env.example` (create with examples)
- Update main.py to use settings

**Verification Steps**:
1. Create .env file with custom values
2. Start app, verify settings loaded
3. Expected: Configuration works

**Success Criteria**:
- [ ] Configuration management implemented
- [ ] Environment variables supported
- [ ] Example .env created
- [ ] Settings used throughout app

#### 6.2 Improve Error Pages
**Files**: 
- `app/shared/templates/404.html` (update)
- `app/shared/templates/500.html` (update)

**Action**:
- Enhance 404 page with helpful links (home, search)
- Enhance 500 page with contact/report info
- Ensure error pages extend base.html
- Add error handlers in main.py

**Code in main.py**:
```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi import Request

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)
```

**Verification Steps**:
1. Visit non-existent route, verify 404 page
2. Trigger error (temporarily), verify 500 page
3. Expected: Error pages display correctly

**Success Criteria**:
- [ ] Error pages styled with Tailwind
- [ ] Error handlers registered
- [ ] Helpful error messages
- [ ] Manual verification successful

#### 6.3 Add Form Validation Messages
**Action**:
- Add client-side validation for required fields
- Add server-side validation error messages
- Display validation errors inline on forms
- Use flash messages for success/error notifications

**Files to Update**:
- `app/services/auth/templates/register.html`
- `app/services/auth/templates/login.html`
- `app/services/plugin/templates/upload.html`

**Template Changes**:
- Add error display blocks
- Style errors with Tailwind (red text, border)
- Add success message blocks (green)

**Verification Steps**:
1. Submit forms with invalid data
2. Verify error messages display
3. Submit valid data, verify success messages
4. Expected: Validation feedback clear and helpful

**Success Criteria**:
- [ ] Validation messages display correctly
- [ ] Error styling consistent
- [ ] Success messages show after actions
- [ ] Manual verification successful

#### 6.4 Add Loading States and UX Improvements
**Action**:
- Add loading spinner for file uploads
- Add "Copy to clipboard" functionality for installation commands
- Add tooltips for complex UI elements
- Improve responsive design for mobile

**File**: `app/static/js/main.js`
**Code**:
```javascript
// Copy to clipboard
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    alert('Copied to clipboard!');
  });
}

// Upload progress (if using fetch instead of form)
document.getElementById('upload-form')?.addEventListener('submit', (e) => {
  document.getElementById('upload-button').disabled = true;
  document.getElementById('upload-button').innerText = 'Uploading...';
});
```

**Verification Steps**:
1. Test copy button on plugin detail page
2. Test upload shows loading state
3. Test on mobile viewport
4. Expected: UX improvements work

**Success Criteria**:
- [ ] Copy to clipboard works
- [ ] Upload shows loading state
- [ ] Responsive design works on mobile
- [ ] Manual verification successful

#### 6.5 Run Complete Test Suite
**Action**:
- Run all tests with coverage report
- Fix any failing tests
- Ensure at least 80% code coverage on critical paths
- Review and update test fixtures

**Commands**:
```bash
uv run pytest -v
uv run pytest --cov=app --cov-report=html
```

**Verification Steps**:
1. Run full test suite
2. Review coverage report
3. Expected: All tests passing, high coverage

**Success Criteria**:
- [ ] All tests passing
- [ ] Coverage report generated
- [ ] Critical paths have >80% coverage
- [ ] No test warnings or deprecations

#### 6.6 Manual End-to-End Testing
**Action**:
- Test complete creator workflow: register → upload → update → manage
- Test complete user workflow: browse → search → view → report
- Test complete admin workflow: review → unpublish
- Test Claude Code integration: add marketplace → install plugin
- Test edge cases from requirements.md

**Test Scenarios**:
1. **Creator uploads first plugin**
   - Register new account
   - Upload valid plugin zip
   - Verify plugin appears on homepage
   - Verify profile shows plugin
   
2. **Creator updates plugin version**
   - Upload new version (higher version number)
   - Verify version history
   - Verify marketplace.json updated
   
3. **User discovers plugin**
   - Search for plugin
   - View detail page
   - Read README (with formatted markdown)
   - Copy installation command
   
4. **User installs in Claude Code**
   - Add marketplace
   - List plugins
   - Install plugin
   - Verify plugin works
   
5. **User reports plugin**
   - Submit report
   - Verify rate limiting (submit 6 times)
   
6. **Admin moderates**
   - Login as admin
   - View reports
   - Unpublish plugin
   - Verify plugin gone from homepage and marketplace.json

**Verification Steps**:
1. Execute each scenario
2. Document any issues
3. Fix critical bugs
4. Expected: All workflows work smoothly

**Success Criteria**:
- [ ] All user stories work end-to-end
- [ ] No critical bugs found
- [ ] Edge cases handled gracefully
- [ ] Claude Code integration works
- [ ] Manual testing complete

#### 6.7 Update README Documentation
**File**: `README.md`
**Action**:
- Update project description
- Add setup instructions (uv installation, database setup, running app)
- Document environment variables
- Add usage examples
- Document admin account creation
- Add contributing guidelines

**Content Structure**:
```markdown
# Claude Plugin Marketplace

Community-driven marketplace for Claude Code plugins.

## Features
- Plugin upload and management
- Browse and search plugins
- Claude Code integration via marketplace.json
- Plugin reporting and moderation

## Setup

### Prerequisites
- Python 3.12
- uv package manager

### Installation
1. Clone repository
2. Install dependencies: `uv sync`
3. Run migrations: `uv run alembic upgrade head`
4. Start server: `uv run uvicorn main:app --reload`

### Configuration
Create `.env` file (see `.env.example`):
- SESSION_SECRET_KEY: Random secret key
- BASE_URL: Your deployment URL

### Creating Admin User
```sql
sqlite3 data/app.db "UPDATE users SET is_admin=1 WHERE username='your-username';"
```

## Usage

### For Plugin Creators
1. Register account
2. Upload plugin zip (must contain .claude-plugin/plugin.json)
3. Manage plugins at /plugins/my-plugins

### For Plugin Users
1. Browse plugins at homepage
2. Search by name or description
3. Add marketplace to Claude Code:
   `/plugin marketplace add https://yoursite.com/marketplace.json`
4. Install plugins:
   `/plugin install username-pluginname`

## Development

### Running Tests
```bash
uv run pytest
uv run pytest --cov=app
```

### Database Migrations
```bash
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head
```

## License
MIT
```

**Verification Steps**:
1. Review README for completeness
2. Follow setup instructions on fresh clone
3. Expected: README accurate and helpful

**Success Criteria**:
- [ ] README updated with current information
- [ ] Setup instructions complete and tested
- [ ] Admin setup documented
- [ ] Usage examples clear

#### 6.8 Prepare Dockerfile and Deployment
**File**: `Dockerfile` (update if needed)
**Action**:
- Ensure Dockerfile uses Python 3.12
- Install uv in container
- Copy all necessary files
- Set up volume for data/ directory
- Expose port 8000
- Run migrations on startup

**Dockerfile Structure**:
```dockerfile
FROM python:3.12-slim

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY main.py alembic.ini ./

# Install dependencies
RUN uv sync --frozen

# Create data directory
RUN mkdir -p data/plugins

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn main:app --host 0.0.0.0 --port 8000"]
```

**Verification Steps**:
1. Build Docker image: `docker build -t plugin-marketplace .`
2. Run container: `docker run -p 8000:8000 -v $(pwd)/data:/app/data plugin-marketplace`
3. Test app in container
4. Expected: Container runs successfully

**Success Criteria**:
- [ ] Dockerfile builds successfully
- [ ] Container runs without errors
- [ ] Volumes configured correctly
- [ ] App accessible from host
- [ ] Migrations run on startup

---

## Verification Checklist

### Requirements Completion

#### User Story 1: Creator Uploads a Plugin
- [ ] Create account with email and password
- [ ] Log in to account
- [ ] Upload plugin directory as zip file
- [ ] System validates plugin structure (.claude-plugin/plugin.json)
- [ ] Plugin appears in marketplace immediately
- [ ] See confirmation of successful publish

#### User Story 2: Creator Manages Their Plugins
- [ ] See list of all my published plugins
- [ ] Upload new version of existing plugin
- [ ] Each plugin page shows version history
- [ ] See which version is currently "latest"
- [ ] View my public profile showing all plugins

#### User Story 3: User Discovers Plugins
- [ ] View homepage with all available plugins
- [ ] See plugin name, author, description, version
- [ ] Search plugins by text (name and description)
- [ ] Sort plugins by newest first or alphabetically
- [ ] Click on plugin to see detail page

#### User Story 4: User Views Plugin Details
- [ ] Plugin page shows name, author, description, version, upload date
- [ ] README.md content displayed with markdown rendering
- [ ] Plugin page lists components (counts)
- [ ] Installation instructions with copy-paste commands
- [ ] Download ZIP button works
- [ ] Version history displayed

#### User Story 5: User Installs Plugin via Claude Code
- [ ] marketplace.json accessible at public URL
- [ ] marketplace.json follows Claude Code schema
- [ ] Can add marketplace in Claude Code with `/plugin marketplace add`
- [ ] Can see marketplace plugins in `/plugin` list
- [ ] Can install plugin with `/plugin install plugin-name@marketplace-name`
- [ ] Plugin downloads and installs successfully

#### User Story 6: User Reports Problematic Plugin
- [ ] Each plugin page has "Report" button
- [ ] Report form shows with reason dropdown and details
- [ ] After submitting, see confirmation message
- [ ] Don't need account to report

#### User Story 7: Admin Reviews Reports
- [ ] Access admin dashboard (separate view)
- [ ] Dashboard shows all reported plugins with details
- [ ] Can unpublish plugin to remove from marketplace
- [ ] Unpublished plugins disappear from listings and marketplace.json

### Functional Requirements
- [x] FR1: User Authentication - Registration, login, logout, sessions
- [x] FR2: Plugin Upload - Authenticated users upload zip files
- [x] FR3: Plugin Validation - Structure and JSON validation
- [x] FR4: Plugin Storage - Files stored with stable download URLs
- [x] FR5: Marketplace JSON Generation - Claude Code-compatible JSON
- [x] FR6: Plugin Browsing - Public browse without auth
- [x] FR7: Plugin Search - Text search by name/description
- [x] FR8: Plugin Detail Page - Full information display
- [x] FR9: Version Management - Track history, mark latest
- [x] FR10: User Profiles - Public creator profiles
- [x] FR11: Report System - Submit and store reports
- [x] FR12: Admin Dashboard - Review and moderate

### Design Implementation
- [ ] All components from design.md implemented
- [ ] Data model matches design.md (User, Plugin, PluginVersion, Report)
- [ ] File structure matches design.md
- [ ] Tech stack matches design.md (FastAPI, SQLite, Tailwind, etc.)

### Quality Checks
- [ ] Code builds without errors: `uv run uvicorn main:app`
- [ ] Linter passes (if configured): `uv run ruff check .`
- [ ] Tests pass: `uv run pytest`
- [ ] Application runs: `uv run uvicorn main:app --reload`

### User Acceptance
- [ ] Manually tested all user flows
- [ ] Verified all edge cases from requirements.md
- [ ] Performance meets requirements (homepage <3s, search <1s)
- [ ] Security requirements met (password hashing, SQL injection prevention, XSS protection)

---

## Development Notes

### Suggested Order
1. Follow phases sequentially - each builds on previous
2. Run tests after completing each task before moving on
3. Do manual verification at phase boundaries
4. Update this plan document if you discover gaps in specs

### If You Get Stuck
- Review requirements.md for the "why" behind features
- Review design.md for the "how" and technical details
- Test incrementally - don't wait until end to test
- Ask questions if specs are unclear
- Document any assumptions made

### Testing Philosophy
- Write tests after implementing each feature
- Focus on integration tests (full request/response cycles)
- Manual testing for UI/UX aspects
- Tests must pass before marking task complete

### Git Workflow
- Commit frequently with clear messages
- Consider feature branches for each phase
- Test before merging to main
- Tag releases (v0.1.0, v0.2.0, v1.0.0)

## References
- **Requirements**: `spec/requirements.md`
- **Design**: `spec/design.md`
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Tailwind CSS**: https://tailwindcss.com/

