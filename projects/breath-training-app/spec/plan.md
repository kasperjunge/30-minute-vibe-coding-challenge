# Implementation Plan: Breath Training App

## Overview
Building a web-based breath training application using FastAPI, Jinja2 templates, and SQLite. The app helps users reduce stress through guided breathing exercises with visual animations, tracks their progress with streaks and statistics, and provides multiple evidence-based breathing patterns.

## Current State
- Empty project / Starting from scratch
- Target tech stack: Python 3.12, FastAPI, Jinja2, SQLite, Tailwind CSS, Vanilla JavaScript

## Desired End State
A fully functional web application where users can:
- Create accounts and log in securely
- Start breathing sessions within 2 clicks
- Practice with 3+ evidence-based breathing patterns
- See smooth 60fps breathing animations
- Track progress with streaks, session counts, and weekly calendars
- Customize session duration (2, 5, or 10 minutes)
- Access the app on desktop and mobile browsers

**Success Criteria:**
- [ ] All 9 user stories from requirements.md are implemented
- [ ] All acceptance criteria are met
- [ ] Application matches design specifications
- [ ] Code is tested and runs without errors
- [ ] Breathing animation is smooth (60fps) and synchronized
- [ ] Stats tracking works correctly (especially streaks)

## What We're NOT Doing
- Mobile native apps (iOS/Android)
- Social features or user-generated content
- Wearable/fitness tracker integration
- Video or meditation content beyond breathing
- Payment/subscription features
- Multiple languages (English only for v1)
- Offline/PWA functionality
- AI-powered recommendations
- Email verification (immediate access after signup)
- Password reset (can be added in v2)

## Implementation Approach
The implementation follows 5 discrete phases:
1. **Project Setup** - Establish foundation with FastAPI, database, and authentication
2. **Breathing Engine** - Build core breathing patterns and animated sessions
3. **Progress Tracking** - Implement statistics, streaks, and dashboard
4. **Enhanced Features** - Add onboarding, pattern library, settings, and polish
5. **Deployment** - Containerize and prepare for production

This order ensures each phase builds on a stable foundation. We can't track progress without authentication, can't show stats without sessions, and can't polish what doesn't exist yet.

---

## Phase 1: Project Setup & Foundation

### Overview
Initialize the Python project with UV, set up FastAPI with database models, implement user authentication, and create the base template structure with Tailwind CSS.

### Tasks

#### 1.1 Initialize Project with UV
**Action**:
- Initialize UV project with Python 3.12
- Install core dependencies: fastapi, uvicorn, sqlalchemy, aiosqlite, passlib[bcrypt], python-multipart, jinja2, itsdangerous
- Install dev dependencies: pytest, pytest-asyncio, httpx, ruff
- Create basic project structure

**Files Created**:
- `pyproject.toml` - Project configuration and dependencies
- `uv.lock` - Locked dependency versions
- `src/` - Main application directory
- `tests/` - Test directory
- `static/` - Static assets directory
- `.env.example` - Environment variables template

**Success Criteria**:
- [x] Project initializes: `uv init` completes
- [x] Dependencies install: `uv sync` completes without errors
- [x] Python version correct: `uv run python --version` shows 3.12+
- [x] Directory structure matches design.md

#### 1.2 Create FastAPI Application Structure
**File**: `src/main.py`
**Action**:
- Create FastAPI application instance
- Configure Jinja2 template directory
- Mount static files directory
- Add basic health check endpoint
- Configure CORS and security headers

**Code Structure**:
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Breath Training App")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="src/templates")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

**Test Requirements**:
- [ ] Write test to verify app starts correctly
- [ ] Test health endpoint returns 200
- [ ] Tests pass: `uv run pytest tests/test_main.py`

**Verification Steps**:
1. Run dev server: `uv run uvicorn src.main:app --reload`
2. Visit http://localhost:8000/health in browser
3. Expected: JSON response `{"status": "ok"}`

**Success Criteria**:
- [x] All code changes completed
- [x] Server starts without errors
- [x] Health endpoint responds correctly
- [x] Tests written and passing

#### 1.3 Setup Database Models and Connection
**Files**:
- `src/database.py` - Database connection and session management
- `src/models/user.py` - User model
- `src/models/session.py` - Session model
- `src/models/pattern.py` - BreathingPattern model
- `src/models/user_stats.py` - UserStats model
- `src/models/user_preference.py` - UserPreference model

**Action**:
- Configure SQLAlchemy with async SQLite
- Create database models matching design.md entities
- Add relationships between models
- Create database initialization function

**Data Models** (from design.md):
```python
# User model with email, password_hash, timestamps
# BreathingPattern with timing parameters
# Session with user_id, pattern_id, durations
# UserStats with streaks and totals
# UserPreference with settings
```

**Test Requirements**:
- [ ] Write tests for database connection
- [ ] Test model creation and relationships
- [ ] Test database initialization
- [ ] Tests pass: `uv run pytest tests/test_database.py`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_database.py -v`
2. Verify all models created successfully
3. Expected: All tests passing, database file created

**Success Criteria**:
- [ ] All code changes completed
- [ ] All 5 models defined per design.md
- [ ] Relationships configured correctly
- [ ] Database initializes without errors
- [ ] Tests written and passing

#### 1.4 Implement Authentication Service
**Files**:
- `src/services/auth_service.py` - Authentication business logic
- `src/utils/security.py` - Password hashing and session signing
- `src/schemas/auth.py` - Pydantic schemas for login/register

**Action**:
- Implement password hashing with bcrypt
- Create user registration function
- Create login authentication function
- Implement session token creation and validation
- Add logout functionality

**Functions to Implement**:
```python
async def register_user(email: str, password: str) -> User
async def authenticate_user(email: str, password: str) -> User | None
async def create_session(user_id: int) -> str
async def validate_session(token: str) -> User | None
async def delete_session(token: str) -> None
```

**Implements User Story**: Story 6 - Manage Account and Preferences

**Test Requirements**:
- [x] Test user registration with valid data
- [x] Test registration with duplicate email (should fail)
- [x] Test password hashing and verification
- [x] Test login with correct credentials
- [x] Test login with incorrect credentials
- [x] Test session creation and validation
- [x] Tests pass: `uv run pytest tests/test_auth.py`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_auth.py -v`
2. Verify all auth functions tested
3. Expected: All tests passing, password properly hashed

**Success Criteria**:
- [x] All code changes completed
- [x] All auth functions implemented
- [x] Password hashing uses bcrypt with 12 rounds
- [x] Session tokens cryptographically signed
- [x] Tests written and passing with 100% coverage

#### 1.5 Create Authentication Routes
**Files**:
- `src/routes/auth.py` - Login, register, logout endpoints
- `src/middleware/auth_middleware.py` - Session validation middleware

**Action**:
- Create POST /register endpoint
- Create POST /login endpoint
- Create POST /logout endpoint
- Implement middleware for session validation
- Add httpOnly, Secure, SameSite cookies

**Route Structure**:
```python
@router.post("/register")
async def register(request: RegisterRequest)
@router.post("/login")
async def login(request: LoginRequest, response: Response)
@router.post("/logout")
async def logout(response: Response)
```

**Implements User Story**: Story 6 - Manage Account and Preferences

**Test Requirements**:
- [ ] Test registration endpoint creates user
- [ ] Test login endpoint sets session cookie
- [ ] Test logout endpoint clears cookie
- [ ] Test middleware validates sessions
- [ ] Tests pass: `uv run pytest tests/test_routes.py::test_auth*`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_routes.py -v -k auth`
2. Manual test: Register via API, verify cookie set
3. Expected: Tests passing, cookies configured correctly

**Success Criteria**:
- [ ] All code changes completed
- [ ] Registration, login, logout working
- [ ] Cookies are httpOnly, Secure, SameSite=Lax
- [ ] Middleware blocks unauthenticated requests
- [ ] Tests written and passing

#### 1.6 Create Base Templates with Tailwind
**Files**:
- `src/templates/base.html` - Base layout template
- `src/templates/auth/login.html` - Login page
- `src/templates/auth/register.html` - Registration page
- `src/templates/landing.html` - Landing page for unauthenticated users
- `static/css/styles.css` - Tailwind setup

**Action**:
- Set up Tailwind CSS via CDN (for rapid development)
- Create base template with navigation and structure
- Build login and registration forms
- Create landing page with hero section
- Apply calming color palette (soft blues, greens, whites)

**Template Structure**:
```html
<!-- base.html with Tailwind, navigation, content block -->
<!-- login.html with email/password form -->
<!-- register.html with email/password form -->
<!-- landing.html with hero and CTA buttons -->
```

**Implements User Story**: Story 6 - Manage Account and Preferences

**Test Requirements**:
- [ ] Manual verification: Templates render correctly
- [ ] Manual verification: Forms submit properly
- [ ] Manual verification: Responsive on mobile and desktop
- [ ] Manual verification: Color scheme is calming

**Verification Steps**:
1. Start server: `uv run uvicorn src.main:app --reload`
2. Visit http://localhost:8000/ (landing page)
3. Visit http://localhost:8000/login (login form)
4. Visit http://localhost:8000/register (register form)
5. Expected: All pages render, forms work, styling applied

**Success Criteria**:
- [ ] All code changes completed
- [ ] Base template structure working
- [ ] Login and register forms functional
- [ ] Tailwind CSS applied correctly
- [ ] Manual verification confirms appearance

---

## Phase 2: Breathing Patterns & Session Engine

### Overview
Implement the core breathing functionality: pattern definitions, animated breathing sessions, session timer, and session tracking.

### Tasks

#### 2.1 Create Breathing Pattern Service
**Files**:
- `src/services/pattern_service.py` - Pattern management logic
- `src/routes/patterns.py` - Pattern endpoints

**Action**:
- Create preset breathing patterns (Box: 4-4-4-4, 4-7-8: 4-7-8-0, Coherent: 5-0-5-0)
- Implement function to seed database with presets
- Add functions to retrieve patterns
- Add validation for custom pattern timing

**Functions to Implement**:
```python
async def get_all_patterns(user_id: int | None) -> list[BreathingPattern]
async def get_pattern_by_id(pattern_id: int) -> BreathingPattern
async def create_preset_patterns() -> None
async def validate_pattern_timing(pattern: PatternCreate) -> bool
```

**Implements User Story**: Story 2 - Explore Different Breathing Techniques

**Test Requirements**:
- [ ] Test preset patterns created correctly
- [ ] Test pattern retrieval
- [ ] Test pattern validation (valid and invalid)
- [ ] Tests pass: `uv run pytest tests/test_patterns.py`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_patterns.py -v`
2. Verify preset patterns match design.md specifications
3. Expected: All tests passing, 3 presets available

**Success Criteria**:
- [ ] All code changes completed
- [ ] 3 preset patterns defined (Box, 4-7-8, Coherent)
- [ ] Pattern service functions implemented
- [ ] Tests written and passing

#### 2.2 Build Active Session Page
**Files**:
- `src/templates/session/active.html` - Active session template
- `src/routes/sessions.py` - Session start endpoint
- `static/js/breathing.js` - Breathing animation controller

**Action**:
- Create session start endpoint that creates Session record
- Build active session HTML template
- Implement circular breathing animation with CSS transforms
- Add phase labels ("Breathe In", "Hold", "Breathe Out")
- Create timer display (countdown format)

**Template Structure**:
```html
<!-- Header with pattern name, audio toggle, pause, close -->
<!-- Center: large circular div with CSS scale animation -->
<!-- Phase label below circle -->
<!-- Countdown timer at bottom -->
```

**JavaScript Animation**:
```javascript
// Cycle through phases using requestAnimationFrame
// Control CSS scale transform (1.0 to 1.8)
// Update phase label text
// Synchronize with pattern timing
```

**Implements User Story**: Story 1 - Quick Stress Relief

**Test Requirements**:
- [ ] Test session start endpoint creates Session record
- [ ] Manual verification: Animation is smooth (60fps)
- [ ] Manual verification: Timing matches pattern (±0.1s)
- [ ] Manual verification: Phase labels update correctly
- [ ] Tests pass: `uv run pytest tests/test_sessions.py::test_start*`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_sessions.py -v -k start`
2. Manual test: Start session, watch animation for full cycle
3. Use browser DevTools Performance tab to verify 60fps
4. Expected: Smooth animation, correct timing, labels sync

**Success Criteria**:
- [ ] All code changes completed
- [ ] Session start endpoint working
- [ ] Breathing animation smooth and synchronized
- [ ] Phase labels update correctly
- [ ] Backend tests passing
- [ ] Manual verification confirms visual quality

#### 2.3 Implement Session Timer and Controls
**Files**:
- `static/js/session.js` - Session timer and control logic
- Update: `src/templates/session/active.html` - Add control buttons

**Action**:
- Implement countdown timer with requestAnimationFrame
- Add pause button functionality (freeze timer and animation)
- Add close button with confirmation modal
- Track elapsed time for partial sessions
- Handle timer reaching 0:00 (auto-complete)

**Control Functions**:
```javascript
function startTimer(duration) { /* countdown from duration */ }
function pauseTimer() { /* freeze at current time */ }
function resumeTimer() { /* continue from paused time */ }
function stopSession() { /* show confirmation, send actual duration */ }
```

**Implements User Story**: Story 1 - Quick Stress Relief (pause/stop), Story 4 - Customize Practice Duration

**Test Requirements**:
- [ ] Manual verification: Timer counts down correctly
- [ ] Manual verification: Pause freezes timer and animation
- [ ] Manual verification: Resume continues correctly
- [ ] Manual verification: Close shows confirmation modal
- [ ] Manual verification: Timer reaching 0:00 triggers completion

**Verification Steps**:
1. Start session with 2-minute duration
2. Pause at 1:30 remaining, verify timer frozen
3. Resume, verify timer continues correctly
4. Click close, verify confirmation appears
5. Let timer reach 0:00, verify auto-completion
6. Expected: All controls work, timer accurate

**Success Criteria**:
- [ ] All code changes completed
- [ ] Timer counts down accurately
- [ ] Pause/resume functionality working
- [ ] Close button shows confirmation
- [ ] Auto-completion at 0:00 working
- [ ] Manual verification confirms all controls

#### 2.4 Create Session Tracking Service
**Files**:
- `src/services/session_service.py` - Session management logic
- Update: `src/routes/sessions.py` - Add completion endpoint

**Action**:
- Implement session start function (creates Session record)
- Implement session complete function (updates record, calculates completion %)
- Add logic for ≥50% completion counting toward progress
- Handle abandoned sessions (mark incomplete)

**Functions to Implement**:
```python
async def start_session(user_id: int, pattern_id: int, target_duration: int) -> Session
async def complete_session(session_id: int, actual_duration: int) -> Session
async def is_session_complete(target: int, actual: int) -> bool  # >=50% check
async def mark_abandoned_sessions(user_id: int) -> None
```

**Implements User Story**: Story 1 - Quick Stress Relief, Story 4 - Customize Practice Duration

**Test Requirements**:
- [ ] Test session creation
- [ ] Test full completion (actual = target)
- [ ] Test partial completion ≥50% (counts toward progress)
- [ ] Test partial completion <50% (doesn't count)
- [ ] Test abandoned session handling
- [ ] Tests pass: `uv run pytest tests/test_sessions.py`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_sessions.py -v`
2. Verify completion percentage logic is correct
3. Expected: All tests passing, 100% coverage on session functions

**Success Criteria**:
- [ ] All code changes completed
- [ ] Session start and complete functions working
- [ ] 50% threshold logic correct
- [ ] Abandoned sessions handled
- [ ] Tests written and passing

#### 2.5 Implement Session Completion Endpoint
**Files**:
- Update: `src/routes/sessions.py` - POST /session/{id}/complete
- `src/templates/session/complete.html` - Completion screen

**Action**:
- Create completion endpoint that accepts actual duration
- Call session_service.complete_session()
- Calculate if session counts toward progress
- Return completion data for display

**Route Structure**:
```python
@router.post("/session/{session_id}/complete")
async def complete_session(session_id: int, actual_duration: int)
```

**Implements User Story**: Story 9 - Complete a Session and Get Feedback

**Test Requirements**:
- [ ] Test completion endpoint updates Session record
- [ ] Test completion endpoint calculates is_completed correctly
- [ ] Test completion endpoint returns correct data
- [ ] Tests pass: `uv run pytest tests/test_routes.py::test_complete*`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_routes.py -v -k complete`
2. Manual test: Complete a session, verify database updated
3. Expected: Tests passing, Session record updated correctly

**Success Criteria**:
- [ ] All code changes completed
- [ ] Completion endpoint working
- [ ] Session records updated correctly
- [ ] Tests written and passing

---

## Phase 3: Progress Tracking & Statistics

### Overview
Implement statistics calculation (especially streak logic), create the dashboard with stats display, and build the session completion screen.

### Tasks

#### 3.1 Implement Statistics Service
**Files**:
- `src/services/stats_service.py` - Statistics calculation logic
- `src/utils/datetime_utils.py` - Timezone handling and date utilities

**Action**:
- Implement streak calculation function (consecutive days logic)
- Create function to update UserStats after session completion
- Add weekly calendar generation (current week, marked days)
- Implement timezone-aware date handling

**Functions to Implement**:
```python
async def update_stats_after_session(session: Session) -> UserStats
def calculate_streak(last_practice: date, current: date, current_streak: int) -> int
def generate_weekly_calendar(user_id: int, timezone: str) -> list[dict]
async def get_user_stats(user_id: int) -> UserStats
```

**Streak Logic** (from design.md):
- Same day: no change to streak
- Consecutive day: increment streak by 1
- Missed day(s): reset streak to 1

**Implements User Story**: Story 3 - Build a Consistent Practice

**Test Requirements**:
- [ ] Test streak continues on consecutive day
- [ ] Test streak resets after missed day
- [ ] Test multiple sessions same day (streak unchanged)
- [ ] Test total sessions and minutes increment
- [ ] Test longest streak tracking
- [ ] Test weekly calendar generation
- [ ] Tests pass: `uv run pytest tests/test_stats.py`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_stats.py -v`
2. Verify streak logic matches all cases from design.md
3. Expected: All tests passing, 100% coverage on stats functions

**Success Criteria**:
- [ ] All code changes completed
- [ ] Streak calculation logic correct
- [ ] Stats update after session completion
- [ ] Weekly calendar generation working
- [ ] Timezone handling correct
- [ ] Tests written and passing with 100% coverage

#### 3.2 Integrate Stats Update with Session Completion
**Files**:
- Update: `src/routes/sessions.py` - Call stats_service after completion

**Action**:
- Modify session completion endpoint to update UserStats
- Call stats_service.update_stats_after_session()
- Handle timezone from client (passed in request)
- Ensure stats update atomically with session completion

**Integration Point**:
```python
# In complete_session endpoint:
session = await session_service.complete_session(session_id, actual_duration, timezone)
if session.is_completed:
    stats = await stats_service.update_stats_after_session(session)
```

**Implements User Story**: Story 3 - Build a Consistent Practice

**Test Requirements**:
- [ ] Test session completion updates stats
- [ ] Test stats don't update for incomplete sessions (<50%)
- [ ] Test timezone passed correctly from client
- [ ] Tests pass: `uv run pytest tests/test_routes.py::test_complete_updates_stats`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_routes.py -v -k complete`
2. Manual test: Complete session, check database for updated stats
3. Expected: Tests passing, stats update correctly

**Success Criteria**:
- [ ] All code changes completed
- [ ] Stats update integrated with completion
- [ ] Incomplete sessions don't affect stats
- [ ] Timezone handling working
- [ ] Tests written and passing

#### 3.3 Build Dashboard with Stats Display
**Files**:
- `src/templates/dashboard/home.html` - Main dashboard template
- `src/templates/components/stats_card.html` - Stats display component
- `src/routes/dashboard.py` - Dashboard endpoint

**Action**:
- Create dashboard route that loads user stats
- Build stats card showing streak (with fire emoji), total sessions, total minutes
- Add weekly calendar view (M T W T F S S with checkmarks)
- Create quick start card with pattern selector and duration radio buttons
- Add profile dropdown with Settings and Logout

**Template Structure**:
```html
<!-- Welcome message with user name -->
<!-- Stats card: streak, sessions, minutes -->
<!-- Weekly calendar: 7 days with practice markers -->
<!-- Quick start: pattern dropdown, duration radios, start button -->
<!-- Navigation: profile dropdown -->
```

**Implements User Story**: Story 3 - Build a Consistent Practice, Story 1 - Quick Stress Relief

**Test Requirements**:
- [ ] Test dashboard endpoint loads stats correctly
- [ ] Manual verification: Stats display correctly
- [ ] Manual verification: Weekly calendar shows current week
- [ ] Manual verification: Quick start form works
- [ ] Tests pass: `uv run pytest tests/test_routes.py::test_dashboard`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_routes.py -v -k dashboard`
2. Manual test: Log in, view dashboard with stats
3. Complete a session, return to dashboard, verify stats updated
4. Expected: Tests passing, dashboard displays correct data

**Success Criteria**:
- [ ] All code changes completed
- [ ] Dashboard displays stats correctly
- [ ] Weekly calendar shows current week with markers
- [ ] Quick start form functional
- [ ] Manual verification confirms appearance
- [ ] Tests written and passing

#### 3.4 Create Session Completion Screen
**Files**:
- `src/templates/session/complete.html` - Completion screen template
- Update: `src/routes/sessions.py` - Render completion template

**Action**:
- Build completion screen with checkmark and positive message
- Display session summary (pattern, duration, time)
- Show updated streak if first session of day
- Display total minutes milestone
- Add "Practice Again" and "Back to Home" buttons

**Template Structure**:
```html
<!-- "Well Done!" header with checkmark -->
<!-- Session summary card -->
<!-- Updated streak display (if applicable) -->
<!-- Total minutes milestone -->
<!-- Action buttons -->
```

**Implements User Story**: Story 9 - Complete a Session and Get Feedback

**Test Requirements**:
- [ ] Manual verification: Completion screen renders correctly
- [ ] Manual verification: Session details displayed
- [ ] Manual verification: Streak update shown if applicable
- [ ] Manual verification: Buttons navigate correctly

**Verification Steps**:
1. Complete a full session (5 minutes)
2. Verify completion screen shows correct details
3. Check if streak update displayed (if first session of day)
4. Click "Back to Home", verify navigation
5. Expected: All details correct, navigation working

**Success Criteria**:
- [ ] All code changes completed
- [ ] Completion screen displays correctly
- [ ] Session details accurate
- [ ] Streak update shown when applicable
- [ ] Navigation buttons working
- [ ] Manual verification confirms appearance

---

## Phase 4: Enhanced Features & Polish

### Overview
Add onboarding flow, pattern library with customization, settings page, audio guidance, and polish UI/UX for responsive design.

### Tasks

#### 4.1 Implement Onboarding Flow
**Files**:
- `src/templates/onboarding/steps.html` - Onboarding screens
- `src/routes/onboarding.py` - Onboarding endpoints
- Update: `src/services/auth_service.py` - Check onboarding status

**Action**:
- Create 3-step onboarding flow (Welcome, Demo Session, Setup Complete)
- Implement 30-second demo breathing session (auto-plays)
- Add skip functionality at any point
- Update has_completed_onboarding flag on completion
- Redirect new users to onboarding after registration

**Onboarding Screens**:
1. Welcome message (1/3)
2. 30-second demo session (2/3, auto-proceeds)
3. Setup complete checklist (3/3)

**Implements User Story**: Story 5 - First-Time User Onboarding

**Test Requirements**:
- [ ] Test onboarding flag updates after completion
- [ ] Test onboarding shown only once
- [ ] Manual verification: 3 screens display correctly
- [ ] Manual verification: Demo session auto-plays
- [ ] Manual verification: Skip button works at any point
- [ ] Tests pass: `uv run pytest tests/test_onboarding.py`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_onboarding.py -v`
2. Manual test: Register new account, verify onboarding starts
3. Complete onboarding, log out, log in, verify onboarding skipped
4. Expected: Tests passing, onboarding only shows once

**Success Criteria**:
- [ ] All code changes completed
- [ ] Onboarding flow working
- [ ] Demo session auto-plays correctly
- [ ] Skip functionality working
- [ ] Onboarding flag set correctly
- [ ] Tests written and passing
- [ ] Manual verification confirms flow

#### 4.2 Build Pattern Library Page
**Files**:
- `src/templates/patterns/library.html` - Pattern library template
- `src/templates/components/pattern_card.html` - Pattern card component
- Update: `src/routes/patterns.py` - Pattern library endpoint

**Action**:
- Create pattern library page listing all patterns
- Build pattern cards with name, timing notation, description
- Add "Start Session" button (prompts for duration)
- Add "Customize" button for advanced users
- Display benefits and recommended use for each pattern

**Template Structure**:
```html
<!-- Back to Home link -->
<!-- Header: "Choose Your Pattern" -->
<!-- Pattern cards (3 presets) -->
<!-- Each card: name, timing, description, buttons -->
```

**Implements User Story**: Story 2 - Explore Different Breathing Techniques

**Test Requirements**:
- [ ] Test pattern library endpoint returns all patterns
- [ ] Manual verification: All 3 presets displayed
- [ ] Manual verification: Descriptions are clear
- [ ] Manual verification: Start button works
- [ ] Tests pass: `uv run pytest tests/test_routes.py::test_pattern_library`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_routes.py -v -k pattern`
2. Manual test: Navigate to pattern library
3. Verify all 3 patterns displayed with descriptions
4. Click "Start Session", verify duration selection appears
5. Expected: Tests passing, all patterns visible

**Success Criteria**:
- [ ] All code changes completed
- [ ] Pattern library displays 3 presets
- [ ] Pattern cards show timing and benefits
- [ ] Start button functional
- [ ] Manual verification confirms appearance
- [ ] Tests written and passing

#### 4.3 Implement Pattern Customization (Advanced)
**Files**:
- Update: `src/services/pattern_service.py` - Add custom pattern creation
- Update: `src/templates/patterns/library.html` - Add customization modal
- `static/js/pattern_customization.js` - Customization UI logic

**Action**:
- Create customization modal with timing sliders (1-10 seconds per phase)
- Implement custom pattern creation endpoint
- Validate pattern timing (no phase >10s, total cycle ≤60s)
- Save custom patterns linked to user
- Display custom patterns in user's pattern list

**Customization UI**:
```html
<!-- Modal with 4 sliders: inhale, inhale_hold, exhale, exhale_hold -->
<!-- Range: 0-10 seconds each -->
<!-- "Save Custom Pattern" button -->
<!-- "Reset to Default" button -->
```

**Implements User Story**: Story 8 - Adjust Breathing Pattern Timing (Advanced)

**Test Requirements**:
- [ ] Test custom pattern creation
- [ ] Test pattern validation (valid and invalid)
- [ ] Test custom patterns saved per user
- [ ] Manual verification: Sliders work correctly
- [ ] Manual verification: Validation shows errors for invalid patterns
- [ ] Tests pass: `uv run pytest tests/test_patterns.py::test_custom*`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_patterns.py -v -k custom`
2. Manual test: Open customization modal, adjust sliders
3. Save custom pattern, verify it appears in list
4. Test invalid pattern (total >60s), verify error shown
5. Expected: Tests passing, custom patterns work

**Success Criteria**:
- [ ] All code changes completed
- [ ] Customization modal working
- [ ] Custom pattern creation endpoint implemented
- [ ] Validation logic correct
- [ ] Custom patterns saved and retrieved
- [ ] Tests written and passing
- [ ] Manual verification confirms UI

#### 4.4 Create Settings Page
**Files**:
- `src/templates/settings/preferences.html` - Settings template
- `src/routes/settings.py` - Settings endpoints
- `src/services/preference_service.py` - Preference management

**Action**:
- Build settings page with preference controls
- Add default pattern dropdown
- Add audio guidance toggle
- Add reminder settings (enable + time picker)
- Add email display and change password button
- Implement save changes endpoint

**Settings Sections**:
- Default Pattern dropdown
- Audio Guidance checkbox
- Daily Reminders (enable + time)
- Account (email display, change password)
- Logout button

**Implements User Story**: Story 6 - Manage Account and Preferences, Story 7 - Receive Practice Reminders

**Test Requirements**:
- [ ] Test preferences update endpoint
- [ ] Test preference retrieval
- [ ] Manual verification: All settings save correctly
- [ ] Manual verification: Settings persist across sessions
- [ ] Tests pass: `uv run pytest tests/test_settings.py`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_settings.py -v`
2. Manual test: Change settings, save, log out, log in
3. Verify settings persisted correctly
4. Expected: Tests passing, settings save and load

**Success Criteria**:
- [ ] All code changes completed
- [ ] Settings page displays correctly
- [ ] All preferences save successfully
- [ ] Settings persist across sessions
- [ ] Tests written and passing
- [ ] Manual verification confirms functionality

#### 4.5 Add Audio Guidance
**Files**:
- `static/audio/inhale.mp3` - "Breathe in" audio cue
- `static/audio/hold.mp3` - "Hold" audio cue
- `static/audio/exhale.mp3` - "Breathe out" audio cue
- `static/js/audio_controller.js` - Audio playback logic
- Update: `static/js/breathing.js` - Integrate audio cues

**Action**:
- Find or create calming audio cues for each phase
- Implement audio controller to play cues at phase transitions
- Synchronize audio with visual animation
- Respect user's audio_enabled preference
- Add audio toggle button in active session

**Audio Integration**:
```javascript
// Play audio at start of each phase
function playAudioCue(phase) {
  if (audioEnabled) {
    const audio = new Audio(`/static/audio/${phase}.mp3`);
    audio.play();
  }
}
```

**Implements User Story**: Story 1 - Quick Stress Relief (audio guidance), FR3 - Audio Guidance

**Test Requirements**:
- [ ] Manual verification: Audio files play clearly
- [ ] Manual verification: Audio synchronized with animation
- [ ] Manual verification: Toggle on/off works
- [ ] Manual verification: No audio overlap or cutting off

**Verification Steps**:
1. Start session with audio enabled
2. Verify audio plays at each phase transition
3. Toggle audio off, verify no sound
4. Toggle back on, verify sound returns
5. Expected: Clear audio, synchronized, toggle works

**Success Criteria**:
- [ ] All code changes completed
- [ ] Audio files added (inhale, hold, exhale)
- [ ] Audio controller implemented
- [ ] Audio synchronized with animation
- [ ] Toggle functionality working
- [ ] Manual verification confirms quality

#### 4.6 Implement Browser Notifications
**Files**:
- `static/js/notifications.js` - Notification handler
- Update: `src/routes/settings.py` - Save reminder preferences

**Action**:
- Request notification permission from user
- Schedule daily reminder based on user's set time
- Show notification if browser is open at reminder time
- Handle permission denied gracefully (show notice in settings)
- Add reminder enable/disable and time picker in settings

**Notification Logic**:
```javascript
// Request permission
Notification.requestPermission().then(permission => { /* ... */ });

// Schedule reminder (check every minute if time matches)
function checkReminder() {
  const now = new Date();
  if (shouldShowReminder(now, reminderTime)) {
    showNotification();
  }
}
```

**Implements User Story**: Story 7 - Receive Practice Reminders

**Test Requirements**:
- [ ] Manual verification: Permission request appears
- [ ] Manual verification: Notification shows at set time
- [ ] Manual verification: Graceful degradation if permission denied
- [ ] Manual verification: Reminder time can be changed

**Verification Steps**:
1. Enable reminders in settings, set time to 1 minute from now
2. Wait for notification to appear
3. Verify notification content is appropriate
4. Test with permission denied scenario
5. Expected: Notification appears at correct time, graceful degradation

**Success Criteria**:
- [ ] All code changes completed
- [ ] Notification permission request implemented
- [ ] Reminder scheduling working
- [ ] Notification appears at set time
- [ ] Graceful handling of denied permission
- [ ] Manual verification confirms functionality

#### 4.7 Responsive Design & UI Polish
**Files**:
- Update: All templates - Add responsive classes
- Update: `static/css/styles.css` - Custom responsive styles
- Update: `src/templates/base.html` - Add viewport meta tag

**Action**:
- Test all pages on mobile (375px), tablet (768px), desktop (1440px)
- Add responsive Tailwind classes to all components
- Ensure breathing animation is visible on all screen sizes
- Verify touch targets are at least 44x44px on mobile
- Ensure no horizontal scrolling on any screen size
- Test in Chrome, Safari, Firefox, Edge

**Responsive Testing Checklist**:
- [ ] Landing page responsive
- [ ] Login/register forms responsive
- [ ] Dashboard responsive (stats card, calendar, quick start)
- [ ] Pattern library responsive (cards stack on mobile)
- [ ] Active session responsive (animation scales properly)
- [ ] Completion screen responsive
- [ ] Settings page responsive

**Implements**: FR12 - Responsive Design

**Test Requirements**:
- [ ] Manual verification: All pages work on 375px width
- [ ] Manual verification: All pages work on 768px width
- [ ] Manual verification: All pages work on 1440px+ width
- [ ] Manual verification: No horizontal scrolling
- [ ] Manual verification: Touch targets adequate on mobile
- [ ] Manual verification: Works in Chrome, Safari, Firefox, Edge

**Verification Steps**:
1. Open browser DevTools, toggle device toolbar
2. Test each page at 375px, 768px, 1440px widths
3. Verify all elements visible and usable
4. Test on actual mobile device if available
5. Expected: All pages responsive, no issues

**Success Criteria**:
- [ ] All code changes completed
- [ ] All pages responsive on mobile, tablet, desktop
- [ ] No horizontal scrolling
- [ ] Touch targets adequate
- [ ] Tested in 4 browsers
- [ ] Manual verification confirms quality

---

## Phase 5: Deployment & Production Readiness

### Overview
Create Docker container, configure production settings, set up database migrations, and add security headers.

### Tasks

#### 5.1 Create Dockerfile and Docker Compose
**Files**:
- `Dockerfile` - Container definition
- `docker-compose.yml` - Local development setup
- `.dockerignore` - Exclude unnecessary files

**Action**:
- Create multi-stage Dockerfile using Python 3.12
- Install dependencies with UV in container
- Configure uvicorn for production
- Create docker-compose.yml for easy local dev
- Add environment variable configuration

**Dockerfile Structure**:
```dockerfile
FROM python:3.12-slim
# Install UV
# Copy project files
# Install dependencies with UV
# Expose port 8000
# Run uvicorn
```

**Test Requirements**:
- [ ] Build Docker image: `docker build -t breath-app .`
- [ ] Run container: `docker-compose up`
- [ ] Test app accessible at http://localhost:8000
- [ ] Verify all features work in container

**Verification Steps**:
1. Build image: `docker build -t breath-app .`
2. Run container: `docker-compose up`
3. Visit http://localhost:8000, test core features
4. Expected: App runs in container, all features work

**Success Criteria**:
- [ ] All code changes completed
- [ ] Dockerfile builds successfully
- [ ] Docker Compose starts app correctly
- [ ] App accessible in container
- [ ] All features functional in containerized environment

#### 5.2 Setup Database Migrations with Alembic
**Files**:
- `alembic.ini` - Alembic configuration
- `migrations/env.py` - Migration environment
- `migrations/versions/001_initial.py` - Initial migration

**Action**:
- Install Alembic
- Initialize Alembic migrations
- Create initial migration from models
- Test migration up and down
- Document migration commands

**Migration Commands**:
```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

**Test Requirements**:
- [ ] Test initial migration creates all tables
- [ ] Test migration rollback removes tables
- [ ] Test migration idempotency (run twice)

**Verification Steps**:
1. Run migration: `uv run alembic upgrade head`
2. Verify database tables created correctly
3. Rollback: `uv run alembic downgrade -1`
4. Verify tables removed
5. Expected: Migrations work both directions

**Success Criteria**:
- [ ] All code changes completed
- [ ] Alembic configured correctly
- [ ] Initial migration created
- [ ] Migration up/down works correctly
- [ ] Migration commands documented

#### 5.3 Add Production Configuration
**Files**:
- `src/config.py` - Environment configuration
- `.env.example` - Environment variables template
- Update: `src/main.py` - Add production middleware

**Action**:
- Create configuration class for environment variables
- Add production/development mode toggle
- Configure HTTPS redirect in production
- Add security headers (CSP, HSTS, X-Frame-Options)
- Add CSRF protection middleware
- Add rate limiting on auth endpoints
- Set up logging with structlog

**Configuration Variables**:
```python
DATABASE_URL: str
SECRET_KEY: str  # For session signing
ENVIRONMENT: str  # "development" or "production"
ALLOWED_HOSTS: list[str]
HTTPS_ONLY: bool
```

**Security Headers**:
```python
# Content-Security-Policy
# Strict-Transport-Security (HSTS)
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
```

**Test Requirements**:
- [ ] Test configuration loads from environment
- [ ] Test security headers present in production mode
- [ ] Test CSRF protection blocks invalid requests
- [ ] Test rate limiting on /login endpoint
- [ ] Tests pass: `uv run pytest tests/test_config.py`

**Verification Steps**:
1. Run tests: `uv run pytest tests/test_config.py -v`
2. Start app in production mode
3. Verify security headers in HTTP response
4. Test rate limiting by making 11 requests to /login
5. Expected: Tests passing, security headers present, rate limiting works

**Success Criteria**:
- [ ] All code changes completed
- [ ] Configuration system working
- [ ] Security headers added
- [ ] CSRF protection enabled
- [ ] Rate limiting configured
- [ ] Logging set up
- [ ] Tests written and passing

#### 5.4 Write Deployment Documentation
**Files**:
- `README.md` - Project overview and setup
- `docs/DEPLOYMENT.md` - Production deployment guide

**Action**:
- Document local development setup
- Document Docker deployment steps
- Document environment variables
- Document database migration process
- Add troubleshooting section

**README Sections**:
- Project overview
- Quick start (local development)
- Tech stack
- Project structure
- Testing instructions
- Contributing guidelines

**Deployment Guide Sections**:
- Prerequisites
- Environment setup
- Docker deployment
- Database migrations
- Security considerations
- Monitoring and logs

**Test Requirements**:
- [ ] Manual verification: Follow README from scratch
- [ ] Manual verification: Follow deployment guide
- [ ] Manual verification: All commands work as documented

**Verification Steps**:
1. Follow README setup instructions on fresh machine
2. Verify all commands work correctly
3. Follow deployment guide to deploy to test environment
4. Expected: Documentation is clear and accurate

**Success Criteria**:
- [ ] All code changes completed
- [ ] README.md complete and accurate
- [ ] DEPLOYMENT.md complete and accurate
- [ ] Manual verification confirms accuracy

---

## Verification Checklist

### Requirements Completion

#### User Story 1: Quick Stress Relief
- [ ] User can begin breathing exercise within 2 clicks
- [ ] Default pattern starts for returning users
- [ ] Visual animation provides clear guidance
- [ ] Session continues smoothly without interruptions
- [ ] User can pause or stop at any time

#### User Story 2: Explore Different Breathing Techniques
- [ ] User can browse 3+ breathing patterns
- [ ] Each pattern has description of benefits
- [ ] User can preview pattern timing
- [ ] User can switch between patterns easily
- [ ] Patterns follow evidence-based timing

#### User Story 3: Build a Consistent Practice
- [ ] User can see total sessions completed
- [ ] User can see current streak
- [ ] User can see total minutes practiced
- [ ] User can view weekly calendar
- [ ] Statistics update immediately after session
- [ ] Streak increments only once per day

#### User Story 4: Customize Practice Duration
- [ ] User can select duration (2, 5, or 10 minutes)
- [ ] Timer counts down and shows remaining time
- [ ] Session ends automatically at 0:00
- [ ] User can end session early
- [ ] Sessions ≥50% complete count toward progress

#### User Story 5: First-Time User Onboarding
- [ ] First-time users see welcome screen
- [ ] Onboarding includes 30-second demo
- [ ] Instructions are clear and minimal
- [ ] User can skip onboarding
- [ ] User can start full session after onboarding
- [ ] Onboarding only shows once

#### User Story 6: Manage Account and Preferences
- [ ] User can create account with email/password
- [ ] User can log in with credentials
- [ ] User can log out
- [ ] User remains logged in across sessions
- [ ] Password meets security requirements
- [ ] Practice history requires login

#### User Story 7: Receive Practice Reminders
- [ ] User can enable/disable reminders
- [ ] User can set preferred time
- [ ] Reminders are optional (disabled by default)
- [ ] User can change reminder time
- [ ] Reminder appears as browser notification

#### User Story 8: Adjust Breathing Pattern Timing
- [ ] User can access advanced settings
- [ ] User can adjust timing independently
- [ ] Adjustments saved per pattern
- [ ] User can reset to defaults
- [ ] Animation adapts to custom timing
- [ ] Feature marked as "Advanced"

#### User Story 9: Complete Session and Get Feedback
- [ ] Completion screen shows pattern used
- [ ] Completion screen shows duration
- [ ] Completion screen shows time of day
- [ ] Updated streak displayed if first session of day
- [ ] Positive encouragement message shown
- [ ] User can start another session or return home

### Functional Requirements
- [ ] FR1: Breathing pattern engine with ±0.1s accuracy
- [ ] FR2: Visual animation smooth at 60fps and synchronized
- [ ] FR3: Audio guidance toggleable, clear, synchronized
- [ ] FR4: Secure authentication with persistent sessions
- [ ] FR5: Progress tracking with accurate timestamps
- [ ] FR6: Session timer with countdown display
- [ ] FR7: Session controls (pause and stop)
- [ ] FR8: Pattern library with 3+ patterns
- [ ] FR9: Weekly practice view for current week
- [ ] FR10: Browser notifications for reminders
- [ ] FR11: Pattern customization with reasonable bounds
- [ ] FR12: Responsive design (320px to 2560px)

### Non-Functional Requirements
- [ ] Initial page load <2 seconds on broadband
- [ ] Animation maintains 60fps on modern browsers
- [ ] Session start delay <500ms
- [ ] Statistics update <1 second after completion
- [ ] First-time users start session within 3 minutes
- [ ] Visual animation intuitive without text
- [ ] All actions within 2 clicks from home
- [ ] Calming color scheme (soft blues, greens)
- [ ] Text readable (min 14px, good contrast)
- [ ] Visual animation has sufficient contrast
- [ ] Audio cues available
- [ ] Keyboard navigation supported
- [ ] Screen reader friendly
- [ ] Progress data persists across closures
- [ ] Session state recovers from tab switching
- [ ] Authentication persists 7 days
- [ ] Passwords hashed with bcrypt
- [ ] User data private
- [ ] HTTPS required in production
- [ ] Protection against XSS, CSRF

### Quality Checks
- [ ] Code builds without errors: `uv run uvicorn src.main:app`
- [ ] Linter passes: `uv run ruff check src/`
- [ ] All tests pass: `uv run pytest`
- [ ] Test coverage ≥80%: `uv run pytest --cov=src`
- [ ] Application runs in Docker: `docker-compose up`
- [ ] Database migrations work: `uv run alembic upgrade head`

### Manual Testing
- [ ] Register new account, complete onboarding
- [ ] Log in, start breathing session with each pattern
- [ ] Complete full session, verify stats update
- [ ] Complete partial session, verify progress logic
- [ ] Test streak calculation across multiple days
- [ ] Customize pattern timing, start session with custom pattern
- [ ] Change settings, log out/in, verify settings persisted
- [ ] Enable reminders, verify notification appears
- [ ] Test on mobile device (responsive design)
- [ ] Test in Chrome, Safari, Firefox, Edge
- [ ] Test pause/resume during session
- [ ] Test early session ending
- [ ] Test weekly calendar shows correct days
- [ ] Test audio toggle during session

### User Acceptance
- [ ] User can complete breathing session in <2 minutes (first-time)
- [ ] User can complete breathing session in <30 seconds (returning)
- [ ] At least 3 breathing patterns available
- [ ] Progress data persists correctly
- [ ] Breathing animation smooth and synchronized
- [ ] App works on desktop and mobile browsers

---

## Development Notes

### Suggested Workflow
1. **Don't skip phases** - Each builds on the previous
2. **Verify success criteria** before moving to next task
3. **Run tests frequently** during development
4. **Manual test after each UI change** to catch visual issues early
5. **Commit after each completed task** with descriptive message
6. **Update this document** if you discover issues in specs

### If You Get Stuck
- **Review requirements.md** for the "why" behind features
- **Review design.md** for the "how" (architecture, data models)
- **Run tests to identify failing logic** before debugging manually
- **Check console and network tab** for frontend issues
- **Ask questions** if specs are unclear
- **Update specs** if you find gaps or ambiguities

### Testing Workflow
1. Implement feature/function
2. Manually test basic functionality
3. Write comprehensive automated tests (for backend)
4. Refactor if needed
5. Verify all tests pass
6. Mark task complete

### Critical Rules
- ✅ **Every backend feature requires tests** before marking complete
- ✅ **All tests must pass** before moving to next task
- ✅ **If tests fail 3+ times**, stop and reassess approach
- ✅ **Frontend requires manual testing** in Chrome and Safari minimum
- ✅ **Document any skipped tests** with reason and TODO comment
- ✅ **Commit early and often** to avoid losing work

---

## References
- **Requirements**: `spec/requirements.md`
- **Design**: `spec/design.md`
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **UV Documentation**: https://docs.astral.sh/uv/
- **Pytest**: https://docs.pytest.org/
- **Alembic**: https://alembic.sqlalchemy.org/
