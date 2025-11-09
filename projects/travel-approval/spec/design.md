# Design: Travel Approval System

## Design Overview
A web-based travel approval system built with FastAPI (Python) serving server-side rendered HTML via Jinja2 templates, backed by SQLite for data persistence. The architecture follows a traditional MVC pattern with role-based access control, automatic request routing, and notification system for workflow management.

## Tech Stack

### Languages & Frameworks
- **Language**: Python 3.11+
- **Web Framework**: FastAPI 0.104+
- **Template Engine**: Jinja2 (bundled with FastAPI)
- **ASGI Server**: Uvicorn
- **Styling**: Tailwind CSS (via CDN for simplicity)

### Data & State
- **Database**: SQLite 3
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Session Management**: FastAPI sessions with signed cookies

### Dependencies
- **FastAPI**: Web framework with automatic API docs
- **SQLAlchemy**: Database ORM and query builder
- **Alembic**: Database migration tool
- **python-multipart**: Form data parsing
- **python-jose**: JWT token handling for session security
- **passlib**: Password hashing (bcrypt)
- **pydantic**: Data validation and settings management
- **pydantic-settings**: Environment configuration
- **jinja2**: Template rendering
- **itsdangerous**: Secure cookie signing (for sessions)
- **email-validator**: Email validation
- **httpx** (optional): For LLM API calls if implementing email integration

**Rationale**: FastAPI provides excellent performance for 500 concurrent users, automatic API documentation, and built-in Jinja2 support. SQLite is perfect for internal tools with moderate concurrency. This stack minimizes deployment complexity (single Python process, no separate database server needed) while meeting all performance requirements.

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────┐
│           Browser (User Interface)          │
│         (Server-Rendered HTML)              │
└─────────────────┬───────────────────────────┘
                  │ HTTP/HTTPS
┌─────────────────▼───────────────────────────┐
│         FastAPI Application Layer           │
│  ┌────────────────────────────────────┐    │
│  │  Routes (Path Operations)          │    │
│  │  - Auth, Travel Requests, Admin    │    │
│  └────────────┬───────────────────────┘    │
│  ┌────────────▼───────────────────────┐    │
│  │  Services (Business Logic)         │    │
│  │  - Request Routing, Notifications  │    │
│  └────────────┬───────────────────────┘    │
│  ┌────────────▼───────────────────────┐    │
│  │  Data Access Layer (SQLAlchemy)    │    │
│  └────────────┬───────────────────────┘    │
└───────────────┼─────────────────────────────┘
                │
┌───────────────▼─────────────────────────────┐
│         SQLite Database                     │
│  Tables: users, travel_requests, projects,  │
│          t_accounts, notifications          │
└─────────────────────────────────────────────┘
```

### Component Breakdown

#### Component: Authentication & Session Management
**Purpose**: Handle user login, session management, and role-based access control
**Location**: `app/auth/`
**Responsibilities**:
- User login/logout with secure password hashing
- Session creation and validation using signed cookies
- Role verification middleware (decorator-based)
- Password reset functionality

**Key Functions**:
```python
async def authenticate_user(email: str, password: str) -> User | None
async def create_session(user: User) -> str  # Returns session token
async def get_current_user(session: str) -> User
def require_role(*roles: str)  # Decorator for route protection
```

#### Component: Travel Request Service
**Purpose**: Core business logic for travel request lifecycle
**Location**: `app/services/travel_request_service.py`
**Responsibilities**:
- Create travel requests with automatic routing
- Validate request data and relationships
- Determine approver based on request type
- Handle status transitions (pending → approved/rejected)
- Enforce business rules

**Key Functions**:
```python
async def create_request(request_data: TravelRequestCreate, user: User) -> TravelRequest
async def get_pending_requests_for_approver(user: User) -> list[TravelRequest]
async def approve_request(request_id: int, approver: User, comments: str | None) -> TravelRequest
async def reject_request(request_id: int, approver: User, reason: str) -> TravelRequest
async def determine_approver(request: TravelRequest) -> User
```

#### Component: Notification Service
**Purpose**: Handle notification delivery to relevant parties
**Location**: `app/services/notification_service.py`
**Responsibilities**:
- Create notifications for status changes
- Queue notifications (in-app initially, email optional)
- Mark notifications as read
- Send to multiple recipients based on event type

**Key Functions**:
```python
async def notify_request_submitted(request: TravelRequest) -> None
async def notify_request_approved(request: TravelRequest) -> None
async def notify_request_rejected(request: TravelRequest) -> None
async def get_unread_notifications(user: User) -> list[Notification]
async def mark_notification_read(notification_id: int) -> None
```

#### Component: Project Management Service
**Purpose**: Admin functionality for project lifecycle management
**Location**: `app/services/project_service.py`
**Responsibilities**:
- CRUD operations for projects
- Team lead assignment
- Project activation/deactivation
- Validate project availability for new requests

**Key Functions**:
```python
async def create_project(project_data: ProjectCreate) -> Project
async def update_project(project_id: int, project_data: ProjectUpdate) -> Project
async def assign_team_lead(project_id: int, user_id: int) -> Project
async def deactivate_project(project_id: int) -> Project
async def get_active_projects() -> list[Project]
```

#### Component: Reporting Service
**Purpose**: Generate reports and filtered views for accounting
**Location**: `app/services/reporting_service.py`
**Responsibilities**:
- Filter approved travel requests by multiple criteria
- Generate CSV exports
- Aggregate by T-account, project, date range
- Calculate totals and summaries

**Key Functions**:
```python
async def get_approved_requests(filters: ReportFilters) -> list[TravelRequest]
async def export_to_csv(requests: list[TravelRequest]) -> str  # Returns CSV content
async def get_summary_by_taccount(date_from: date, date_to: date) -> dict
```

## Data Model

### Entity: User
```python
class User(Base):
    __tablename__ = "users"

    id: int  # Primary key
    email: str  # Unique, indexed
    password_hash: str
    full_name: str
    role: str  # Enum: employee, manager, team_lead, admin, accounting
    manager_id: int | None  # Foreign key to User (self-referential)
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

**Purpose**: Represents all system users with role-based permissions
**Relationships**:
- Self-referential manager (one manager, many employees)
- Many travel requests (as requester or approver)
- Many projects (as team lead)

### Entity: TravelRequest
```python
class TravelRequest(Base):
    __tablename__ = "travel_requests"

    id: int  # Primary key
    requester_id: int  # Foreign key to User
    request_type: str  # Enum: operations, project
    project_id: int | None  # Foreign key to Project (nullable)

    # Travel details
    destination: str
    start_date: date
    end_date: date
    purpose: str  # Text description
    estimated_cost: Decimal

    # Budget tracking
    taccount_id: int  # Foreign key to TAccount

    # Approval workflow
    status: str  # Enum: pending, approved, rejected
    approver_id: int | None  # Foreign key to User
    approval_date: datetime | None
    approval_comments: str | None
    rejection_reason: str | None

    # Metadata
    created_at: datetime
    updated_at: datetime
```

**Purpose**: Core entity representing a travel approval request
**Relationships**:
- Belongs to User (requester)
- Belongs to User (approver)
- Optionally belongs to Project
- Belongs to TAccount
- Has many Notifications

**Indexes**:
- requester_id, status (for employee dashboard)
- approver_id, status (for approver dashboard)
- taccount_id, status (for accounting reports)

### Entity: Project
```python
class Project(Base):
    __tablename__ = "projects"

    id: int  # Primary key
    name: str
    description: str
    team_lead_id: int  # Foreign key to User
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

**Purpose**: Represents projects that can have travel requests
**Relationships**:
- Belongs to User (team_lead)
- Has many TravelRequests

### Entity: TAccount
```python
class TAccount(Base):
    __tablename__ = "t_accounts"

    id: int  # Primary key
    account_code: str  # Unique, e.g., "T-1234"
    account_name: str
    description: str
    is_active: bool
    created_at: datetime
```

**Purpose**: Budget accounts for tracking travel expenses
**Relationships**:
- Has many TravelRequests

### Entity: Notification
```python
class Notification(Base):
    __tablename__ = "notifications"

    id: int  # Primary key
    user_id: int  # Foreign key to User (recipient)
    travel_request_id: int  # Foreign key to TravelRequest
    notification_type: str  # Enum: request_submitted, request_approved, request_rejected
    message: str
    is_read: bool
    created_at: datetime
```

**Purpose**: In-app notifications for workflow events
**Relationships**:
- Belongs to User
- Belongs to TravelRequest

## User Interface Design

### Screen: Login Page
**Route**: `/login`
**Purpose**: User authentication
**Layout**:
```
┌─────────────────────────┐
│  Company Logo           │
│  Travel Approval System │
├─────────────────────────┤
│  Email: [________]      │
│  Password: [________]   │
│  [Login Button]         │
└─────────────────────────┘
```

**Key Elements**:
- Email input (validated)
- Password input (masked)
- Login button (POST form submission)
- Error message display area

**User Interactions**:
- Submit form → Authenticate → Redirect to dashboard based on role

### Screen: Employee Dashboard
**Route**: `/dashboard`
**Purpose**: View and manage own travel requests
**Layout**:
```
┌─────────────────────────────────────┐
│  Header [Notifications] [Profile ▼] │
├─────────────────────────────────────┤
│  Welcome, [Name]                    │
│  [+ New Travel Request]             │
├─────────────────────────────────────┤
│  My Travel Requests                 │
│  ┌─────────────────────────────┐   │
│  │ Pending (3)                 │   │
│  │ - Request #123 (Berlin)     │   │
│  │ - Request #122 (London)     │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Approved (5)                │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Rejected (1)                │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Key Elements**:
- Notification bell with unread count
- New request button (prominent)
- Grouped lists by status with visual indicators
- Each request shows: ID, destination, dates, status

**User Interactions**:
- Click request → View detail page
- Click "New Travel Request" → Create request form

### Screen: Create Travel Request
**Route**: `/requests/new`
**Purpose**: Submit new travel request
**Layout**:
```
┌─────────────────────────────────────┐
│  New Travel Request                 │
├─────────────────────────────────────┤
│  Request Type:                      │
│  ( ) Operations  ( ) Project        │
│                                     │
│  [Project dropdown - if selected]   │
│                                     │
│  Destination: [________]            │
│  Start Date: [📅]                  │
│  End Date: [📅]                    │
│  Purpose: [________________]        │
│           [________________]        │
│  Estimated Cost: [________] DKK     │
│  T-Account: [Dropdown ▼]           │
│                                     │
│  [Cancel] [Submit Request]          │
└─────────────────────────────────────┘
```

**Key Elements**:
- Radio buttons for request type
- Conditional project dropdown (only for project type)
- Date pickers with validation (end >= start)
- Textarea for purpose
- T-account dropdown (required)
- Validation feedback inline

**User Interactions**:
- Select "Project" → Project dropdown appears
- Submit → Validate → Create request → Route to approver → Redirect to dashboard

### Screen: Approver Dashboard
**Route**: `/approvals`
**Purpose**: Review and approve/reject pending requests
**Layout**:
```
┌─────────────────────────────────────┐
│  Pending Approvals (7)              │
├─────────────────────────────────────┤
│  ┌─────────────────────────────┐   │
│  │ Request #124 - Sarah Jensen │   │
│  │ Berlin, Jun 15-17, 2025     │   │
│  │ Operations • T-4567          │   │
│  │ Est. Cost: 12,500 DKK       │   │
│  │ [View Details]              │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Request #123 - Mark Nielsen │   │
│  │ ...                         │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Key Elements**:
- Request count badge
- Compact request cards with key info
- Visual distinction for request type
- View details button

**User Interactions**:
- Click request → Request detail modal/page

### Screen: Request Detail & Approval
**Route**: `/requests/{id}`
**Purpose**: View full request details and approve/reject
**Layout**:
```
┌─────────────────────────────────────┐
│  Travel Request #124                │
│  Status: Pending                    │
├─────────────────────────────────────┤
│  Requester: Sarah Jensen            │
│  Type: Operations                   │
│  Destination: Berlin, Germany       │
│  Dates: Jun 15-17, 2025 (3 days)   │
│  Purpose: Client meeting with...    │
│  Estimated Cost: 12,500 DKK         │
│  T-Account: T-4567 (Sales Travel)   │
│  Submitted: Jun 1, 2025             │
├─────────────────────────────────────┤
│  [For Approvers]                    │
│  Comments (optional):               │
│  [________________________]         │
│  [________________________]         │
│                                     │
│  [Reject] [Approve]                 │
└─────────────────────────────────────┘
```

**Key Elements**:
- Full request details (read-only for employees)
- Status badge with color coding
- Approval actions (only visible to approver)
- Comments textarea
- Action buttons with confirmation

**User Interactions**:
- Approve → Confirm → Update status → Notify employee & accounting
- Reject → Require reason → Update status → Notify employee

### Screen: Accounting Reports
**Route**: `/reports`
**Purpose**: View and export approved travel data
**Layout**:
```
┌─────────────────────────────────────┐
│  Travel Reports                     │
├─────────────────────────────────────┤
│  Filters:                           │
│  Date Range: [📅] to [📅]        │
│  T-Account: [All ▼]                │
│  Project: [All ▼]                  │
│  Status: [Approved ▼]              │
│  [Apply Filters] [Export CSV]       │
├─────────────────────────────────────┤
│  Results (23 requests)              │
│  Total: 456,789 DKK                 │
│                                     │
│  [Table with pagination]            │
│  ID | Employee | Destination | ... │
└─────────────────────────────────────┘
```

**Key Elements**:
- Filter controls (date range, T-account, project)
- Export CSV button
- Summary statistics (count, total cost)
- Sortable, paginated table

**User Interactions**:
- Apply filters → Reload table with filtered data
- Export CSV → Download file with filtered data

### Screen: Admin - Project Management
**Route**: `/admin/projects`
**Purpose**: Manage projects and team leads
**Layout**:
```
┌─────────────────────────────────────┐
│  Project Management                 │
│  [+ New Project]                    │
├─────────────────────────────────────┤
│  Active Projects (8)                │
│  ┌─────────────────────────────┐   │
│  │ Project Alpha               │   │
│  │ Team Lead: John Doe         │   │
│  │ [Edit] [Deactivate]         │   │
│  └─────────────────────────────┘   │
│                                     │
│  Inactive Projects (2)              │
│  ...                                │
└─────────────────────────────────────┘
```

**Key Elements**:
- Create new project button
- Grouped lists (active/inactive)
- Edit and deactivate actions per project
- Team lead assignment visible

**User Interactions**:
- Create → Modal/form for new project
- Edit → Update project details and team lead
- Deactivate → Confirm → Prevent new requests

## Key Interactions & Flows

### Flow: Submit and Approve Operations Travel Request
**Scenario**: Employee submits operational travel, manager approves

1. Employee logs in → Redirected to `/dashboard`
2. Employee clicks "New Travel Request" → Navigate to `/requests/new`
3. Employee selects "Operations" radio button
4. System hides project dropdown
5. Employee fills form (destination, dates, purpose, cost, T-account)
6. Employee clicks "Submit Request"
7. System validates form data
8. System creates TravelRequest with status="pending"
9. System determines approver (employee's manager via manager_id)
10. System creates notification for manager
11. System redirects employee to dashboard with success message
12. Manager logs in → Badge shows "1 pending approval"
13. Manager navigates to `/approvals`
14. Manager clicks request card → Navigate to `/requests/{id}`
15. Manager reviews details, adds optional comments
16. Manager clicks "Approve"
17. System updates request status="approved", records approval_date
18. System creates notifications for employee and accounting staff
19. System redirects manager to approvals page
20. Employee receives notification "Request #124 approved"
21. Accounting sees request in `/reports` filtered view

**Error Handling**:
- If form validation fails → Show inline errors, prevent submission
- If manager_id is null → Show error "No manager assigned, contact admin"
- If T-account not selected → Show error "T-account is required"
- If database error → Show user-friendly message, log error

### Flow: Submit and Reject Project Travel Request
**Scenario**: Employee submits project travel, team lead rejects with reason

1. Employee navigates to `/requests/new`
2. Employee selects "Project" radio button
3. System shows project dropdown with active projects
4. Employee selects project (e.g., "Project Alpha")
5. Employee fills remaining form fields
6. Employee submits request
7. System creates TravelRequest with project_id set
8. System determines approver (project.team_lead_id)
9. System creates notification for team lead
10. Team lead logs in → Sees pending approval
11. Team lead views request details
12. Team lead clicks "Reject"
13. System prompts for rejection reason (required)
14. Team lead enters reason: "Project budget exhausted for Q2"
15. Team lead confirms rejection
16. System updates request status="rejected", stores reason
17. System creates notification for employee
18. Employee receives notification with rejection reason
19. Employee can view rejection reason in request detail

**Error Handling**:
- If project is inactive → Show error "Project unavailable for new requests"
- If project has no team_lead_id → Show error "Project has no team lead assigned"
- If rejection reason is empty → Show error "Rejection reason is required"

### Flow: Admin Creates Project and Assigns Team Lead
**Scenario**: Admin creates new project for travel requests

1. Admin logs in → Navigates to `/admin/projects`
2. Admin clicks "New Project" button
3. System shows modal/form with fields: name, description, team lead
4. Admin enters project name: "Project Beta"
5. Admin enters description: "New client engagement in Sweden"
6. Admin selects team lead from user dropdown (role=team_lead or manager)
7. Admin submits form
8. System validates inputs
9. System creates Project with is_active=true
10. System redirects to projects list with success message
11. Employees can now see "Project Beta" in project dropdown when creating requests

**Error Handling**:
- If project name already exists → Show error "Project name must be unique"
- If selected team lead is not active → Show error "Cannot assign inactive user"

## File Structure
```
travel-approval/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app initialization
│   ├── config.py                    # Settings using pydantic-settings
│   ├── database.py                  # SQLAlchemy setup and session management
│   │
│   ├── models/                      # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── travel_request.py
│   │   ├── project.py
│   │   ├── taccount.py
│   │   └── notification.py
│   │
│   ├── schemas/                     # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── travel_request.py
│   │   ├── project.py
│   │   └── notification.py
│   │
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── travel_request_service.py
│   │   ├── notification_service.py
│   │   ├── project_service.py
│   │   └── reporting_service.py
│   │
│   ├── routers/                     # Route handlers (controllers)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── travel_requests.py
│   │   ├── approvals.py
│   │   ├── reports.py
│   │   └── admin.py
│   │
│   ├── auth/                        # Authentication & authorization
│   │   ├── __init__.py
│   │   ├── dependencies.py          # get_current_user, require_role
│   │   ├── password.py              # Password hashing utilities
│   │   └── session.py               # Session management
│   │
│   ├── templates/                   # Jinja2 templates
│   │   ├── base.html                # Base template with header/footer
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── requests/
│   │   │   ├── new.html
│   │   │   ├── detail.html
│   │   │   └── list.html
│   │   ├── approvals/
│   │   │   └── list.html
│   │   ├── reports/
│   │   │   └── index.html
│   │   └── admin/
│   │       └── projects.html
│   │
│   └── static/                      # Static files
│       ├── css/
│       │   └── custom.css           # Custom styles (Tailwind via CDN)
│       └── js/
│           └── main.js              # Minimal JavaScript for interactions
│
├── alembic/                         # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── test_auth.py
│   ├── test_travel_requests.py
│   ├── test_approvals.py
│   ├── test_projects.py
│   └── test_notifications.py
│
├── spec/                            # Documentation
│   ├── requirements.md
│   ├── design.md
│   └── plan.md                      # To be created
│
├── .env.example                     # Example environment variables
├── .gitignore
├── alembic.ini                      # Alembic configuration
├── pyproject.toml                   # Poetry/pip dependencies
├── README.md
└── travel_approval.db               # SQLite database (gitignored)
```

## Design Decisions & Tradeoffs

### Decision: SQLite for Database
**Choice**: SQLite with SQLAlchemy ORM
**Alternatives Considered**: PostgreSQL, MySQL
**Rationale**: Requirements specify 500 concurrent users and read-heavy workloads (approvals dashboard, accounting reports). SQLite with WAL mode handles this well for internal tools. Simplifies deployment (no separate DB server). Easy to backup (single file).
**Tradeoffs**:
- Gain: Zero database server management, simple backups, faster development
- Lose: Cannot scale beyond ~1000 concurrent writes/sec (not a concern here)

### Decision: Server-Side Rendering with Jinja2
**Choice**: Jinja2 templates rendered server-side
**Alternatives Considered**: React/Vue SPA with API
**Rationale**: Requirements don't need real-time updates or complex client-side interactions. SSR provides faster initial page loads, better SEO (if needed), simpler security model, and matches team's tech stack preference.
**Tradeoffs**:
- Gain: Simpler architecture, no build tooling, better accessibility by default
- Lose: Less interactive UI (full page reloads), harder to add real-time features later

### Decision: Session-Based Authentication
**Choice**: Signed session cookies with user_id
**Alternatives Considered**: JWT tokens, OAuth
**Rationale**: Internal tool with controlled user base. Session cookies provide automatic CSRF protection, easy revocation, and simpler implementation. No need for OAuth (no external identity providers mentioned).
**Tradeoffs**:
- Gain: Automatic cookie handling, server-side session control, simpler logout
- Lose: Server memory for session storage (negligible for 500 users)

### Decision: In-App Notifications First, Email Optional
**Choice**: Database-backed notifications shown in UI, email as future enhancement
**Alternatives Considered**: Email-only notifications
**Rationale**: Requirements mention "notifications for relevant changes" but don't specify email. In-app provides immediate feedback, easier to implement, and avoids email infrastructure complexity. Can add email later without architectural changes.
**Tradeoffs**:
- Gain: Faster MVP, no email server dependency, instant notification delivery
- Lose: Users must be logged in to see notifications (acceptable for internal tool)

### Decision: Role as String Enum vs. Separate Roles Table
**Choice**: Role stored as string enum in users table
**Alternatives Considered**: Separate roles table with many-to-many
**Rationale**: Requirements define 5 fixed roles (employee, manager, team_lead, admin, accounting) with no indication of complex permissions or role hierarchies. Simple enum is sufficient and avoids unnecessary joins.
**Tradeoffs**:
- Gain: Simpler queries, faster role checks, easier to understand
- Lose: Harder to add granular permissions later (can refactor if needed)

### Decision: Single Approver per Request
**Choice**: One approver_id field, routing logic determines who
**Alternatives Considered**: Multi-level approval chains
**Rationale**: Requirements explicitly state "single approver per request type" and list multi-level chains as out of scope. YAGNI principle applies.
**Tradeoffs**:
- Gain: Simple data model, clear approval state, faster approvals
- Lose: Cannot add approval chains without schema changes (acceptable per requirements)

## Non-Functional Considerations

### Performance
- **Database Indexing**: Add indexes on frequently queried columns (requester_id, approver_id, status, taccount_id)
- **Connection Pooling**: SQLAlchemy pool size configured for 500 concurrent users
- **Template Caching**: Jinja2 template caching enabled in production
- **Query Optimization**: Use eager loading (joinedload) to avoid N+1 queries on list views
- **Pagination**: Limit result sets to 50 items per page for dashboard and reports

### Scalability
- **Current Design**: Handles 500 concurrent users comfortably
- **Scaling Path**: If users exceed 1000+, migrate to PostgreSQL with minimal code changes (SQLAlchemy abstracts database)
- **Caching**: Can add Redis for session storage if needed
- **Async Support**: FastAPI's async handlers allow efficient I/O-bound operations

### Accessibility
- **Semantic HTML**: Use proper heading hierarchy, form labels, ARIA labels where needed
- **Keyboard Navigation**: All actions accessible via keyboard (tab, enter, escape)
- **Focus Management**: Visible focus indicators on interactive elements
- **Color Contrast**: Tailwind CSS utilities ensure WCAG AA compliance for text
- **Screen Reader Support**: Form errors announced, status changes communicated

### Error Handling
- **Validation Errors**: Pydantic schemas validate all inputs, return 422 with detailed messages
- **Business Logic Errors**: Custom exceptions (e.g., `UnauthorizedApproval`) return user-friendly messages
- **Database Errors**: Catch SQLAlchemy exceptions, log details, show generic error to user
- **404 Handling**: Custom 404 template for missing resources
- **500 Handling**: Custom 500 template, errors logged to file/stdout

### Security
- **Authentication**: All routes except `/login` require valid session
- **Authorization**: Decorator-based role checks on sensitive routes (@require_role("manager"))
- **Password Security**: Bcrypt hashing with salt, minimum password length enforced
- **SQL Injection**: SQLAlchemy ORM prevents injection attacks
- **XSS Protection**: Jinja2 auto-escapes template variables
- **CSRF Protection**: Session cookies with SameSite=Lax, form tokens for state-changing operations
- **Audit Logging**: All approval/rejection actions logged with timestamp, user, and request ID

## Testing Strategy

**Philosophy**: Every feature must be verified before moving to the next. Testing is incremental with focus on business logic and integration tests for workflows.

### Testing Tools & Framework
- **Testing Framework**: pytest 7.0+
- **Test Database**: In-memory SQLite for fast test execution
- **HTTP Client**: TestClient from FastAPI (built on Starlette)
- **Fixtures**: pytest fixtures for database setup, user creation, authentication
- **Test Runner Command**: `pytest` (runs all tests) or `pytest -v` (verbose)
- **Coverage Tool**: pytest-cov (`pytest --cov=app --cov-report=html`)

### Verification Approach for Each Task Type

#### Code/Logic Tasks (Services, Business Logic)
- **Verification Method**: Automated unit tests with pytest
- **When to Test**: After implementing each service function
- **What to Test**:
  - Happy path: Function returns expected results with valid inputs
  - Edge cases: Empty lists, null values, boundary conditions
  - Error handling: Invalid inputs raise appropriate exceptions
  - Business rules: Approval routing, status transitions, role checks

**Example Test Structure**:
```python
# tests/test_travel_requests.py
async def test_create_operations_request_routes_to_manager(db_session):
    # Given: Employee with assigned manager
    employee = create_user(role="employee", manager_id=manager.id)
    # When: Create operations request
    request = await travel_request_service.create_request(request_data, employee)
    # Then: Approver is employee's manager
    assert request.approver_id == employee.manager_id
```

#### API Route Tasks
- **Verification Method**: Integration tests using FastAPI TestClient
- **When to Test**: After implementing each route handler
- **What to Test**:
  - Authentication: Unauthenticated requests return 401
  - Authorization: Users can only access permitted resources
  - Request/Response: Correct status codes, response structure
  - Form submissions: POST requests create/update records correctly
  - Redirects: Successful actions redirect to appropriate pages

**Example Test Structure**:
```python
# tests/test_approvals.py
def test_approve_request_as_manager(client, authenticated_manager):
    # Given: Pending request for manager's employee
    request = create_pending_request(requester=employee, approver=authenticated_manager)
    # When: Manager approves request
    response = client.post(f"/requests/{request.id}/approve", data={"comments": "Approved"})
    # Then: Request status updated, redirect to approvals page
    assert response.status_code == 302
    assert response.headers["location"] == "/approvals"
    assert db.query(TravelRequest).get(request.id).status == "approved"
```

#### Template/UI Tasks
- **Verification Method**: Automated tests for rendering + manual verification
- **Automated Tests**: Check correct template used, context variables passed
- **Manual Verification**: Visual appearance, responsive design, form usability
- **When to Test**: After implementing each template

**Example Test Structure**:
```python
# tests/test_dashboard.py
def test_dashboard_shows_user_requests(client, authenticated_employee):
    # Given: Employee has 2 pending requests
    create_travel_request(requester=authenticated_employee, status="pending")
    create_travel_request(requester=authenticated_employee, status="pending")
    # When: Access dashboard
    response = client.get("/dashboard")
    # Then: Response contains both requests
    assert response.status_code == 200
    assert b"Pending (2)" in response.content
```

#### Database Migration Tasks
- **Verification Method**: Run migration, check schema
- **Success Criteria**: `alembic upgrade head` completes without errors, tables created correctly
- **When to Test**: Immediately after creating migration

### Test Writing Approach
**Test-After with Immediate Verification**: Implement feature, write tests immediately, verify before moving on. This ensures each component works before building dependent features.

### Critical Testing Rules
1. Every service function must have at least one test covering the happy path
2. All authentication/authorization logic must be tested
3. Tests must pass before committing code
4. If tests fail repeatedly (3+ times), reassess implementation approach
5. Integration tests are higher priority than 100% unit test coverage

### Unit Tests
- **What**: Test individual service functions and utilities in isolation
- **Where**: `tests/test_*_service.py` (mirrors `app/services/`)
- **Key areas**:
  - Travel request creation and routing logic
  - Approval/rejection workflows
  - Notification creation
  - Project management (CRUD operations)
  - Reporting filters and aggregations
- **Run Command**: `pytest tests/test_*_service.py`

### Integration Tests
- **What**: Test complete user flows through API routes
- **Key flows**:
  - Employee submits request → Manager approves → Notifications sent
  - Employee submits project request → Team lead rejects
  - Admin creates project → Employee selects project in request form
  - Accounting filters reports by T-account and exports CSV
- **Run Command**: `pytest tests/test_*.py` (runs all integration tests)

### Manual Testing Scenarios
- **What**: UI/UX verification requiring human judgment
- **Key scenarios**:
  - Visual design matches Tailwind styles across browsers
  - Form validation displays helpful error messages inline
  - Notification badge updates correctly after status changes
  - Responsive design works on tablet/mobile screen sizes
  - Keyboard navigation flows logically through forms
  - Date pickers work correctly
  - CSV export downloads with correct formatting
- **When**: After completing each UI-related phase

## Development Approach

### Phase Breakdown
1. **Phase 1: Project Setup & Core Structure**
   - Initialize FastAPI project with proper structure
   - Configure SQLAlchemy, Alembic, and database models
   - Set up authentication (login, session management)
   - Create base template with navigation

2. **Phase 2: Core Travel Request Workflow**
   - Implement travel request creation (operations & project)
   - Build approval routing logic
   - Create employee and approver dashboards
   - Add request detail view with approve/reject actions

3. **Phase 3: Notifications & Admin Features**
   - Build notification service and display
   - Implement project management (admin panel)
   - Add T-account management
   - Create user management interface

4. **Phase 4: Reporting & Polish**
   - Build accounting reports with filters
   - Add CSV export functionality
   - Implement audit logging
   - Add comprehensive error handling and validation
   - Performance optimization and testing

5. **Phase 5: Optional LLM Email Integration**
   - Set up email receiving (if infrastructure available)
   - Integrate with LLM API (e.g., OpenAI, Anthropic)
   - Build confirmation workflow for extracted data
   - Add to existing request creation flow

### Development Standards
- **Code Style**: Follow PEP 8, use Black for formatting, Ruff for linting
- **Type Hints**: Use Python type hints for all function signatures
- **Docstrings**: Add docstrings to all service functions (Google style)
- **Naming Conventions**:
  - Models: Singular, PascalCase (e.g., `TravelRequest`)
  - Tables: Plural, snake_case (e.g., `travel_requests`)
  - Functions: snake_case, verb-prefixed (e.g., `create_request`, `get_pending_requests`)
  - Routes: kebab-case (e.g., `/travel-requests/new`)
- **Error Handling**: Use custom exception classes, catch and log appropriately
- **Git Commits**: Conventional commits format (feat:, fix:, docs:, refactor:)
- **Documentation**: Update README with setup instructions, API documentation generated by FastAPI

## Open Questions
- **Notification Channel**: Confirm preference for in-app notifications vs. email (or both). Affects Phase 3 implementation.
- **User Provisioning**: How are users created? Manual admin interface, CSV import, or SSO integration?
- **Manager Assignment**: How is manager_id determined when creating users? Manual assignment or HR system integration?
- **T-Account Management**: Should admins manage T-accounts in the system, or are they imported from accounting system?
- **Request Cancellation**: Should approved requests have a cancellation workflow? (Currently out of scope but common need)
- **Historical Data**: Is there existing travel data to migrate? Affects database schema design (e.g., need for legacy IDs)
- **Deployment Environment**: On-premise server, cloud VM, or container platform? Affects setup instructions and configuration.

## References
- Requirements: `spec/requirements.md`
- FastAPI Documentation: https://fastapi.tiangolo.com
- SQLAlchemy 2.0 Documentation: https://docs.sqlalchemy.org
- Tailwind CSS Documentation: https://tailwindcss.com/docs
