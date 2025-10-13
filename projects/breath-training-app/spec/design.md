# Design: Breath Training App

## Design Overview
A server-rendered web application using FastAPI and Jinja2 templates with client-side JavaScript for real-time breathing animations. The architecture uses session-based authentication with SQLite for data persistence, deployed as a Docker container. The design prioritizes simplicity, smooth animations, and reliable progress tracking while keeping the user experience calm and focused.

## Tech Stack

### Languages & Frameworks
- **Language**: Python 3.12
- **Backend Framework**: FastAPI 0.115+
- **Template Engine**: Jinja2 (built into FastAPI)
- **Package Manager**: uv
- **Styling**: Tailwind CSS 3.4+
- **Frontend JavaScript**: Vanilla ES6+ (no framework needed)

### Data & State
- **Database**: SQLite 3 (via SQLAlchemy 2.0+)
- **ORM**: SQLAlchemy with async support
- **Session Management**: Server-side sessions with httpOnly cookies (using itsdangerous for signing)
- **Password Hashing**: bcrypt via passlib
- **Data Format**: Relational data in SQLite, JSON for API responses where needed

### Dependencies
- **fastapi**: Web framework and routing
- **uvicorn**: ASGI server
- **sqlalchemy**: Database ORM with async support
- **aiosqlite**: Async SQLite driver
- **passlib[bcrypt]**: Password hashing
- **python-multipart**: Form data handling
- **jinja2**: Template rendering (included with FastAPI)
- **itsdangerous**: Session token signing

### Development Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **httpx**: HTTP client for testing FastAPI
- **ruff**: Linting and formatting

**Rationale**: This stack provides a lightweight, fast, and maintainable solution. FastAPI offers excellent performance with async support, Jinja2 templates work seamlessly with server-side rendering for better SEO and simpler state management, and SQLite eliminates database server complexity while being sufficient for the scale. Tailwind enables rapid UI development with a calming, responsive design. Using `uv` dramatically speeds up dependency installation and environment management.

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────┐
│         Browser (Client)                │
│  ┌─────────────────────────────────┐   │
│  │  Jinja2 Templates (HTML)        │   │
│  │  + Tailwind CSS                 │   │
│  │  + Vanilla JavaScript           │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │ HTTP/HTTPS + Session Cookie
┌──────────────▼──────────────────────────┐
│         FastAPI Server                  │
│  ┌─────────────────────────────────┐   │
│  │  Route Handlers                 │   │
│  ├─────────────────────────────────┤   │
│  │  Authentication Middleware      │   │
│  ├─────────────────────────────────┤   │
│  │  Business Logic Layer           │   │
│  │  (Session tracking, streaks)    │   │
│  ├─────────────────────────────────┤   │
│  │  SQLAlchemy ORM                 │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         SQLite Database                 │
│  (users, sessions, patterns,            │
│   user_preferences)                     │
└─────────────────────────────────────────┘
```

### Component Breakdown

#### Component: Authentication System
**Purpose**: Handle user registration, login, logout, and session management  
**Location**: `src/auth/`  
**Responsibilities**:
- User registration with email validation and password hashing
- Login credential verification
- Session creation and validation
- Logout and session cleanup
- Password requirements enforcement

**Key Modules**:
```python
# src/auth/service.py
class AuthService:
    async def register_user(email: str, password: str) -> User
    async def authenticate_user(email: str, password: str) -> User | None
    async def create_session(user_id: int) -> str  # Returns session token
    async def validate_session(token: str) -> User | None
    async def delete_session(token: str) -> None
    def hash_password(password: str) -> str
    def verify_password(plain: str, hashed: str) -> bool
```

**Session Management**:
- Sessions stored as httpOnly, Secure, SameSite=Lax cookies
- Session tokens are cryptographically signed using itsdangerous
- 7-day expiration unless user logs out
- Middleware validates session on protected routes

#### Component: Breathing Pattern Engine
**Purpose**: Define and serve breathing pattern configurations  
**Location**: `src/patterns/`  
**Responsibilities**:
- Store predefined breathing patterns (Box, 4-7-8, Coherent)
- Provide pattern details and timing to frontend
- Handle custom pattern adjustments (advanced feature)
- Validate pattern timing parameters

**Data Structure**:
```python
# src/patterns/models.py
class BreathingPattern:
    id: int
    name: str
    slug: str  # e.g., "box-breathing"
    description: str
    inhale_duration: int  # seconds
    inhale_hold_duration: int
    exhale_duration: int
    exhale_hold_duration: int
    is_preset: bool  # True for defaults, False for user customs
    user_id: int | None  # None for presets, user_id for customs
```

**Preset Patterns**:
- Box Breathing: 4-4-4-4 (equal phases)
- 4-7-8 Breathing: 4-7-8-0 (relaxation focused)
- Coherent Breathing: 5-0-5-0 (balanced, no holds)

#### Component: Session Tracking System
**Purpose**: Record and manage breathing practice sessions  
**Location**: `src/sessions/`  
**Responsibilities**:
- Create new session when user starts practice
- Update session on completion or early stop
- Calculate session duration and completion percentage
- Determine if session counts toward progress (≥50% complete)
- Update user statistics (total sessions, minutes, streaks)

**Data Structure**:
```python
# src/sessions/models.py
class Session:
    id: int
    user_id: int
    pattern_id: int
    target_duration: int  # seconds (120, 300, or 600)
    actual_duration: int  # seconds actually practiced
    completed_at: datetime
    is_completed: bool  # True if ≥50% of target
    
class UserStats:
    user_id: int
    total_sessions: int
    total_minutes: int
    current_streak: int
    longest_streak: int
    last_practice_date: date
```

**Streak Calculation Logic**:
- Streak increments if user practices today and practiced yesterday
- Streak resets to 1 if user practices today but missed yesterday
- Streak remains unchanged for multiple sessions in same day
- Uses user's local timezone for "day" calculation (passed from client)

#### Component: Progress Dashboard
**Purpose**: Display user statistics and practice history  
**Location**: `src/dashboard/`  
**Responsibilities**:
- Aggregate user statistics (sessions, minutes, streaks)
- Generate weekly calendar view of practice days
- Format data for display in templates
- Calculate milestone achievements

**Weekly Calendar Logic**:
- Shows current week (Monday through Sunday)
- Each day marked as practiced (✓) or not (−)
- Timezone-aware based on user's location
- Updates in real-time after session completion

#### Component: Breathing Animation Controller
**Purpose**: Client-side JavaScript for smooth breathing animation  
**Location**: `static/js/breathing.js`  
**Responsibilities**:
- Control circular breathing animation (expand/contract)
- Synchronize animation with pattern timing
- Update phase labels ("Breathe In", "Hold", "Breathe Out")
- Manage session countdown timer
- Handle pause/resume/stop controls
- Play audio cues if enabled

**Animation Approach**:
- CSS transitions for smooth circle scaling
- JavaScript requestAnimationFrame for precise timing
- Circle scales from 100% to 180% during inhale
- Phase transitions use bezier easing for natural feel

#### Component: User Preferences
**Purpose**: Store and manage user settings  
**Location**: `src/preferences/`  
**Responsibilities**:
- Save default pattern selection
- Store audio enabled/disabled preference
- Manage reminder settings (time, enabled)
- Track onboarding completion status

**Data Structure**:
```python
# src/preferences/models.py
class UserPreference:
    user_id: int
    default_pattern_id: int | None
    audio_enabled: bool = True
    reminder_enabled: bool = False
    reminder_time: time | None  # e.g., 09:00
    has_completed_onboarding: bool = False
```

## Data Model

### Entity: User
```python
class User:
    id: int  # Primary key
    email: str  # Unique, indexed
    password_hash: str
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    sessions: list[Session]
    stats: UserStats
    preferences: UserPreference
    custom_patterns: list[BreathingPattern]
```

**Purpose**: Stores user account information  
**Relationships**: One-to-many with Sessions, one-to-one with UserStats and UserPreference

### Entity: BreathingPattern
```python
class BreathingPattern:
    id: int  # Primary key
    name: str
    slug: str  # URL-friendly identifier
    description: str
    inhale_duration: int
    inhale_hold_duration: int
    exhale_duration: int
    exhale_hold_duration: int
    is_preset: bool
    user_id: int | None  # Foreign key, null for presets
    created_at: datetime
```

**Purpose**: Defines breathing pattern timing and metadata  
**Relationships**: Many-to-one with User (for custom patterns), one-to-many with Sessions

### Entity: Session
```python
class Session:
    id: int  # Primary key
    user_id: int  # Foreign key
    pattern_id: int  # Foreign key
    target_duration: int  # In seconds
    actual_duration: int  # In seconds
    completed_at: datetime  # Timestamp with timezone
    is_completed: bool  # True if actual >= target * 0.5
    timezone: str  # e.g., "America/New_York"
    
    # Relationships
    user: User
    pattern: BreathingPattern
```

**Purpose**: Records individual breathing practice sessions  
**Relationships**: Many-to-one with User and BreathingPattern

### Entity: UserStats
```python
class UserStats:
    user_id: int  # Primary key, foreign key
    total_sessions: int = 0
    total_minutes: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_practice_date: date | None
    updated_at: datetime
    
    # Relationships
    user: User
```

**Purpose**: Aggregated statistics for quick display  
**Relationships**: One-to-one with User

### Entity: UserPreference
```python
class UserPreference:
    user_id: int  # Primary key, foreign key
    default_pattern_id: int | None  # Foreign key
    audio_enabled: bool = True
    reminder_enabled: bool = False
    reminder_time: time | None
    has_completed_onboarding: bool = False
    updated_at: datetime
    
    # Relationships
    user: User
    default_pattern: BreathingPattern | None
```

**Purpose**: User-specific settings and preferences  
**Relationships**: One-to-one with User, many-to-one with BreathingPattern

## User Interface Design

### Screen: Landing Page (Unauthenticated)
**Purpose**: Introduce app and encourage signup/login  
**Route**: `/`  
**Layout**:
```
┌─────────────────────────────────────────┐
│  [Logo] Breath         [Login] [Sign Up]│
├─────────────────────────────────────────┤
│                                         │
│     Find Calm Through Breathing         │
│     [Large calming gradient circle]     │
│                                         │
│     Reduce stress in minutes with       │
│     guided breathing exercises          │
│                                         │
│     [Try Demo Session →]                │
│                                         │
├─────────────────────────────────────────┤
│  Features: 3 Patterns | Track Progress  │
└─────────────────────────────────────────┘
```

**Key Elements**:
- Hero section with subtle animated circle (preview of breathing)
- Clear CTA buttons for signup/login
- Optional: Demo session without login (limited functionality)
- Calming color palette: soft blues, greens, whites

### Screen: Onboarding Flow (First Login)
**Purpose**: Guide new users through first experience  
**Route**: `/onboarding`  
**Screens**:

1. Welcome (1/3)
```
┌─────────────────────────────────────────┐
│     Welcome to Your Practice            │
│                                         │
│     Take a moment to breathe deeply     │
│     and let's get started               │
│                                         │
│     [Continue →]              [Skip]    │
└─────────────────────────────────────────┘
```

2. Demo Session (2/3)
```
┌─────────────────────────────────────────┐
│     Let's try a quick session           │
│                                         │
│     [Breathing circle animation]        │
│     "Breathe In"                        │
│                                         │
│     30-second demo running...           │
│     (Auto-proceeds to next)             │
└─────────────────────────────────────────┘
```

3. Setup Complete (3/3)
```
┌─────────────────────────────────────────┐
│     You're all set!                     │
│                                         │
│     ✓ Breathing basics learned          │
│     ✓ Choose from 3 patterns            │
│     ✓ Track your progress               │
│                                         │
│     [Start Your Practice →]             │
└─────────────────────────────────────────┘
```

**User Interactions**:
- Can skip onboarding at any point
- Demo session runs automatically (non-interactive)
- After completion, redirected to home dashboard
- Onboarding flag set in database, won't show again

### Screen: Home Dashboard (Authenticated)
**Purpose**: Central hub showing stats and quick start  
**Route**: `/dashboard`  
**Layout**:
```
┌─────────────────────────────────────────┐
│  [Logo]                [Profile ▾]      │
├─────────────────────────────────────────┤
│  Good morning, [Name]                   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Your Progress                  │   │
│  │  🔥 7 day streak                │   │
│  │  📊 24 sessions | 120 minutes   │   │
│  │                                 │   │
│  │  This Week:  M T W T F S S      │   │
│  │              ✓ ✓ ✓ ✓ ✓ − −      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Start a Session                │   │
│  │                                 │   │
│  │  Pattern: [Box Breathing ▾]     │   │
│  │  Duration: ⦿ 2min  ○ 5min  ○ 10min│
│  │                                 │   │
│  │  [Start Practice]               │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Explore Patterns] [Settings]          │
└─────────────────────────────────────────┘
```

**Key Elements**:
- Stats card: streak (with fire emoji if active), total sessions, total minutes
- Weekly calendar: simple grid showing practice days
- Quick start card: pattern selector, duration radio buttons, start button
- Profile dropdown: Settings, Logout

**User Interactions**:
- Select pattern → updates selection
- Select duration → updates radio button
- Click Start → navigates to active session screen
- Dropdown provides access to settings and logout

### Screen: Pattern Library
**Purpose**: Browse and learn about breathing patterns  
**Route**: `/patterns`  
**Layout**:
```
┌─────────────────────────────────────────┐
│  ← Back to Home                         │
├─────────────────────────────────────────┤
│  Choose Your Pattern                    │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Box Breathing              4-4-4-4│
│  │                                 │   │
│  │  Equal breathing for calm focus.│   │
│  │  Great for anxiety relief.      │   │
│  │                                 │   │
│  │  [Start Session] [Customize]    │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  4-7-8 Breathing            4-7-8 │
│  │                                 │   │
│  │  Relaxation technique for       │   │
│  │  stress and better sleep.       │   │
│  │                                 │   │
│  │  [Start Session] [Customize]    │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Coherent Breathing         5-5  │   │
│  │                                 │   │
│  │  Balanced breathing for heart   │   │
│  │  rate variability and calm.     │   │
│  │                                 │   │
│  │  [Start Session] [Customize]    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Key Elements**:
- Pattern cards with name, timing notation, description
- Start Session button (goes to duration selection)
- Customize button (advanced users, opens modal)

**User Interactions**:
- Start Session → prompts for duration → starts session
- Customize → opens modal with timing sliders (1-10 seconds each phase)

### Screen: Active Session
**Purpose**: Guide user through breathing session  
**Route**: `/session/{session_id}`  
**Layout**:
```
┌─────────────────────────────────────────┐
│  Box Breathing         [🔊] [✕] [⏸]    │
├─────────────────────────────────────────┤
│                                         │
│                                         │
│              [  ●  ]                    │
│           Breathing Circle              │
│           (expands/contracts)           │
│                                         │
│             Breathe In                  │
│                                         │
│                                         │
│              4:23                       │
│         Remaining Time                  │
│                                         │
└─────────────────────────────────────────┘
```

**Key Elements**:
- Top bar: Pattern name, audio toggle, close button, pause button
- Center: Large circular animation (100% to 180% scale)
- Phase label: "Breathe In" / "Hold" / "Breathe Out"
- Countdown timer: Minutes:Seconds remaining
- Minimal UI to avoid distraction

**User Interactions**:
- Circle expands during inhale (CSS scale transform)
- Circle contracts during exhale
- Pause button → freezes animation and timer
- Close button → shows "End Session Early?" confirmation
- Audio toggle → enables/disables audio cues
- Timer counts down to 0:00

**Animation Details**:
```javascript
// Breathing phases controlled by JavaScript
const phases = [
  { name: 'Breathe In', duration: 4, scale: 1.8 },
  { name: 'Hold', duration: 4, scale: 1.8 },
  { name: 'Breathe Out', duration: 4, scale: 1.0 },
  { name: 'Hold', duration: 4, scale: 1.0 }
];
// Cycle through phases using requestAnimationFrame
```

### Screen: Session Completion
**Purpose**: Celebrate completion and update stats  
**Route**: `/session/{session_id}/complete`  
**Layout**:
```
┌─────────────────────────────────────────┐
│                                         │
│              Well Done! ✓               │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Box Breathing                  │   │
│  │  5 minutes                      │   │
│  │  Completed at 2:45 PM           │   │
│  │                                 │   │
│  │  🔥 Day 8 streak!               │   │
│  └─────────────────────────────────┘   │
│                                         │
│  You've practiced for 125 total         │
│  minutes. Keep up the great work.       │
│                                         │
│  [Practice Again] [Back to Home]        │
│                                         │
└─────────────────────────────────────────┘
```

**Key Elements**:
- Completion checkmark and positive message
- Session summary card: pattern, duration, time
- Updated streak display (if applicable)
- Total minutes milestone
- Action buttons for next steps

**User Interactions**:
- Practice Again → returns to duration selection
- Back to Home → returns to dashboard
- Stats automatically saved to database

### Screen: Settings
**Purpose**: Manage preferences and account  
**Route**: `/settings`  
**Layout**:
```
┌─────────────────────────────────────────┐
│  ← Back                                 │
├─────────────────────────────────────────┤
│  Settings                               │
│                                         │
│  Default Pattern                        │
│  [Box Breathing ▾]                      │
│                                         │
│  Audio Guidance                         │
│  [✓] Enable audio cues                  │
│                                         │
│  Daily Reminders                        │
│  [ ] Enable daily reminder              │
│  Reminder time: [09:00]                 │
│                                         │
│  Account                                │
│  Email: user@example.com                │
│  [Change Password]                      │
│                                         │
│  [Save Changes]                         │
│                                         │
│  [Logout]                               │
└─────────────────────────────────────────┘
```

**Key Elements**:
- Default pattern dropdown
- Audio toggle checkbox
- Reminder settings (enable + time picker)
- Account email display
- Change password button
- Logout button

**User Interactions**:
- Change settings → Save Changes updates database
- Change Password → opens modal with current/new password fields
- Logout → clears session and redirects to landing

## Key Interactions & Flows

### Flow: First-Time User Registration
**Scenario**: New user creates account and completes onboarding

1. User lands on `/` (landing page)
2. User clicks "Sign Up"
3. System shows registration form (email + password)
4. User submits form
5. System validates email format and password requirements
6. System creates user account (hashed password)
7. System creates session and sets httpOnly cookie
8. System creates UserStats and UserPreference records
9. System redirects to `/onboarding`
10. User completes 3-step onboarding (or skips)
11. System sets `has_completed_onboarding = True`
12. System redirects to `/dashboard`
13. User sees welcome message and empty stats

**Error Handling**:
- If email already exists → "Email already registered" message
- If password too weak → "Password must be at least 8 characters with number and special character"
- If validation fails → show inline error messages, don't clear form

### Flow: Returning User Quick Start
**Scenario**: User logs in and starts default breathing session

1. User lands on `/` and clicks "Login"
2. User enters email and password
3. System validates credentials
4. System creates session and sets httpOnly cookie
5. System redirects to `/dashboard` (skips onboarding)
6. System loads user's stats and preferences
7. Dashboard shows default pattern pre-selected
8. User selects duration (e.g., 5 minutes)
9. User clicks "Start Practice"
10. System creates session record (status: in_progress)
11. System redirects to `/session/{session_id}`
12. JavaScript initializes breathing animation
13. Timer begins countdown from 5:00

**Error Handling**:
- If credentials invalid → "Invalid email or password"
- If session creation fails → retry once, then show error page

### Flow: Complete Breathing Session
**Scenario**: User completes full breathing session and sees updated stats

1. User is in active session (`/session/{session_id}`)
2. JavaScript manages breathing cycle animation
3. Timer counts down from selected duration
4. Each breath cycle: inhale → hold → exhale → hold
5. Audio cues play at phase transitions (if enabled)
6. Timer reaches 0:00
7. JavaScript sends POST request to `/api/session/{session_id}/complete`
8. System updates session record:
   - `actual_duration = target_duration`
   - `is_completed = True`
   - `completed_at = current_timestamp`
9. System updates UserStats:
   - Increment `total_sessions`
   - Add to `total_minutes`
   - Recalculate streak (check if practice today and yesterday)
10. System redirects to `/session/{session_id}/complete`
11. User sees completion screen with updated stats
12. User clicks "Back to Home"
13. Dashboard shows updated streak and session count

**Error Handling**:
- If network fails during completion → retry automatically (3 attempts)
- If retry fails → store completion in localStorage, sync on next page load
- If timezone detection fails → default to UTC, log warning

### Flow: End Session Early
**Scenario**: User stops session before completion

1. User is in active session with 2:30 remaining (out of 5:00)
2. User clicks close button (✕)
3. System shows modal: "End session early? Progress will still be saved."
4. User clicks "End Session"
5. JavaScript sends POST request with actual duration (2:30)
6. System calculates completion: 2.5 / 5.0 = 50% (exactly at threshold)
7. System updates session record:
   - `actual_duration = 150` (seconds)
   - `is_completed = True` (≥50%)
   - `completed_at = current_timestamp`
8. System updates UserStats (counts toward progress)
9. System redirects to completion screen with "Good effort!" message

**Error Handling**:
- If user closes browser without clicking button → session remains in_progress
- On next dashboard visit, system detects abandoned session → marks as incomplete
- Incomplete sessions (<50%) don't count toward stats but are logged for reference

### Flow: Customize Breathing Pattern (Advanced)
**Scenario**: Experienced user adjusts 4-7-8 pattern timing

1. User navigates to `/patterns`
2. User clicks "Customize" on 4-7-8 Breathing card
3. System shows modal with sliders:
   - Inhale: 4 seconds (range: 1-10)
   - Hold after inhale: 7 seconds (range: 1-10)
   - Exhale: 8 seconds (range: 1-10)
   - Hold after exhale: 0 seconds (range: 0-10)
4. User adjusts exhale to 10 seconds
5. User clicks "Save Custom Pattern"
6. System validates: no phase exceeds 60 seconds total
7. System creates new BreathingPattern record:
   - `is_preset = False`
   - `user_id = current_user.id`
   - `name = "4-7-8 Breathing (Custom)"`
8. System saves pattern and closes modal
9. User sees new custom pattern in their pattern list
10. User can select custom pattern for sessions

**Error Handling**:
- If total cycle > 60 seconds → "Pattern cycle too long (max 60 seconds)"
- If any phase < 1 second (except holds) → "Minimum 1 second required"
- If save fails → show error, don't close modal, allow retry

### Flow: Daily Streak Calculation
**Scenario**: System calculates streak after session completion

**Case 1: Continue Streak**
- Last practice: Yesterday (Oct 12)
- Current session: Today (Oct 13)
- Current streak: 7 days
- Result: Increment to 8 days

**Case 2: Start New Streak**
- Last practice: 3 days ago (Oct 10)
- Current session: Today (Oct 13)
- Current streak: 10 days
- Result: Reset to 1 day, update longest_streak if applicable

**Case 3: Same Day Multiple Sessions**
- Last practice: Today (Oct 13, 9:00 AM)
- Current session: Today (Oct 13, 5:00 PM)
- Current streak: 8 days
- Result: No change (remains 8 days)

**Implementation**:
```python
def calculate_streak(last_practice_date: date, current_date: date, current_streak: int) -> int:
    if last_practice_date == current_date:
        return current_streak  # Same day, no change
    
    days_diff = (current_date - last_practice_date).days
    
    if days_diff == 1:
        return current_streak + 1  # Consecutive day
    else:
        return 1  # Streak broken, restart
```

## File Structure
```
breath-training-app/
├── src/
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration and environment variables
│   ├── database.py                  # SQLAlchemy setup and session management
│   │
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                  # User model
│   │   ├── session.py               # Session model
│   │   ├── pattern.py               # BreathingPattern model
│   │   ├── user_stats.py            # UserStats model
│   │   └── user_preference.py       # UserPreference model
│   │
│   ├── schemas/                     # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── user.py                  # UserCreate, UserResponse
│   │   ├── session.py               # SessionCreate, SessionResponse
│   │   ├── pattern.py               # PatternCreate, PatternResponse
│   │   └── auth.py                  # LoginRequest, RegisterRequest
│   │
│   ├── routes/                      # FastAPI route handlers
│   │   ├── __init__.py
│   │   ├── auth.py                  # /login, /register, /logout
│   │   ├── dashboard.py             # /dashboard, /
│   │   ├── patterns.py              # /patterns, /patterns/{id}
│   │   ├── sessions.py              # /session/{id}, /session/{id}/complete
│   │   ├── settings.py              # /settings
│   │   └── onboarding.py            # /onboarding
│   │
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py          # Authentication logic
│   │   ├── session_service.py       # Session tracking logic
│   │   ├── stats_service.py         # Statistics calculation
│   │   ├── pattern_service.py       # Pattern management
│   │   └── notification_service.py  # Reminder scheduling (future)
│   │
│   ├── middleware/                  # Custom middleware
│   │   ├── __init__.py
│   │   ├── auth_middleware.py       # Session validation
│   │   └── error_handler.py         # Global error handling
│   │
│   ├── utils/                       # Utility functions
│   │   ├── __init__.py
│   │   ├── security.py              # Password hashing, session signing
│   │   ├── datetime_utils.py        # Timezone handling, streak calculation
│   │   └── validators.py            # Email, password validation
│   │
│   └── templates/                   # Jinja2 templates
│       ├── base.html                # Base layout with Tailwind
│       ├── landing.html             # Landing page
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       ├── dashboard/
│       │   └── home.html            # Main dashboard
│       ├── onboarding/
│       │   └── steps.html           # Onboarding flow
│       ├── patterns/
│       │   └── library.html         # Pattern library
│       ├── session/
│       │   ├── active.html          # Active session
│       │   └── complete.html        # Completion screen
│       ├── settings/
│       │   └── preferences.html     # Settings page
│       └── components/              # Reusable template components
│           ├── navigation.html
│           ├── stats_card.html
│           └── pattern_card.html
│
├── static/                          # Static assets
│   ├── css/
│   │   └── styles.css               # Additional custom CSS (minimal)
│   ├── js/
│   │   ├── breathing.js             # Breathing animation controller
│   │   ├── session.js               # Session management (timer, controls)
│   │   ├── notifications.js         # Browser notification handler
│   │   └── utils.js                 # Helper functions
│   └── audio/
│       ├── inhale.mp3               # "Breathe in" audio cue
│       ├── hold.mp3                 # "Hold" audio cue
│       └── exhale.mp3               # "Breathe out" audio cue
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── test_auth.py                 # Authentication tests
│   ├── test_sessions.py             # Session tracking tests
│   ├── test_stats.py                # Statistics calculation tests
│   ├── test_patterns.py             # Pattern management tests
│   └── test_routes.py               # Route integration tests
│
├── migrations/                      # Database migrations (Alembic)
│   ├── versions/
│   └── env.py
│
├── spec/                            # Project documentation
│   ├── requirements.md
│   └── design.md                    # This file
│
├── Dockerfile                       # Container definition
├── docker-compose.yml               # Local development setup
├── pyproject.toml                   # UV project configuration
├── uv.lock                          # UV lockfile
├── .env.example                     # Environment variables template
├── alembic.ini                      # Alembic configuration
└── README.md                        # Project overview and setup
```

## Design Decisions & Tradeoffs

### Decision: Server-Side Rendering with Jinja2
**Choice**: Use Jinja2 templates instead of React/Vue SPA  
**Alternatives Considered**: React SPA, Vue.js, Svelte  
**Rationale**: 
- Simpler architecture for this use case
- Better initial page load performance
- SEO-friendly without additional setup
- Reduces frontend complexity and build pipeline
- FastAPI has excellent Jinja2 integration
- Breathing animation and timer can be handled with vanilla JS

**Tradeoffs**: 
- **Gain**: Faster development, simpler deployment, better SEO, no build step
- **Lose**: Some interactivity requires full page reloads, less "app-like" feel, harder to add complex client-side state

### Decision: SQLite Database
**Choice**: Use SQLite with SQLAlchemy ORM  
**Alternatives Considered**: PostgreSQL, MongoDB, MySQL  
**Rationale**:
- Sufficient for expected user scale (thousands of users)
- Zero configuration or separate server needed
- Perfect for Docker deployment (single container)
- Excellent performance for read-heavy workloads
- Easy backup (single file)
- SQLAlchemy provides same API as Postgres (easy to migrate later)

**Tradeoffs**:
- **Gain**: Simple deployment, no database server, easy backups, fast for small-medium scale
- **Lose**: Limited concurrent writes (not an issue for this app), no built-in replication, scaling requires migration to Postgres

### Decision: Session-Based Authentication
**Choice**: Server-side sessions with httpOnly cookies  
**Alternatives Considered**: JWT tokens, OAuth  
**Rationale**:
- More secure for server-rendered apps (no token exposure to JavaScript)
- Simpler implementation with FastAPI
- Easy to invalidate sessions server-side (logout, security)
- Works seamlessly with Jinja2 templates
- No need for token refresh logic

**Tradeoffs**:
- **Gain**: Better security, simpler client-side code, instant logout/revocation
- **Lose**: Slightly more server memory usage, harder to scale horizontally (needs shared session store)

### Decision: CSS Animations for Breathing Circle
**Choice**: CSS transforms with JavaScript timing control  
**Alternatives Considered**: Canvas API, GSAP library, anime.js, SVG animations  
**Rationale**:
- CSS transitions are GPU-accelerated (smooth 60fps)
- No external animation library needed
- Simple to implement and maintain
- Good enough for circular breathing animation
- Reduces bundle size

**Tradeoffs**:
- **Gain**: Lightweight, performant, no dependencies, simple code
- **Lose**: Less control over complex animations, harder to add advanced effects later

### Decision: Client-Side Timer with requestAnimationFrame
**Choice**: JavaScript handles timing, syncs with server on completion  
**Alternatives Considered**: Server-side timer with WebSocket, polling backend for time  
**Rationale**:
- Lower server load (no WebSocket connections)
- Works offline during session (only needs sync at end)
- Simpler architecture
- requestAnimationFrame provides smooth, precise timing
- Session duration sent to server on completion for validation

**Tradeoffs**:
- **Gain**: Simple, efficient, works offline, low server load
- **Lose**: Client can manipulate timer (mitigated by server-side validation), slight timing drift over long sessions

### Decision: UV Package Manager
**Choice**: Use UV instead of pip/poetry  
**Alternatives Considered**: pip + virtualenv, Poetry, PDM  
**Rationale**:
- Extremely fast dependency resolution and installation
- Excellent lockfile support (reproducible builds)
- Simple CLI matching pip conventions
- Growing adoption in Python community
- Works great with Docker

**Tradeoffs**:
- **Gain**: Much faster installs, better lockfile, modern tool, simple CLI
- **Lose**: Newer tool (less mature than pip/poetry), smaller ecosystem, team needs to learn new tool

## Non-Functional Considerations

### Performance
- **Database Indexing**: Index on `User.email`, `Session.user_id`, `Session.completed_at` for fast queries
- **Database Connection Pooling**: Use SQLAlchemy async pool with reasonable pool size (10-20 connections)
- **CSS Loading**: Inline critical Tailwind CSS, defer non-critical styles
- **JavaScript Loading**: Defer non-critical JS, use async where possible
- **Static Asset Caching**: Set aggressive cache headers on `/static/*` (1 year)
- **Template Caching**: Enable Jinja2 template compilation caching in production
- **Session Query Optimization**: Use `select(User).options(joinedload(User.stats))` to avoid N+1 queries
- **Breathing Animation**: Use CSS transforms (GPU-accelerated) not position/size changes

### Scalability
- **Current Architecture**: Handles 1,000-10,000 concurrent users comfortably
- **Horizontal Scaling**: If needed, move sessions to Redis, use Postgres instead of SQLite
- **Vertical Scaling**: SQLite performs well with SSD and sufficient RAM for cache
- **Database Migration Path**: SQLAlchemy makes Postgres migration straightforward (change connection string)
- **Static Assets**: Can offload to CDN (S3 + CloudFront) if traffic grows
- **Monitoring**: Add logging (structlog) and metrics (Prometheus) for production

### Accessibility
- **ARIA Labels**: All interactive elements have descriptive `aria-label` attributes
- **Keyboard Navigation**: Full keyboard support for all controls (Tab, Enter, Space, Escape)
- **Focus Indicators**: Clear focus styles on all interactive elements
- **Screen Reader Support**: Breathing phase announcements via `aria-live` regions
- **Color Contrast**: WCAG AA compliant (4.5:1 minimum for text)
- **Text Scaling**: UI remains usable at 200% zoom
- **Skip Links**: "Skip to main content" link at top of each page
- **Semantic HTML**: Proper heading hierarchy, landmarks, button vs div distinction

### Error Handling
- **Database Errors**: Catch SQLAlchemy exceptions, log error, show user-friendly message
- **Authentication Errors**: Clear messages ("Invalid credentials" not "User not found")
- **Validation Errors**: Inline form validation with specific error messages
- **Network Errors**: Retry logic for session completion (3 attempts), fallback to localStorage
- **Session Expiry**: Graceful redirect to login with "Session expired" message
- **404/500 Pages**: Custom error pages with navigation back to home
- **Logging**: Structured logging with contextual information (user_id, session_id, action)
- **Sentry Integration** (optional): Capture exceptions in production for monitoring

### Security
- **Password Requirements**: Minimum 8 characters, 1 number, 1 special character
- **Password Hashing**: bcrypt with 12 rounds (balanced security/performance)
- **Session Security**: httpOnly, Secure, SameSite=Lax cookies
- **Session Expiry**: 7-day expiry, sliding window (refreshes on activity)
- **SQL Injection**: Protected by SQLAlchemy ORM (parameterized queries)
- **XSS Protection**: Jinja2 auto-escaping enabled, CSP headers in production
- **CSRF Protection**: CSRF tokens on all forms (using FastAPI middleware)
- **Rate Limiting**: Add slowapi middleware to prevent brute force (10 requests/minute on /login)
- **HTTPS Only**: Force HTTPS in production, HSTS headers
- **Input Validation**: Pydantic schemas validate all inputs
- **Dependency Security**: Regular `uv lock` updates, monitor for CVEs

## Testing Strategy

**Philosophy**: Every task must be verified before moving to the next. Testing is incremental and continuous, focusing on backend logic correctness while keeping frontend testing practical.

### Testing Tools & Framework
- **Testing Framework**: pytest 8.0+
- **Async Testing**: pytest-asyncio
- **HTTP Testing**: httpx (FastAPI's TestClient)
- **Database Testing**: SQLAlchemy with in-memory SQLite
- **Coverage Tool**: pytest-cov
- **Test Runner Command**: `uv run pytest`
- **Coverage Command**: `uv run pytest --cov=src --cov-report=term-missing`

### Verification Approach for Each Task Type

#### Code/Logic Tasks (Backend)
- **Verification Method**: Automated pytest tests
- **When to Test**: After implementing each service/route
- **What to Test**:
  - Function behavior with valid inputs
  - Edge cases (empty strings, nulls, boundary values)
  - Error handling and exceptions
  - Database operations (CRUD)
  - Authentication and authorization
  - Statistics calculations (especially streak logic)

#### UI/Component Tasks (Frontend)
- **Verification Method**: Manual verification in browser
- **Automated Tests**: None (vanilla JS, not worth the Playwright overhead)
- **Manual Verification**: 
  - Visual appearance matches design
  - Responsive layout on mobile/desktop
  - Animations are smooth
  - Forms work correctly
  - Navigation functions properly

#### Configuration/Setup Tasks
- **Verification Method**: Run application and verify functionality
- **Success Criteria**: 
  - `uv run uvicorn src.main:app --reload` starts without errors
  - Database initializes correctly
  - Static files serve properly
  - Docker container builds and runs

### Test Writing Approach
**Test-After Development**: 
1. Implement feature/function
2. Manually test basic functionality
3. Write comprehensive automated tests
4. Refactor if needed
5. Verify tests pass before moving to next task

This approach balances speed and quality—we verify as we go manually, then lock in behavior with tests.

### Critical Testing Rules
1. **Every backend feature requires tests** before marking task complete
2. **All tests must pass** before moving to next task
3. **If tests fail 3+ times**, stop and reassess approach
4. **Frontend requires manual testing** in at least Chrome and Safari
5. **Document any skipped tests** with reason and TODO comment

### Unit Tests

**What**: Test individual functions and services in isolation  
**Where**: `tests/test_*.py` files  
**Run Command**: `uv run pytest tests/`

**Key Areas to Test**:

1. **Authentication Service** (`tests/test_auth.py`)
   - User registration with valid data
   - Registration with duplicate email (should fail)
   - Password hashing and verification
   - Login with correct credentials
   - Login with incorrect credentials
   - Session creation and validation
   - Session expiry

2. **Session Service** (`tests/test_sessions.py`)
   - Create new session
   - Complete session (full duration)
   - Complete session early (>50%, should count)
   - Complete session early (<50%, shouldn't count)
   - Abandoned sessions (marked incomplete)
   - Session duration calculation

3. **Statistics Service** (`tests/test_stats.py`)
   - Increment total sessions and minutes
   - Streak calculation (consecutive days)
   - Streak reset (missed days)
   - Same-day multiple sessions (streak unchanged)
   - Longest streak tracking
   - Weekly calendar generation

4. **Pattern Service** (`tests/test_patterns.py`)
   - Retrieve preset patterns
   - Create custom pattern
   - Validate pattern timing (within bounds)
   - Reject invalid patterns (too long)

5. **Utility Functions** (`tests/test_utils.py`)
   - Email validation (valid/invalid formats)
   - Password strength validation
   - Timezone handling
   - Date calculations for streaks

**Example Test**:
```python
@pytest.mark.asyncio
async def test_streak_continues_on_consecutive_day(db_session):
    user = await create_test_user(db_session)
    stats = await get_user_stats(db_session, user.id)
    
    # Practice yesterday
    yesterday = date.today() - timedelta(days=1)
    stats.last_practice_date = yesterday
    stats.current_streak = 5
    await db_session.commit()
    
    # Practice today
    await complete_session(db_session, user.id, pattern_id=1, duration=300)
    
    # Check streak incremented
    updated_stats = await get_user_stats(db_session, user.id)
    assert updated_stats.current_streak == 6
```

### Integration Tests

**What**: Test multiple components working together (routes + services + database)  
**Key Flows**: Full user journeys through the application  
**Run Command**: `uv run pytest tests/test_routes.py`

**Critical Flows to Test**:

1. **User Registration Flow**
   - POST /register → creates user → returns session → redirects to onboarding

2. **Login to Session Flow**
   - POST /login → validates credentials → creates session → loads dashboard → shows stats

3. **Complete Session Flow**
   - GET /dashboard → POST /session/start → GET /session/{id} → POST /session/{id}/complete → stats update

4. **Streak Calculation Flow**
   - Complete session today → verify streak increments → complete another today → verify streak unchanged

5. **Custom Pattern Flow**
   - POST /patterns/customize → save pattern → start session with custom → verify timing

**Example Integration Test**:
```python
def test_complete_breathing_session_updates_stats(client, authenticated_user):
    # Start session
    response = client.post("/session/start", data={
        "pattern_id": 1,
        "duration": 300
    })
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # Complete session
    response = client.post(f"/session/{session_id}/complete", data={
        "actual_duration": 300
    })
    assert response.status_code == 200
    
    # Verify stats updated
    response = client.get("/api/stats")
    stats = response.json()
    assert stats["total_sessions"] == 1
    assert stats["total_minutes"] == 5
```

### Manual Testing Scenarios

**What**: UI/UX verification requiring human judgment  
**When**: After completing each phase with UI changes

**Key Scenarios**:

1. **Breathing Animation**
   - Circle expands smoothly during inhale
   - Circle contracts smoothly during exhale
   - No jank or stutter at 60fps
   - Timing matches pattern specification (±0.1s)
   - Phase labels update at correct times

2. **Responsive Design**
   - Test on mobile (375px), tablet (768px), desktop (1440px)
   - All elements visible and usable
   - No horizontal scrolling
   - Touch targets at least 44x44px on mobile

3. **Browser Compatibility**
   - Chrome (latest)
   - Safari (latest)
   - Firefox (latest)
   - Edge (latest)

4. **Audio Cues**
   - Audio files play clearly
   - Synchronized with visual animation
   - Toggle on/off works
   - No audio overlap or cutting off

5. **Edge Cases**
   - Close browser during session → stats still save
   - Switch tabs during session → animation pauses gracefully
   - Slow network → loading states appear
   - Session expiry → redirects to login

### Test Database Strategy
- Use in-memory SQLite for tests (`:memory:`)
- Create fresh database for each test
- Use pytest fixtures for test data setup
- Reset database between tests (pytest `autouse` fixture)

**Fixture Example**:
```python
@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
    
    await engine.dispose()
```

### Coverage Goals
- **Target Coverage**: 80%+ for backend code
- **Critical Paths**: 100% coverage for authentication, session tracking, statistics
- **Exclude from Coverage**: Main app entry point, configuration files, migrations
- **Review Coverage Report**: Before marking phase complete

### Continuous Testing During Development
1. Run tests frequently during development (`pytest -v`)
2. Use `pytest -k test_name` to run specific tests while debugging
3. Use `pytest --lf` to re-run only failed tests
4. Check coverage before committing: `pytest --cov=src`

## Development Approach

### Phase Breakdown
Development proceeds in four main phases, with testing integrated throughout:

**Phase 1: Project Setup & Core Infrastructure**
- Initialize UV project with dependencies
- Set up FastAPI application structure
- Configure SQLAlchemy and create database models
- Implement authentication system (registration, login, logout)
- Create base Jinja2 templates and Tailwind setup
- Write tests for auth system
- **Milestone**: User can register, login, logout

**Phase 2: Breathing Patterns & Session Foundation**
- Create BreathingPattern model and preset patterns
- Implement pattern service and routes
- Build active session page with breathing animation
- Develop session timer and controls (pause, stop)
- Create session tracking service
- Write tests for session lifecycle
- **Milestone**: User can start and complete a basic breathing session

**Phase 3: Progress Tracking & Statistics**
- Implement UserStats model and calculation logic
- Build streak calculation with timezone support
- Create dashboard with stats display
- Implement weekly calendar view
- Build session completion screen
- Write tests for statistics and streak logic
- **Milestone**: User progress tracked accurately across sessions

**Phase 4: Enhanced Features & Polish**
- Implement onboarding flow for first-time users
- Build pattern library and customization
- Create settings page with preferences
- Add audio guidance feature
- Implement reminder notifications (basic)
- Polish UI/UX and responsive design
- Comprehensive manual testing
- **Milestone**: Full feature set complete and polished

**Phase 5: Deployment**
- Create Dockerfile and docker-compose.yml
- Set up production environment variables
- Configure database migrations (Alembic)
- Add security headers and HTTPS configuration
- Write deployment documentation
- **Milestone**: Application runs in Docker container

### Development Standards

**Python Code Style**:
- Follow PEP 8 conventions
- Use Ruff for linting and formatting (`uv run ruff check src/`)
- Type hints on all function signatures
- Docstrings for public functions (Google style)
- Max line length: 100 characters

**Naming Conventions**:
- Files: snake_case (`user_service.py`)
- Classes: PascalCase (`BreathingPattern`)
- Functions/variables: snake_case (`calculate_streak`)
- Constants: UPPER_SNAKE_CASE (`MAX_SESSION_DURATION`)
- Database tables: snake_case (`user_stats`)

**Code Organization**:
- Keep route handlers thin (delegate to services)
- Business logic in service layer
- Database operations in service layer (not routes)
- Utilities for reusable helper functions
- Models contain only data structure (no logic)

**Git Commit Messages**:
- Use conventional commits format
- Examples: `feat: add streak calculation`, `fix: session timer drift`, `test: add auth tests`

**Documentation Requirements**:
- Docstrings for all public functions
- Inline comments for complex logic
- README with setup instructions
- API documentation via FastAPI auto-docs

**Security Standards**:
- Never log passwords or session tokens
- Validate all user inputs with Pydantic
- Use parameterized queries (via SQLAlchemy)
- Set security headers in middleware
- Keep dependencies updated

## Open Questions

These questions have been resolved based on project requirements and best practices:

✓ **Email verification**: Not required for v1, users get immediate access after registration  
✓ **Encouragement message tone**: Calm and genuine, e.g., "Well done. You've taken time for yourself today."  
✓ **Weekly view scope**: Show current week only, no historical scrolling (keeps UI simple)  
✓ **Data retention policy**: No automatic deletion, keep all user data indefinitely  
✓ **Guest mode**: Not in v1, focus on registered users to simplify MVP  
✓ **Analytics tracking**: Basic server-side logging only, no external analytics (privacy-focused)  
✓ **Timezone handling**: Use client-provided timezone from JavaScript `Intl.DateTimeFormat().resolvedOptions().timeZone`  
✓ **Notification permissions**: Gracefully degrade if denied, show notice in settings that notifications won't work  
✓ **Password reset**: Not in v1, can be added in v2 if needed  
✓ **Session abandonment**: Mark incomplete after 24 hours, don't count toward stats

## References
- Requirements: `spec/requirements.md`
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy 2.0 Documentation: https://docs.sqlalchemy.org/
- Tailwind CSS: https://tailwindcss.com/docs
- UV Documentation: https://docs.astral.sh/uv/
- WCAG Accessibility Guidelines: https://www.w3.org/WAI/WCAG21/quickref/

