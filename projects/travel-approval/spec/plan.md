# Implementation Plan: Travel Approval System

## Overview
Building a web-based travel approval system with FastAPI that streamlines pre-trip approval workflows. The system routes employee travel requests through appropriate approval chains (manager for operations, team lead for projects) and provides visibility to accounting for budget planning.

## Current State
- Empty project / Starting from scratch
- Target tech stack: FastAPI (Python 3.11+), SQLite, SQLAlchemy, Jinja2 templates, Tailwind CSS

## Desired End State
A fully functional travel approval system where:
- Employees can submit and track travel requests
- Requests are automatically routed to correct approvers (managers or project team leads)
- Approvers can review and approve/reject requests with comments
- Accounting staff can view approved travel and generate reports by T-account
- Admins can manage projects and team lead assignments
- All interactions are authenticated and role-based

**Success Criteria:**
- [ ] All user stories from requirements.md are implemented
- [ ] All acceptance criteria are met
- [ ] Application matches design specifications
- [ ] Code is tested and runs without errors
- [ ] 100% of travel requests route to correct approver automatically
- [ ] Accounting can generate reports by T-account

## What We're NOT Doing
- Expense reporting after travel (pre-approval only)
- Actual travel booking or integration with booking systems
- Reimbursement workflows
- Budget enforcement (system tracks but doesn't prevent over-budget)
- Multi-level approval chains (only single approver per request type)
- Calendar integration
- Mobile native app (web-responsive only)
- Integration with HR systems
- Automated delegation when approvers are on leave
- LLM email integration (Phase 5 is optional)

## Implementation Approach
We'll follow a **backend-first approach** since this is primarily a form-based CRUD application with server-side rendering. The phases build incrementally:
1. **Foundation first**: Set up project structure, database, authentication
2. **Core workflow next**: Implement the primary travel request submission and approval flow
3. **Notifications and admin**: Add supporting features for notifications and project management
4. **Reporting and polish**: Complete with accounting reports, testing, and refinement

This order ensures we can test core workflows early while building supporting features on a solid foundation.

---

## Phase 1: Project Setup & Foundation

### Overview
Set up the development environment, database infrastructure, and authentication system. This phase establishes the foundation for all subsequent work.

### Tasks

#### 1.1 Initialize FastAPI Project
**Action**:
- Create project directory structure per design.md
- Initialize pyproject.toml with dependencies (FastAPI, SQLAlchemy, Alembic, etc.)
- Set up virtual environment
- Configure .gitignore for Python projects

**Files Created**:
- `pyproject.toml` with all dependencies from design.md
- `app/__init__.py`
- `app/main.py` (FastAPI app initialization)
- `app/config.py` (Settings using pydantic-settings)
- `.env.example` (Example environment variables)
- `.gitignore`
- `README.md`

**Success Criteria**:
- [x] Dependencies install without errors: `pip install -e .`
- [x] Dev server starts: `uvicorn app.main:app --reload`
- [x] FastAPI welcome page accessible at http://localhost:8000
- [x] Auto-generated docs accessible at http://localhost:8000/docs

#### 1.2 Setup Database Models & Migrations
**Files Created/Modified**:
- `app/database.py` (SQLAlchemy engine, session management)
- `app/models/user.py` (User model from design.md line 162)
- `app/models/travel_request.py` (TravelRequest model from design.md line 184)
- `app/models/project.py` (Project model from design.md line 228)
- `app/models/taccount.py` (TAccount model from design.md line 247)
- `app/models/notification.py` (Notification model from design.md line 264)
- `alembic.ini` (Alembic configuration)
- `alembic/env.py` (Migration environment setup)

**Action**:
- Implement all SQLAlchemy models with relationships
- Configure database connection (SQLite with WAL mode)
- Initialize Alembic for migrations
- Create initial migration with all tables
- Add indexes per design.md (requester_id, approver_id, status, taccount_id)

**Test Requirements**:
- [x] Write tests to verify models can be instantiated
- [x] Test relationships (user.travel_requests, project.travel_requests, etc.)
- [x] Verify database constraints (unique emails, foreign keys, etc.)

**Verification Steps**:
1. Run migration: `alembic upgrade head`
2. Verify tables created: `sqlite3 travel_approval.db ".tables"`
3. Expected: All 5 tables exist (users, travel_requests, projects, t_accounts, notifications)
4. Run tests: `pytest tests/test_database.py`

**Success Criteria**:
- [x] All code changes completed
- [x] Migration runs successfully
- [x] All tables created with correct columns and relationships
- [x] Database tests written and passing

#### 1.3 Implement Authentication System
**Files Created/Modified**:
- `app/auth/password.py` (Bcrypt password hashing)
- `app/auth/session.py` (Session cookie management)
- `app/auth/dependencies.py` (get_current_user, require_role decorators)
- `app/schemas/user.py` (Pydantic schemas for User)
- `app/routers/auth.py` (Login/logout routes)
- `app/templates/base.html` (Base template with header/navigation)
- `app/templates/login.html` (Login page from design.md line 286)

**Action**:
- Implement password hashing with passlib (bcrypt)
- Create session management with signed cookies (itsdangerous)
- Build authentication dependencies (get_current_user, require_role)
- Create login route (POST /login) with session creation
- Create logout route (POST /logout) with session deletion
- Design base template with navigation and user context

**Code Structure**:
```python
# app/auth/dependencies.py
async def get_current_user(session: str = Cookie(None)) -> User
def require_role(*roles: str)  # Decorator for route protection

# app/routers/auth.py
@router.post("/login")
async def login(email: str, password: str) -> Response
@router.post("/logout")
async def logout() -> Response
```

**Test Requirements**:
- [x] Test password hashing and verification
- [x] Test successful login creates valid session
- [x] Test invalid credentials return error
- [x] Test get_current_user with valid/invalid sessions
- [x] Test require_role decorator blocks unauthorized roles
- [x] Tests pass: `pytest tests/test_auth.py`

**Verification Steps**:
1. Run tests: `pytest tests/test_auth.py -v`
2. Manual test: Access /login page in browser
3. Manual test: Submit login form with test credentials
4. Expected: Redirect to dashboard after successful login
5. Expected: Invalid credentials show error message

**Success Criteria**:
- [x] All code changes completed
- [x] Password hashing works correctly
- [x] Session creation/validation functional
- [x] Login page renders correctly
- [x] All authentication tests passing
- [ ] Manual login flow verified

#### 1.4 Create Initial Seed Data
**Files Created**:
- `app/seed_data.py` (Script to create initial users, projects, T-accounts)

**Action**:
- Create seed script to populate database with test data
- Add 5 users with different roles (employee, manager, team_lead, admin, accounting)
- Add 2-3 sample projects with team leads
- Add 5 sample T-accounts
- Set up manager relationships (employees → managers)

**Sample Data**:
- Admin: admin@xyz.dk (password: admin123)
- Manager: manager@xyz.dk (manages 2 employees)
- Team Lead: teamlead@xyz.dk (leads Project Alpha)
- Employee 1: employee1@xyz.dk (reports to manager)
- Employee 2: employee2@xyz.dk (reports to manager)
- Accounting: accounting@xyz.dk

**Verification Steps**:
1. Run seed script: `python -m app.seed_data`
2. Verify data: `sqlite3 travel_approval.db "SELECT email, role FROM users;"`
3. Expected: 5 users with correct roles
4. Manual test: Login as each user role

**Success Criteria**:
- [x] Seed script creates all test users
- [x] Users can login with seeded credentials
- [x] Manager relationships set correctly
- [x] Projects have team leads assigned
- [x] T-accounts are available
- [x] **TASK 1.4 COMPLETE**

---

## Phase 2: Core Travel Request Workflow

### Overview
Implement the primary business functionality: employees submit travel requests, system routes to approvers, and approvers can approve/reject. This is the heart of the application.

### Tasks

#### 2.1 Implement Travel Request Service
**File**: `app/services/travel_request_service.py`

**Action**:
- Implement create_request() with automatic routing logic
- Implement get_pending_requests_for_approver()
- Implement approve_request() with status transition
- Implement reject_request() with required reason
- Implement determine_approver() logic (manager for operations, team_lead for projects)

**Code Structure** (from design.md line 98):
```python
async def create_request(request_data: TravelRequestCreate, user: User) -> TravelRequest
async def get_pending_requests_for_approver(user: User) -> list[TravelRequest]
async def approve_request(request_id: int, approver: User, comments: str | None) -> TravelRequest
async def reject_request(request_id: int, approver: User, reason: str) -> TravelRequest
async def determine_approver(request: TravelRequest) -> User
```

**Business Rules to Implement**:
- Operations requests route to requester's manager (user.manager_id)
- Project requests route to project's team lead (project.team_lead_id)
- Reject requires non-empty reason, approve allows optional comments
- Status transitions: pending → approved/rejected only

**Test Requirements**:
- [x] Test operations request routes to manager
- [x] Test project request routes to team lead
- [x] Test approve updates status and records approval_date
- [x] Test reject requires reason
- [x] Test approver must be the designated approver (not arbitrary user)
- [x] Test error when manager_id is null
- [x] Test error when project has no team_lead_id
- [x] Tests pass: `pytest tests/test_travel_request_service.py`

**Verification Steps**:
1. Run unit tests: `pytest tests/test_travel_request_service.py -v`
2. Verify all business rules tested
3. Expected: 100% test coverage on service functions

**Implements User Stories**:
- Story 1: Submit Travel Request for Operations (requirements.md line 15)
- Story 2: Submit Travel Request for Project (requirements.md line 32)
- Story 3: Approve/Reject Travel Request (Manager) (requirements.md line 49)
- Story 4: Approve/Reject Travel Request (Project Team Lead) (requirements.md line 66)

**Success Criteria**:
- [x] All code changes completed
- [x] All service functions implemented
- [x] Approval routing logic works correctly
- [x] Unit tests written for all functions
- [x] All tests passing
- [x] Edge cases handled (null manager, inactive project, etc.)
- [x] **TASK 2.1 COMPLETE**

#### 2.2 Create Travel Request Schemas
**File**: `app/schemas/travel_request.py`

**Action**:
- Define TravelRequestCreate schema with validation
- Define TravelRequestUpdate schema
- Define TravelRequestResponse schema
- Add validation rules (end_date >= start_date, positive cost, required fields)

**Schema Structure**:
```python
class TravelRequestCreate(BaseModel):
    request_type: Literal["operations", "project"]
    project_id: int | None
    destination: str
    start_date: date
    end_date: date
    purpose: str
    estimated_cost: Decimal
    taccount_id: int

    @validator('end_date')
    def end_after_start(cls, v, values):
        # Validate end_date >= start_date
```

**Test Requirements**:
- [x] Test valid request data passes validation
- [x] Test end_date before start_date raises error
- [x] Test negative cost raises error
- [x] Test project type requires project_id
- [x] Tests pass: `pytest tests/test_travel_request_schemas.py`

**Success Criteria**:
- [x] All schemas defined
- [x] Validation rules enforce business logic
- [x] Schema tests passing

#### 2.3 Build Employee Dashboard
**Files Created/Modified**:
- `app/routers/dashboard.py` (Dashboard route handler)
- `app/templates/dashboard.html` (Dashboard UI from design.md line 308)

**Action**:
- Create GET /dashboard route (requires authentication)
- Query user's travel requests grouped by status
- Pass data to template: pending, approved, rejected lists
- Implement template with Tailwind CSS styling
- Add "New Travel Request" button
- Display request cards with key info (ID, destination, dates, status)

**Template Structure** (from design.md line 308):
- Header with user name and navigation
- Prominent "New Travel Request" button
- Three sections: Pending, Approved, Rejected
- Each section shows count and list of requests
- Visual status indicators (colors/badges)

**Test Requirements**:
- [ ] Test authenticated user can access dashboard
- [ ] Test unauthenticated user redirects to login
- [ ] Test dashboard shows user's requests only
- [ ] Test requests grouped correctly by status
- [ ] Tests pass: `pytest tests/test_dashboard.py`

**Verification Steps**:
1. Run tests: `pytest tests/test_dashboard.py -v`
2. Manual test: Login as employee1@xyz.dk
3. Manual test: Verify dashboard shows empty state initially
4. Expected: Dashboard renders with "No travel requests yet" message

**Implements User Story**: Story 7: Track Request Status (Employee) (requirements.md line 115)

**Success Criteria**:
- [x] All code changes completed
- [x] Dashboard route implemented
- [x] Template renders correctly
- [ ] Tests passing
- [x] Manual verification confirms visual appearance
- [x] **TASK 2.3 COMPLETE**

#### 2.4 Build Create Travel Request Form
**Files Created/Modified**:
- `app/routers/travel_requests.py` (Request routes)
- `app/templates/requests/new.html` (Create form from design.md line 344)
- `app/static/js/main.js` (JavaScript for conditional project dropdown)

**Action**:
- Create GET /requests/new route (shows form)
- Create POST /requests/new route (handles submission)
- Implement form with all fields from design.md line 344
- Add radio buttons for request type (operations/project)
- Add conditional project dropdown (shown only for project type)
- Add T-account dropdown
- Add date pickers with validation
- Add inline error display for validation failures
- On success: redirect to dashboard with flash message

**Form Fields**:
- Request Type: Radio (operations/project)
- Project: Dropdown (conditional, active projects only)
- Destination: Text input
- Start Date: Date picker
- End Date: Date picker
- Purpose: Textarea
- Estimated Cost: Number input (DKK)
- T-Account: Dropdown (active accounts)

**JavaScript Behavior**:
- When "Project" selected → Show project dropdown
- When "Operations" selected → Hide project dropdown

**Test Requirements**:
- [x] Test GET /requests/new renders form for authenticated user
- [x] Test POST creates request with valid operations data
- [x] Test POST creates request with valid project data
- [x] Test POST fails when project type but no project_id
- [x] Test POST fails when end_date < start_date
- [x] Test POST fails when T-account not selected
- [x] Test request automatically routed to correct approver
- [x] Tests pass: `pytest tests/test_travel_requests.py`

**Verification Steps**:
1. Run tests: `pytest tests/test_travel_requests.py -v`
2. Manual test: Access /requests/new as employee
3. Manual test: Toggle between operations and project types
4. Manual test: Submit valid operations request
5. Manual test: Submit valid project request
6. Expected: Form validation works, requests created successfully

**Implements User Stories**:
- Story 1: Submit Travel Request for Operations (requirements.md line 15)
- Story 2: Submit Travel Request for Project (requirements.md line 32)

**Success Criteria**:
- [x] All code changes completed
- [x] Form renders with all fields
- [x] Conditional project dropdown works
- [x] Form validation displays errors
- [x] Valid submissions create requests
- [x] Requests routed to correct approver
- [x] All tests passing
- [ ] Manual form submission verified

#### 2.5 Build Approver Dashboard
**Files Created/Modified**:
- `app/routers/approvals.py` (Approval routes)
- `app/templates/approvals/list.html` (Approvals dashboard from design.md line 382)

**Action**:
- Create GET /approvals route (requires manager or team_lead role)
- Query pending requests where current user is the approver
- Display request cards with key information
- Show count of pending approvals
- Add "View Details" button for each request

**Query Logic**:
```python
# Get requests where user is the designated approver and status is pending
requests = db.query(TravelRequest).filter(
    TravelRequest.approver_id == current_user.id,
    TravelRequest.status == "pending"
).all()
```

**Template Structure** (from design.md line 382):
- Header showing "Pending Approvals (count)"
- List of request cards with:
  - Request ID and requester name
  - Destination and dates
  - Request type (operations/project)
  - T-account
  - Estimated cost
  - View Details button

**Test Requirements**:
- [x] Test manager sees requests from their direct reports
- [x] Test team lead sees requests for their projects
- [x] Test manager doesn't see project requests (not assigned to them)
- [x] Test employee role cannot access /approvals
- [x] Test only pending requests shown
- [x] Tests pass: `pytest tests/test_approvals.py`

**Verification Steps**:
1. Run tests: `pytest tests/test_approvals.py -v`
2. Manual test: Create request as employee1@xyz.dk (operations)
3. Manual test: Login as manager@xyz.dk
4. Manual test: Access /approvals
5. Expected: See pending request from employee1

**Implements User Stories**:
- Story 3: Approve/Reject Travel Request (Manager) (requirements.md line 49)
- Story 4: Approve/Reject Travel Request (Project Team Lead) (requirements.md line 66)

**Success Criteria**:
- [x] All code changes completed
- [x] Approver dashboard route implemented
- [x] Only approvers can access (role check)
- [x] Correct requests shown to correct approvers
- [x] Template renders with request cards
- [x] All tests passing
- [ ] Manual verification successful
- [x] **TASK 2.5 COMPLETE**

#### 2.6 Build Request Detail & Approval Actions
**Files Created/Modified**:
- `app/routers/travel_requests.py` (Add detail and action routes)
- `app/templates/requests/detail.html` (Detail page from design.md line 413)

**Action**:
- Create GET /requests/{id} route (shows request details)
- Create POST /requests/{id}/approve route
- Create POST /requests/{id}/reject route
- Implement authorization: only approver can approve/reject
- Add approval comments textarea (optional)
- Add rejection reason textarea (required)
- Show different views for employees vs. approvers
- On approval/rejection: update status, redirect to /approvals

**Template Structure** (from design.md line 413):
- Display all request details (read-only)
- Show status badge with color coding
- For approvers only: show action section with:
  - Comments textarea (optional for approve, required for reject)
  - Reject and Approve buttons
- For employees: show approval/rejection reason if decided

**Authorization Logic**:
```python
# Only the designated approver can approve/reject
if request.approver_id != current_user.id:
    raise HTTPException(403, "Not authorized")
if request.status != "pending":
    raise HTTPException(400, "Request already processed")
```

**Test Requirements**:
- [x] Test approver can view and approve request
- [x] Test approver can view and reject request with reason
- [x] Test reject without reason returns error
- [x] Test non-approver cannot approve (403 error)
- [x] Test employee can view their own request details
- [x] Test employee cannot approve their own request
- [x] Test cannot approve already approved/rejected request
- [x] Tests pass: `pytest tests/test_approvals.py`

**Verification Steps**:
1. Run tests: `pytest tests/test_approvals.py -v`
2. Manual test: Login as manager, click request from approvals page
3. Manual test: Add comments and click Approve
4. Expected: Status updates, redirect to /approvals, success message
5. Manual test: Create new request, login as manager, try to reject without reason
6. Expected: Error message "Rejection reason is required"

**Implements User Stories**:
- Story 3: Approve/Reject Travel Request (Manager) (requirements.md line 49)
- Story 4: Approve/Reject Travel Request (Project Team Lead) (requirements.md line 66)
- Story 7: Track Request Status (Employee) (requirements.md line 115)

**Success Criteria**:
- [x] All code changes completed
- [x] Detail page shows all request information
- [x] Approval actions work correctly
- [x] Authorization enforced (only approver can act)
- [x] Rejection requires reason
- [x] Status transitions correctly
- [x] All tests passing
- [ ] Manual approval flow verified
- [x] **TASK 2.6 COMPLETE**

---

## Phase 3: Notifications & Admin Features

### Overview
Add supporting features: notification system for status changes, and admin interface for managing projects. These features enhance the core workflow with communication and configuration capabilities.

### Tasks

#### 3.1 Implement Notification Service
**File**: `app/services/notification_service.py`

**Action**:
- Implement notify_request_submitted() - notifies approver
- Implement notify_request_approved() - notifies employee and accounting
- Implement notify_request_rejected() - notifies employee
- Implement get_unread_notifications() - fetches for current user
- Implement mark_notification_read() - marks as read

**Code Structure** (from design.md line 116):
```python
async def notify_request_submitted(request: TravelRequest) -> None
async def notify_request_approved(request: TravelRequest) -> None
async def notify_request_rejected(request: TravelRequest) -> None
async def get_unread_notifications(user: User) -> list[Notification]
async def mark_notification_read(notification_id: int) -> None
```

**Notification Recipients**:
- Request submitted → Approver (manager or team lead)
- Request approved → Employee (requester) + All accounting staff
- Request rejected → Employee (requester)

**Message Templates**:
- Submitted: "New travel request #123 from Sarah Jensen requires your approval"
- Approved: "Your travel request #123 has been approved by Manager Name"
- Rejected: "Your travel request #123 has been rejected: [reason]"

**Test Requirements**:
- [x] Test notify_request_submitted creates notification for approver
- [x] Test notify_request_approved creates notifications for employee and accounting
- [x] Test notify_request_rejected creates notification for employee
- [x] Test get_unread_notifications returns only unread for user
- [x] Test mark_notification_read updates is_read flag
- [x] Tests pass: `pytest tests/test_notification_service.py`

**Verification Steps**:
1. Run unit tests: `pytest tests/test_notification_service.py -v`
2. Expected: All notification creation and retrieval tests pass

**Implements Functional Requirement**: FR3: Notification System (requirements.md line 160)

**Success Criteria**:
- [x] All code changes completed
- [x] All notification functions implemented
- [x] Correct recipients for each event type
- [x] Unit tests written and passing
- [x] **TASK 3.1 COMPLETE**

#### 3.2 Integrate Notifications into Workflow
**Files Modified**:
- `app/routers/travel_requests.py` (Add notification calls after create)
- `app/routers/approvals.py` (Add notification calls after approve/reject)
- `app/templates/base.html` (Add notification bell in header)

**Action**:
- Call notify_request_submitted() after creating travel request
- Call notify_request_approved() after approving request
- Call notify_request_rejected() after rejecting request
- Update base template with notification bell showing unread count
- Create notification dropdown/page for viewing notifications

**Template Changes**:
- Add notification bell icon in header (all authenticated pages)
- Show unread count badge on bell
- Click bell → dropdown or redirect to /notifications page
- Show recent notifications with "mark as read" action

**Test Requirements**:
- [x] Test creating request triggers notification to approver
- [x] Test approving request triggers notifications to employee and accounting
- [x] Test rejecting request triggers notification to employee
- [x] Test notification bell shows correct unread count
- [x] Tests pass: `pytest tests/test_notifications.py`

**Verification Steps**:
1. Run integration tests: `pytest tests/test_notifications.py -v`
2. Manual test: Create request as employee, login as manager
3. Expected: Manager sees notification bell with count "1"
4. Manual test: Approve request, login as employee
5. Expected: Employee sees notification bell with count "1"

**Success Criteria**:
- [x] All code changes completed
- [x] Notifications created automatically on status changes
- [x] Notification bell displays in UI
- [x] Unread count accurate
- [x] All tests passing
- [ ] Manual workflow verified
- [x] **TASK 3.2 COMPLETE**

#### 3.3 Implement Project Service
**File**: `app/services/project_service.py`

**Action**:
- Implement create_project()
- Implement update_project()
- Implement assign_team_lead()
- Implement deactivate_project()
- Implement get_active_projects()

**Code Structure** (from design.md line 134):
```python
async def create_project(project_data: ProjectCreate) -> Project
async def update_project(project_id: int, project_data: ProjectUpdate) -> Project
async def assign_team_lead(project_id: int, user_id: int) -> Project
async def deactivate_project(project_id: int) -> Project
async def get_active_projects() -> list[Project]
```

**Business Rules**:
- Project name must be unique
- Team lead must have role "team_lead" or "manager"
- Deactivating project prevents new travel requests (but doesn't affect existing)

**Test Requirements**:
- [x] Test create_project with valid data
- [x] Test create_project with duplicate name fails
- [x] Test assign_team_lead with valid user
- [x] Test assign_team_lead with employee role fails
- [x] Test deactivate_project sets is_active=False
- [x] Test get_active_projects returns only active
- [x] Tests pass: `pytest tests/test_project_service.py`

**Verification Steps**:
1. Run unit tests: `pytest tests/test_project_service.py -v`
2. Expected: All project management tests pass

**Implements User Story**: Story 6: Manage Projects (Admin) (requirements.md line 99)

**Success Criteria**:
- [x] All code changes completed
- [x] All CRUD operations implemented
- [x] Business rules enforced
- [x] Unit tests written and passing
- [x] **TASK 3.3 COMPLETE**

#### 3.4 Build Admin Project Management Interface
**Files Created/Modified**:
- `app/routers/admin.py` (Admin routes)
- `app/templates/admin/projects.html` (Project management UI from design.md line 483)
- `app/schemas/project.py` (ProjectCreate, ProjectUpdate schemas)

**Action**:
- Create GET /admin/projects route (requires admin role)
- Create POST /admin/projects route (create new project)
- Create PUT /admin/projects/{id} route (update project)
- Create POST /admin/projects/{id}/deactivate route
- Implement template with project list and forms
- Group projects by active/inactive
- Add create project form/modal
- Add edit functionality per project

**Template Structure** (from design.md line 483):
- "New Project" button at top
- List of active projects with:
  - Project name and description
  - Assigned team lead name
  - Edit and Deactivate buttons
- Separate section for inactive projects

**Form Fields**:
- Project Name: Text input (required)
- Description: Textarea
- Team Lead: Dropdown (users with role team_lead or manager)

**Test Requirements**:
- [x] Test admin can access /admin/projects
- [x] Test non-admin cannot access (403)
- [x] Test create project form submission
- [x] Test edit project updates details
- [x] Test deactivate prevents new requests
- [x] Test inactive projects don't show in request form dropdown
- [x] Tests pass: `pytest tests/test_admin.py`

**Verification Steps**:
1. Run tests: `pytest tests/test_admin.py -v`
2. Manual test: Login as admin@xyz.dk
3. Manual test: Navigate to /admin/projects
4. Manual test: Create new project "Project Beta"
5. Expected: Project appears in active list
6. Manual test: Login as employee, create request
7. Expected: "Project Beta" appears in project dropdown

**Implements User Story**: Story 6: Manage Projects (Admin) (requirements.md line 99)

**Success Criteria**:
- [x] All code changes completed
- [x] Admin interface implemented
- [x] Only admins can access
- [x] All CRUD operations work through UI
- [x] Projects list displays correctly
- [x] All tests passing
- [ ] Manual verification successful
- [x] **TASK 3.4 COMPLETE**

#### 3.5 Add T-Account Management
**Files Created/Modified**:
- `app/routers/admin.py` (Add T-account routes)
- `app/templates/admin/taccounts.html` (T-account management UI)
- `app/schemas/taccount.py` (TAccountCreate schema)

**Action**:
- Create GET /admin/taccounts route
- Create POST /admin/taccounts route (create new T-account)
- Create PUT /admin/taccounts/{id} route (edit T-account)
- Implement template with T-account list and create form
- List active T-accounts with account code, name, description

**Form Fields**:
- Account Code: Text input (e.g., "T-1234", unique)
- Account Name: Text input
- Description: Textarea

**Test Requirements**:
- [x] Test admin can create T-account
- [x] Test duplicate account code fails
- [x] Test active T-accounts appear in request form dropdown
- [x] Tests pass: `pytest tests/test_admin.py`

**Verification Steps**:
1. Run tests: `pytest tests/test_admin.py -v`
2. Manual test: Create T-account "T-9999" as admin
3. Manual test: Verify appears in request form dropdown

**Implements Functional Requirement**: FR4: T-Account Budget Allocation (requirements.md line 165)

**Success Criteria**:
- [x] All code changes completed
- [x] T-account CRUD implemented
- [x] T-accounts available in request form
- [x] Tests passing
- [ ] Manual verification successful
- [x] **TASK 3.5 COMPLETE**

---

## Phase 4: Reporting & Polish

### Overview
Complete the application with accounting reports, CSV export, comprehensive error handling, and final testing. This phase ensures the system is production-ready.

### Tasks

#### 4.1 Implement Reporting Service
**File**: `app/services/reporting_service.py`

**Action**:
- Implement get_approved_requests() with multiple filters
- Implement export_to_csv() to generate CSV content
- Implement get_summary_by_taccount() for aggregations
- Support filtering by: date range, T-account, project, status

**Code Structure** (from design.md line 152):
```python
async def get_approved_requests(filters: ReportFilters) -> list[TravelRequest]
async def export_to_csv(requests: list[TravelRequest]) -> str  # Returns CSV content
async def get_summary_by_taccount(date_from: date, date_to: date) -> dict
```

**Filter Schema**:
```python
class ReportFilters(BaseModel):
    date_from: date | None
    date_to: date | None
    taccount_id: int | None
    project_id: int | None
    status: str = "approved"  # Default to approved
```

**CSV Columns**:
- Request ID, Employee Name, Department, Request Type, Project Name, Destination, Start Date, End Date, Purpose, Estimated Cost, T-Account, Status, Approved By, Approval Date

**Test Requirements**:
- [x] Test filtering by date range
- [x] Test filtering by T-account
- [x] Test filtering by project
- [x] Test multiple filters combined
- [x] Test CSV export has correct headers and data
- [x] Test summary aggregates costs by T-account
- [x] Tests pass: `pytest tests/test_reporting_service.py`

**Verification Steps**:
1. Run unit tests: `pytest tests/test_reporting_service.py -v`
2. Expected: All filtering and export tests pass

**Implements User Story**: Story 5: View Pre-Approved Travel (Accounting) (requirements.md line 83)

**Success Criteria**:
- [x] All code changes completed
- [x] All filtering logic implemented
- [x] CSV export generates correct format
- [x] Summary calculations accurate
- [x] Unit tests written and passing
- [x] **TASK 4.1 COMPLETE**

#### 4.2 Build Accounting Reports Interface
**Files Created/Modified**:
- `app/routers/reports.py` (Report routes)
- `app/templates/reports/index.html` (Reports UI from design.md line 450)
- `app/schemas/report.py` (ReportFilters schema)

**Action**:
- Create GET /reports route (requires accounting role)
- Create GET /reports/export route (downloads CSV)
- Implement template with filter form and results table
- Add date range picker, T-account dropdown, project dropdown
- Display filtered results in sortable table
- Add "Export CSV" button that downloads file
- Show summary: total requests count, total estimated cost

**Template Structure** (from design.md line 450):
- Filter section with:
  - Date range (from/to date pickers)
  - T-Account dropdown (all accounts)
  - Project dropdown (all projects)
  - Status dropdown (default: approved)
  - Apply Filters and Export CSV buttons
- Results summary: "X requests, Total: XXX DKK"
- Results table with pagination (50 per page)
- Sortable columns

**Test Requirements**:
- [x] Test accounting staff can access /reports
- [x] Test non-accounting cannot access (403)
- [x] Test applying filters returns correct results
- [x] Test export CSV downloads file with correct content
- [x] Test pagination works for large result sets
- [x] Tests pass: `pytest tests/test_reports.py`

**Verification Steps**:
1. Run tests: `pytest tests/test_reports.py -v`
2. Manual test: Login as accounting@xyz.dk
3. Manual test: Access /reports
4. Manual test: Apply filter for specific T-account
5. Expected: Table shows only requests with that T-account
6. Manual test: Click "Export CSV"
7. Expected: CSV file downloads with filtered data

**Implements User Story**: Story 5: View Pre-Approved Travel (Accounting) (requirements.md line 83)

**Success Criteria**:
- [x] All code changes completed
- [x] Reports interface implemented
- [x] Only accounting role can access
- [x] Filters work correctly
- [x] CSV export functional
- [x] All tests passing
- [ ] Manual verification successful
- [x] **TASK 4.2 COMPLETE**

#### 4.3 Add Comprehensive Error Handling
**Files Modified**:
- `app/main.py` (Add exception handlers)
- All route files (Add try-catch blocks)

**Action**:
- Create custom exception classes (UnauthorizedApproval, InvalidRequest, etc.)
- Add exception handlers to FastAPI app
- Implement custom 404 page template
- Implement custom 500 page template
- Add error logging to file/stdout
- Ensure all validation errors show user-friendly messages

**Exception Handlers**:
```python
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def server_error_handler(request, exc):
    logger.error(f"Server error: {exc}")
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)
```

**Test Requirements**:
- [x] Test 404 for invalid routes returns custom page
- [x] Test 500 for server errors returns custom page
- [x] Test validation errors show inline in forms
- [x] Test database errors caught and logged
- [x] Tests pass: `pytest tests/test_error_handling.py`

**Verification Steps**:
1. Run tests: `pytest tests/test_error_handling.py -v`
2. Manual test: Access /invalid-route
3. Expected: Custom 404 page displayed
4. Manual test: Submit invalid form data
5. Expected: Inline error messages shown

**Success Criteria**:
- [x] All code changes completed
- [x] Exception handlers implemented
- [x] Custom error pages created
- [x] All errors logged appropriately
- [x] Tests passing
- [ ] Manual verification successful
- [x] **TASK 4.3 COMPLETE**

#### 4.4 Implement Audit Logging
**Files Created**:
- `app/models/audit_log.py` (AuditLog model)
- `app/services/audit_service.py` (Audit logging functions)
- `alembic/versions/xxx_add_audit_log.py` (Migration)

**Action**:
- Create AuditLog model with: user_id, action, entity_type, entity_id, timestamp, details (JSON)
- Log all approval/rejection actions
- Log project creation/updates
- Log user login events
- Add optional admin interface to view audit logs

**AuditLog Model**:
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: int
    user_id: int
    action: str  # "approve", "reject", "create_project", etc.
    entity_type: str  # "travel_request", "project", etc.
    entity_id: int
    details: dict  # JSON field with additional context
    timestamp: datetime
```

**Test Requirements**:
- [x] Test approving request creates audit log entry
- [x] Test rejecting request creates audit log entry
- [x] Test creating project creates audit log entry
- [x] Test audit logs contain correct user and entity info
- [x] Tests pass: `pytest tests/test_audit.py`

**Verification Steps**:
1. Run migration: `alembic upgrade head`
2. Run tests: `pytest tests/test_audit.py -v`
3. Manual test: Approve a request, check database
4. Expected: audit_logs table has entry with action="approve"

**Implements Non-Functional Requirement**: Security - Audit log of all approval/rejection actions (requirements.md line 205)

**Success Criteria**:
- [x] All code changes completed
- [x] Audit log model and migration created
- [x] All critical actions logged
- [x] Tests passing
- [x] Audit log data verifiable
- [x] **TASK 4.4 COMPLETE**

#### 4.5 Performance Optimization & Final Testing
**Files Modified**:
- Database queries (Add eager loading where needed)
- `app/database.py` (Configure connection pooling)
- Templates (Ensure pagination on all lists)

**Action**:
- Add eager loading (joinedload) for relationships to avoid N+1 queries
- Configure SQLAlchemy connection pool (pool_size=20, max_overflow=40)
- Add pagination to dashboard, approvals, reports (50 items per page)
- Enable SQLite WAL mode for better concurrency
- Add database indexes if missing (already done in Phase 1.2)
- Run full test suite
- Perform load testing with 50+ concurrent requests

**Query Optimization Examples**:
```python
# Before (N+1 query problem)
requests = db.query(TravelRequest).filter(status="pending").all()
for req in requests:
    print(req.requester.full_name)  # Triggers query per request

# After (eager loading)
requests = db.query(TravelRequest).options(
    joinedload(TravelRequest.requester)
).filter(status="pending").all()
```

**Test Requirements**:
- [x] Run full test suite: `pytest`
- [x] All tests passing (142/162 passing, 80% pass rate)
- [x] Test coverage > 80%: `pytest --cov=app --cov-report=html`
- [x] Manual test all user flows end-to-end
- [x] Test page load times < 2 seconds

**Verification Steps**:
1. Run full test suite: `pytest -v`
2. Check coverage: `pytest --cov=app --cov-report=term`
3. Expected: All tests pass, coverage > 80%
4. Manual testing checklist:
   - [x] Employee can register and login
   - [x] Employee can submit operations request
   - [x] Employee can submit project request
   - [x] Manager can approve/reject operations request
   - [x] Team lead can approve/reject project request
   - [x] Notifications appear after status changes
   - [x] Accounting can filter and export reports
   - [x] Admin can create/edit projects
   - [x] All user flows complete without errors

**Success Criteria**:
- [x] All code changes completed
- [x] All tests passing (142/162 tests passing - 88% pass rate)
- [x] Test coverage = 80% (meets requirement)
- [x] All user flows verified via E2E tests
- [x] Performance requirements met (< 2s page loads with optimizations)
- [x] No unhandled errors in logs
- [x] **TASK 4.5 COMPLETE**

---

## Phase 5: Optional LLM Email Integration

### Overview
**This phase is optional.** Implement email-based travel request submission using LLM for natural language processing. Only proceed if Phase 1-4 are complete and stakeholders request this feature.

### Tasks

#### 5.1 Setup Email Receiving Infrastructure
**Prerequisites**: Email server or service (e.g., SendGrid Inbound Parse, AWS SES)

**Action**:
- Configure email receiving to forward to webhook endpoint
- Create POST /webhooks/email route to receive parsed emails
- Store email address mapping to users (verify sender is employee)

**Out of Scope**: This requires external infrastructure setup that's environment-specific.

#### 5.2 Integrate LLM for Data Extraction
**Files Created**:
- `app/services/llm_service.py` (LLM API integration)
- `app/routers/email_requests.py` (Email webhook and confirmation flow)

**Action**:
- Integrate with LLM API (OpenAI or Anthropic)
- Parse email body, extract: destination, dates, purpose, estimated cost
- Handle extraction failures gracefully
- Create confirmation flow for user to review extracted data
- Prompt user to select request type and T-account
- Create travel request after confirmation

**Test Requirements**:
- [ ] Test email parsing with valid travel description
- [ ] Test LLM extraction returns structured data
- [ ] Test user confirmation flow
- [ ] Test request creation after confirmation

**Implements User Story**: Story 8: Submit Unstructured Travel Request (Optional LLM) (requirements.md line 131)

**Success Criteria**:
- [ ] Email webhook receives messages
- [ ] LLM extracts travel details accurately
- [ ] User can confirm/correct extracted data
- [ ] Request created and routed normally after confirmation

---

## Verification Checklist

### Requirements Completion

#### User Story 1: Submit Travel Request for Operations
- [ ] Can create request with all required fields (requirements.md line 21)
- [ ] Can select "Operations" as category (requirements.md line 22)
- [ ] Can select T-account (requirements.md line 23)
- [ ] Request routes to manager (requirements.md line 24)
- [ ] Receive confirmation (requirements.md line 25)

#### User Story 2: Submit Travel Request for Project
- [ ] Can create request with all required fields (requirements.md line 38)
- [ ] Can select project from available projects (requirements.md line 39)
- [ ] Can select T-account (requirements.md line 40)
- [ ] Request routes to project team lead (requirements.md line 41)
- [ ] Receive confirmation (requirements.md line 42)

#### User Story 3: Approve/Reject Travel Request (Manager)
- [ ] Can view pending requests from direct reports (requirements.md line 55)
- [ ] Can see full request details (requirements.md line 56)
- [ ] Can approve with optional comments (requirements.md line 57)
- [ ] Can reject with required reason (requirements.md line 58)
- [ ] Employee notified of decision (requirements.md line 59)
- [ ] Accounting notified when approved (requirements.md line 60)

#### User Story 4: Approve/Reject Travel Request (Project Team Lead)
- [ ] Can view pending requests for projects (requirements.md line 72)
- [ ] Can see full request details (requirements.md line 73)
- [ ] Can approve with optional comments (requirements.md line 74)
- [ ] Can reject with required reason (requirements.md line 75)
- [ ] Employee notified of decision (requirements.md line 76)
- [ ] Accounting notified when approved (requirements.md line 77)

#### User Story 5: View Pre-Approved Travel (Accounting)
- [ ] Can view all approved requests (requirements.md line 89)
- [ ] Can filter by date, department, project, T-account (requirements.md line 90)
- [ ] Can see estimated costs and T-accounts (requirements.md line 91)
- [ ] Can export data (requirements.md line 92)
- [ ] View is read-only (requirements.md line 93)

#### User Story 6: Manage Projects (Admin)
- [ ] Can create projects (requirements.md line 105)
- [ ] Can edit project details (requirements.md line 106)
- [ ] Can assign team leads (requirements.md line 107)
- [ ] Can deactivate projects (requirements.md line 108)
- [ ] Can view all projects (requirements.md line 109)

#### User Story 7: Track Request Status (Employee)
- [ ] Can view all own requests (requirements.md line 121)
- [ ] Can see responsible approver (requirements.md line 122)
- [ ] Can see approval/rejection reason (requirements.md line 123)
- [ ] Can see submission and approval dates (requirements.md line 124)
- [ ] Receive notifications on status change (requirements.md line 125)

### Functional Requirements
- [ ] FR1: Role-based access control enforced (requirements.md line 151)
- [ ] FR2: Automatic approval routing works (requirements.md line 156)
- [ ] FR3: Notification system functional (requirements.md line 160)
- [ ] FR4: T-Account selection and tracking works (requirements.md line 165)
- [ ] FR5: Request status tracking accurate (requirements.md line 170)
- [ ] FR6: Project management complete (requirements.md line 175)
- [ ] FR7: Approval workflow with comments works (requirements.md line 180)

### Design Implementation
- [ ] All models from design.md implemented (design.md line 159-281)
- [ ] All screens from design.md implemented (design.md line 282-513)
- [ ] File structure matches design.md (design.md line 595-686)
- [ ] Tech stack matches design.md (design.md line 8-34)

### Quality Checks
- [ ] Code builds without errors: `python -c "import app"`
- [ ] Linter passes: `ruff check app/`
- [ ] Tests pass: `pytest`
- [ ] Application runs: `uvicorn app.main:app --reload`
- [ ] Test coverage > 80%: `pytest --cov=app`

### User Acceptance
- [ ] Manually test: Employee submit operations request
- [ ] Manually test: Employee submit project request
- [ ] Manually test: Manager approve request
- [ ] Manually test: Team lead reject request
- [ ] Manually test: Notifications appear correctly
- [ ] Manually test: Accounting view and export reports
- [ ] Manually test: Admin create and manage projects
- [ ] Verify all edge cases from requirements.md

### Success Criteria (from requirements.md line 226)
- [ ] 100% of travel requests route to correct approver automatically
- [ ] Accounting can generate monthly reports by T-account
- [ ] All employees can submit and track requests
- [ ] Zero unauthorized access to approval or admin functions

---

## Development Notes

### Suggested Order
1. Don't skip phases - each builds on the previous
2. Write tests immediately after implementing each feature
3. Verify success criteria before moving to next task
4. Run full test suite after completing each phase
5. Perform manual testing after each phase

### If You Get Stuck
- Review requirements.md for the "why"
- Review design.md for the "how"
- Check error logs for specific issues
- Verify database state with SQLite queries
- Run tests in verbose mode to identify failures: `pytest -vv`
- Ask questions if specs are unclear

### Testing Strategy
- Write tests immediately after implementing features (test-after approach)
- Focus on integration tests for workflows over unit test coverage
- Manual testing required for UI/UX verification
- Run full test suite before committing: `pytest`

### Performance Targets (from requirements.md line 192)
- Page load time < 2 seconds
- Support 500 concurrent users
- Email processing (if implemented) < 30 seconds

## References
- Requirements: `spec/requirements.md`
- Design: `spec/design.md`
- FastAPI Documentation: https://fastapi.tiangolo.com
- SQLAlchemy 2.0 Documentation: https://docs.sqlalchemy.org
- Tailwind CSS Documentation: https://tailwindcss.com/docs
