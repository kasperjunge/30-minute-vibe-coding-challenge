# Design: Claude Plugin Marketplace

## Design Overview
The Claude Plugin Marketplace is a web-based platform built with FastAPI that enables plugin creators to upload and share their Claude Code plugins while allowing users to discover and install them. The system uses a service-oriented architecture with local file storage, SQLite database, and generates a Claude Code-compatible marketplace.json for plugin distribution.

## Tech Stack

### Languages & Frameworks
- **Language**: Python 3.12
- **Framework**: FastAPI 0.119.0
- **Template Engine**: Jinja2 3.1.6
- **ASGI Server**: Uvicorn 0.37.0

### Data & State
- **Database**: SQLite with SQLAlchemy 2.0.44 ORM
- **Session Management**: Cookie-based sessions (signed cookies)
- **File Storage**: Local filesystem (`data/plugins/`)
- **Migrations**: Alembic 1.17.0

### Styling & UI
- **CSS Framework**: Tailwind CSS (via CDN)
- **Markdown Rendering**: python-markdown (to be added)
- **File Upload**: python-multipart 0.0.20

### Security & Authentication
- **Password Hashing**: passlib with bcrypt (to be added)
- **Form Security**: CSRF protection via signed cookies
- **File Validation**: Custom validation logic

### Testing
- **Testing Framework**: Pytest 8.4.2
- **HTTP Testing**: httpx 0.28.1 (FastAPI TestClient)

### Dependencies to Add
- `passlib[bcrypt]>=1.7.4`: Password hashing
- `python-markdown>=3.7`: README rendering
- `itsdangerous>=2.2.0`: Session signing

**Rationale**: This stack builds on the existing FastAPI template, minimizing new concepts while adding authentication, file handling, and plugin management. SQLite handles up to 1,000 plugins efficiently, local filesystem storage avoids cloud complexity, and the service-oriented architecture keeps features isolated.

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│  (Jinja2 Templates + Tailwind CSS)      │
├─────────────────────────────────────────┤
│          Application Layer              │
│  ┌─────────┬──────────┬──────────────┐  │
│  │  Auth   │  Plugin  │    Admin     │  │
│  │ Service │ Service  │   Service    │  │
│  └─────────┴──────────┴──────────────┘  │
├─────────────────────────────────────────┤
│           Data Layer                    │
│  ┌──────────────┬──────────────────┐   │
│  │   SQLite DB  │  File Storage    │   │
│  │  (metadata)  │  (plugin zips)   │   │
│  └──────────────┴──────────────────┘   │
└─────────────────────────────────────────┘
```

### Component Breakdown

#### Service: Authentication (`app/services/auth/`)
**Purpose**: Handle user registration, login, logout, and session management

**Location**: `app/services/auth/`

**Responsibilities**:
- User registration with email/password validation
- Password hashing and verification
- Login/logout with session cookie management
- Protect routes requiring authentication
- Display user profile pages

**Key Components**:
- `models.py`: User model
- `routes.py`: Auth endpoints (register, login, logout, profile)
- `dependencies.py`: Auth dependency for protected routes
- `templates/`: Register, login, profile pages

**Database Model**:
```python
class User(Base):
    id: int (primary key)
    email: str (unique, indexed)
    username: str (unique, indexed)
    hashed_password: str
    is_admin: bool (default False)
    created_at: datetime
```

**Session Management**:
- Store user_id in signed cookie session
- Session duration: 30 days
- Cookie name: `plugin_marketplace_session`

#### Service: Plugin (`app/services/plugin/`)
**Purpose**: Handle plugin uploads, validation, display, and marketplace generation

**Location**: `app/services/plugin/`

**Responsibilities**:
- Upload and validate plugin zip files
- Extract and parse plugin.json metadata
- Store plugin files in filesystem
- Generate and serve marketplace.json
- Display plugin listings, search, and detail pages
- Manage plugin versions

**Key Components**:
- `models.py`: Plugin and PluginVersion models
- `routes.py`: Plugin endpoints (upload, list, detail, download)
- `validation.py`: Plugin structure and metadata validation
- `storage.py`: File system operations
- `marketplace.py`: marketplace.json generation
- `templates/`: Upload form, plugin list, plugin detail

**Database Models**:
```python
class Plugin(Base):
    id: int (primary key)
    name: str (plugin identifier, indexed)
    display_name: str
    description: str
    author_id: int (foreign key to User)
    created_at: datetime
    updated_at: datetime
    is_published: bool (default True)
    
class PluginVersion(Base):
    id: int (primary key)
    plugin_id: int (foreign key to Plugin)
    version: str (semantic version)
    file_path: str (path to zip file)
    readme_content: str (nullable, markdown)
    metadata: JSON (full plugin.json content)
    uploaded_at: datetime
    is_latest: bool (only one per plugin)
```

**File Storage Structure**:
```
data/plugins/
├── username/
│   ├── plugin-name/
│   │   ├── 1.0.0.zip
│   │   ├── 1.0.1.zip
│   │   └── metadata/
│   │       ├── 1.0.0/
│   │       │   ├── plugin.json
│   │       │   └── README.md
│   │       └── 1.0.1/
│   │           ├── plugin.json
│   │           └── README.md
```

**Plugin Namespace Strategy**:
- Plugins are namespaced by username (e.g., `@username/plugin-name`)
- Multiple users can have plugins with same name
- In marketplace.json, plugins listed as `username-pluginname` for Claude Code compatibility
- Display names can be anything, but identifiers follow `username-pluginname` pattern

**Validation Rules**:
1. Zip file must contain `.claude-plugin/plugin.json`
2. plugin.json must be valid JSON with required fields:
   - `name`: string (matches plugin identifier)
   - `version`: string (semantic versioning)
   - `description`: string
3. Optional validation: Check for standard directories (commands/, agents/, skills/, hooks/, mcp_servers/)
4. File type check: Block executable extensions (.exe, .sh, .bat, .cmd)
5. Version must be higher than existing versions (no downgrades)

#### Service: Report (`app/services/report/`)
**Purpose**: Handle plugin reporting and moderation

**Location**: `app/services/report/`

**Responsibilities**:
- Accept anonymous plugin reports
- Display reports to admins
- Enable plugin unpublishing

**Key Components**:
- `models.py`: Report model
- `routes.py`: Report submission and admin review endpoints
- `templates/`: Report form, admin dashboard

**Database Model**:
```python
class Report(Base):
    id: int (primary key)
    plugin_id: int (foreign key to Plugin)
    reason: str (predefined options)
    details: str (optional, text)
    reporter_ip: str (for spam prevention)
    reported_at: datetime
    status: str (pending, reviewed, resolved)
    reviewed_by: int (nullable, foreign key to User)
    reviewed_at: datetime (nullable)
```

**Report Reasons** (dropdown):
- "Broken/Non-functional"
- "Malicious/Suspicious"
- "Inappropriate content"
- "Copyright violation"
- "Other"

#### Shared Component: Middleware
**Location**: `app/shared/middleware.py`

**Session Middleware**:
- Sign and verify session cookies
- Inject `request.user` for authenticated requests
- Handle session expiration

**Rate Limiting**:
- Upload rate limit: 10 plugins per hour per user
- Report rate limit: 5 reports per hour per IP

## Data Model

### Complete Schema

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Plugins table
CREATE TABLE plugins (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_published BOOLEAN DEFAULT 1,
    FOREIGN KEY (author_id) REFERENCES users(id),
    UNIQUE(author_id, name)
);
CREATE INDEX idx_plugins_author ON plugins(author_id);
CREATE INDEX idx_plugins_published ON plugins(is_published);

-- Plugin versions table
CREATE TABLE plugin_versions (
    id INTEGER PRIMARY KEY,
    plugin_id INTEGER NOT NULL,
    version VARCHAR(50) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    readme_content TEXT,
    metadata JSON NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_latest BOOLEAN DEFAULT 0,
    FOREIGN KEY (plugin_id) REFERENCES plugins(id),
    UNIQUE(plugin_id, version)
);
CREATE INDEX idx_plugin_versions_plugin ON plugin_versions(plugin_id);
CREATE INDEX idx_plugin_versions_latest ON plugin_versions(is_latest);

-- Reports table
CREATE TABLE reports (
    id INTEGER PRIMARY KEY,
    plugin_id INTEGER NOT NULL,
    reason VARCHAR(100) NOT NULL,
    details TEXT,
    reporter_ip VARCHAR(45) NOT NULL,
    reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    reviewed_by INTEGER,
    reviewed_at DATETIME,
    FOREIGN KEY (plugin_id) REFERENCES plugins(id),
    FOREIGN KEY (reviewed_by) REFERENCES users(id)
);
CREATE INDEX idx_reports_plugin ON reports(plugin_id);
CREATE INDEX idx_reports_status ON reports(status);
```

### Relationships
- **User** → **Plugin**: One-to-many (one user owns many plugins)
- **Plugin** → **PluginVersion**: One-to-many (one plugin has many versions)
- **Plugin** → **Report**: One-to-many (one plugin can have many reports)
- **User** → **Report**: One-to-many (admin reviews many reports)

## User Interface Design

### Screen: Homepage (`/`)
**Purpose**: Welcome visitors and showcase all plugins

**Layout**:
```
┌─────────────────────────────────────────┐
│  Header: Logo | Browse | [Login/Profile]│
├─────────────────────────────────────────┤
│  Hero: "Discover Claude Code Plugins"   │
│  Search: [____________] [Search Btn]     │
├─────────────────────────────────────────┤
│  Sort: [Newest ▼] | 234 plugins found   │
├─────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐│
│  │ Plugin 1 │ │ Plugin 2 │ │ Plugin 3 ││
│  │ @author  │ │ @author  │ │ @author  ││
│  │ v1.2.0   │ │ v2.0.1   │ │ v1.0.0   ││
│  └──────────┘ └──────────┘ └──────────┘│
│  [Grid continues...] (30 per page)      │
├─────────────────────────────────────────┤
│  Pagination: « 1 2 3 4 5 »             │
└─────────────────────────────────────────┘
```

**Key Elements**:
- **Search bar**: Prominent, searches name and description
- **Sort dropdown**: "Newest first", "Alphabetical A-Z"
- **Plugin cards**: Name, author, version, short description
- **Empty state**: "No plugins yet. Be the first to upload!"

### Screen: Plugin Detail (`/plugins/@username/plugin-name`)
**Purpose**: Show comprehensive plugin information

**Layout**:
```
┌─────────────────────────────────────────┐
│  Header (same as homepage)               │
├─────────────────────────────────────────┤
│  Plugin Name                             │
│  by @username | v1.2.3 | Jan 15, 2025   │
│  [Download ZIP] [Report]                 │
├─────────────────────────────────────────┤
│  Description: Lorem ipsum...             │
├─────────────────────────────────────────┤
│  📦 Installation                         │
│  /plugin marketplace add [URL]           │
│  /plugin install username-pluginname     │
│  [Copy] button                           │
├─────────────────────────────────────────┤
│  📖 README (rendered markdown)           │
│  [Full README content]                   │
├─────────────────────────────────────────┤
│  📂 Components                           │
│  • 3 commands                            │
│  • 1 agent                               │
│  • 2 skills                              │
├─────────────────────────────────────────┤
│  📚 Version History                      │
│  • v1.2.3 (latest) - Jan 15, 2025       │
│  • v1.2.2 - Jan 10, 2025                │
│  • v1.2.1 - Jan 5, 2025                 │
└─────────────────────────────────────────┘
```

**Key Elements**:
- **Installation instructions**: Visible without scrolling, copy-paste ready
- **Download button**: Direct zip download
- **Report button**: Opens report modal
- **README**: Markdown rendered with safe HTML
- **Version history**: Expandable list with download links

### Screen: Upload Plugin (`/plugins/upload`)
**Purpose**: Allow creators to upload plugins

**Layout**:
```
┌─────────────────────────────────────────┐
│  Header (logged in)                      │
├─────────────────────────────────────────┤
│  Upload Plugin                           │
├─────────────────────────────────────────┤
│  📎 Select Zip File                      │
│  [Choose File] No file chosen            │
│                                          │
│  Plugin Name: [___________]              │
│  (leave blank to auto-detect)            │
│                                          │
│  ⚠️ Requirements:                        │
│  • Must contain .claude-plugin/plugin.json│
│  • Must follow semantic versioning       │
│                                          │
│  [Upload Plugin]                         │
└─────────────────────────────────────────┘
```

**Validation Feedback**:
- Real-time or post-upload validation
- Clear error messages (e.g., "Missing plugin.json at .claude-plugin/plugin.json")
- Success redirect to plugin detail page

### Screen: User Profile (`/users/@username`)
**Purpose**: Show creator's published plugins

**Layout**:
```
┌─────────────────────────────────────────┐
│  Header                                  │
├─────────────────────────────────────────┤
│  @username                               │
│  Member since: Jan 2025                  │
├─────────────────────────────────────────┤
│  📦 Published Plugins (3)                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐│
│  │ Plugin 1 │ │ Plugin 2 │ │ Plugin 3 ││
│  └──────────┘ └──────────┘ └──────────┘│
└─────────────────────────────────────────┘
```

### Screen: My Plugins (`/plugins/my-plugins`)
**Purpose**: Creator manages their own plugins

**Layout**:
```
┌─────────────────────────────────────────┐
│  Header                                  │
├─────────────────────────────────────────┤
│  My Plugins                              │
│  [+ Upload New Plugin]                   │
├─────────────────────────────────────────┤
│  Plugin Name          Version    Status  │
│  ├─ my-plugin-1       v1.2.0     Public  │
│  ├─ my-plugin-2       v2.1.0     Public  │
│  └─ old-plugin        v1.0.0   Unpublished│
│                                          │
│  [Upload New Version] for each           │
└─────────────────────────────────────────┘
```

### Screen: Admin Dashboard (`/admin/reports`)
**Purpose**: Review and moderate reported plugins

**Layout**:
```
┌─────────────────────────────────────────┐
│  Header | Admin Dashboard                │
├─────────────────────────────────────────┤
│  Reported Plugins (5 pending)            │
├─────────────────────────────────────────┤
│  Report #123 | Jan 15, 2025              │
│  Plugin: @user/malicious-plugin          │
│  Reason: Malicious/Suspicious            │
│  Details: "Contains suspicious code..."  │
│  [View Plugin] [Unpublish] [Dismiss]     │
├─────────────────────────────────────────┤
│  Report #122 | Jan 14, 2025              │
│  ...                                     │
└─────────────────────────────────────────┘
```

### Screen: Login (`/auth/login`)
**Layout**:
```
┌─────────────────────────────────────────┐
│  Header                                  │
├─────────────────────────────────────────┤
│        Login to Plugin Marketplace       │
│                                          │
│  Email:    [__________________]          │
│  Password: [__________________]          │
│                                          │
│  [Login]                                 │
│                                          │
│  Don't have an account? [Register]       │
└─────────────────────────────────────────┘
```

### Screen: Register (`/auth/register`)
**Layout**:
```
┌─────────────────────────────────────────┐
│  Header                                  │
├─────────────────────────────────────────┤
│      Create Plugin Creator Account       │
│                                          │
│  Username: [__________________]          │
│  Email:    [__________________]          │
│  Password: [__________________]          │
│  Confirm:  [__________________]          │
│                                          │
│  [Create Account]                        │
│                                          │
│  Already have an account? [Login]        │
└─────────────────────────────────────────┘
```

## Key Interactions & Flows

### Flow: Creator Uploads First Plugin
**Scenario**: New creator uploads their first plugin to marketplace

1. User visits `/auth/register` and creates account
2. System hashes password, creates user record, sets session cookie
3. User redirects to `/plugins/upload`
4. User selects zip file, clicks "Upload Plugin"
5. System validates zip structure:
   - Extracts zip to temp directory
   - Checks for `.claude-plugin/plugin.json`
   - Validates JSON schema
   - Checks for README.md (optional)
6. System creates Plugin and PluginVersion records
7. System moves zip to `data/plugins/username/plugin-name/version.zip`
8. System extracts metadata to `data/plugins/username/plugin-name/metadata/version/`
9. System regenerates `marketplace.json`
10. User redirects to plugin detail page with success message

**Error Handling**:
- If plugin.json missing → Show error: "Missing required file: .claude-plugin/plugin.json"
- If JSON malformed → Show error: "Invalid plugin.json: [specific error]"
- If plugin name exists → Show error: "You already have a plugin named 'X'. Upload a new version instead."
- If version already exists → Show error: "Version 1.0.0 already exists. Use a higher version number."
- If zip extraction fails → Show error: "Could not extract zip file. Please ensure it's a valid zip archive."

### Flow: User Discovers and Installs Plugin
**Scenario**: Developer finds and installs a plugin in Claude Code

1. User visits homepage at `/`
2. User types "api testing" in search box
3. System filters plugins with SQL: `WHERE name LIKE '%api testing%' OR description LIKE '%api testing%'`
4. User clicks on "API Test Generator" plugin
5. System displays plugin detail page with installation instructions
6. User copies marketplace URL: `https://yoursite.com/marketplace.json`
7. User opens Claude Code, runs: `/plugin marketplace add https://yoursite.com/marketplace.json`
8. Claude Code fetches marketplace.json, validates schema, adds to marketplaces
9. User runs: `/plugin install username-api-test-generator@yoursite`
10. Claude Code downloads zip from plugin download URL
11. Claude Code extracts and installs plugin

**Error Handling**:
- If search returns no results → Show "No plugins found matching 'api testing'"
- If plugin unpublished between browsing and install → Claude Code shows error (marketplace.json already updated)
- If download URL broken → Claude Code shows download error (user reports plugin)

### Flow: Creator Updates Plugin Version
**Scenario**: Creator uploads bug fix for existing plugin

1. User (authenticated) visits `/plugins/my-plugins`
2. User clicks "Upload New Version" for existing plugin
3. System shows upload form pre-filled with plugin name (read-only)
4. User selects new zip file with v1.0.1
5. System validates:
   - plugin.json name matches existing plugin
   - version 1.0.1 > 1.0.0
   - Structure is valid
6. System creates new PluginVersion record
7. System sets `is_latest=False` for old version, `is_latest=True` for new
8. System stores new zip and metadata
9. System regenerates marketplace.json (points to latest version)
10. System updates Plugin.updated_at timestamp

**Error Handling**:
- If version <= current → Show error: "Version must be higher than current version (1.0.0)"
- If plugin name mismatch → Show error: "Plugin name in plugin.json must match existing plugin name"

### Flow: User Reports Malicious Plugin
**Scenario**: User finds suspicious plugin and reports it

1. User views plugin detail page
2. User clicks "Report" button
3. System shows modal with report form:
   - Dropdown: Select reason
   - Textarea: Optional details
4. User selects "Malicious/Suspicious", adds details
5. User clicks "Submit Report"
6. System creates Report record with reporter IP
7. System shows confirmation: "Thank you for your report. Our team will review it shortly."
8. User can continue browsing

**Error Handling**:
- If same IP reports same plugin 3+ times in 24h → Show "You've already reported this plugin"
- If form incomplete → Show "Please select a reason"

### Flow: Admin Reviews Report and Unpublishes Plugin
**Scenario**: Admin investigates report and takes action

1. Admin (is_admin=True) visits `/admin/reports`
2. System shows all pending reports, newest first
3. Admin clicks "View Plugin" to inspect reported plugin
4. Admin reviews code/content, determines it's malicious
5. Admin clicks "Unpublish" on report
6. System shows confirmation modal: "This will remove the plugin from marketplace. Continue?"
7. Admin confirms
8. System sets Plugin.is_published=False
9. System sets Report.status='resolved', reviewed_by, reviewed_at
10. System regenerates marketplace.json (excludes unpublished plugin)
11. Admin sees success message: "Plugin unpublished successfully"

**Error Handling**:
- If plugin already unpublished → Disable "Unpublish" button, show "Already unpublished"
- If admin not authenticated → Redirect to login

## Marketplace.json Schema

### Location
- **Public URL**: `https://yoursite.com/marketplace.json`
- **File location**: `app/static/marketplace.json`
- **Generation**: On every plugin publish/unpublish/update

### Format
```json
{
  "marketplaceId": "claude-plugin-marketplace",
  "name": "Claude Plugin Marketplace",
  "description": "Community-driven marketplace for Claude Code plugins",
  "version": "1.0.0",
  "plugins": [
    {
      "name": "username-pluginname",
      "displayName": "My Awesome Plugin",
      "description": "Does awesome things",
      "version": "1.2.3",
      "author": "username",
      "downloadUrl": "https://yoursite.com/plugins/@username/pluginname/download/1.2.3",
      "homepage": "https://yoursite.com/plugins/@username/pluginname",
      "metadata": {
        "components": {
          "commands": 3,
          "agents": 1,
          "skills": 2,
          "hooks": 0,
          "mcp_servers": 0
        }
      }
    }
  ]
}
```

### Generation Logic
1. Query all plugins where `is_published=True`
2. For each plugin, get latest version where `is_latest=True`
3. Build plugin object with metadata
4. Write JSON to `app/static/marketplace.json`
5. Atomic write (write to temp file, then rename)

## File Structure
```
claude-plugin-marketplace/
├── app/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # User model
│   │   │   ├── routes.py          # Register, login, logout, profile
│   │   │   ├── dependencies.py    # get_current_user, require_admin
│   │   │   ├── utils.py           # Password hashing/verification
│   │   │   └── templates/
│   │   │       ├── register.html
│   │   │       ├── login.html
│   │   │       └── profile.html
│   │   ├── plugin/
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # Plugin, PluginVersion models
│   │   │   ├── routes.py          # Upload, list, detail, download
│   │   │   ├── validation.py      # Zip and metadata validation
│   │   │   ├── storage.py         # File operations
│   │   │   ├── marketplace.py     # marketplace.json generation
│   │   │   └── templates/
│   │   │       ├── upload.html
│   │   │       ├── list.html
│   │   │       ├── detail.html
│   │   │       └── my_plugins.html
│   │   └── report/
│   │       ├── __init__.py
│   │       ├── models.py          # Report model
│   │       ├── routes.py          # Report submission, admin dashboard
│   │       └── templates/
│   │           ├── report_modal.html
│   │           └── admin_dashboard.html
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings
│   │   ├── database.py            # SQLAlchemy setup
│   │   ├── middleware.py          # Session middleware
│   │   └── templates/
│   │       ├── base.html          # Base template
│   │       ├── home.html          # Homepage
│   │       ├── 404.html
│   │       └── 500.html
│   └── static/
│       ├── css/
│       │   └── custom.css
│       ├── js/
│       │   └── main.js
│       └── marketplace.json       # Generated file
├── data/
│   ├── app.db                     # SQLite database
│   └── plugins/
│       └── username/
│           └── plugin-name/
│               ├── 1.0.0.zip
│               ├── 1.0.1.zip
│               └── metadata/
│                   ├── 1.0.0/
│                   │   ├── plugin.json
│                   │   └── README.md
│                   └── 1.0.1/
│                       ├── plugin.json
│                       └── README.md
├── migrations/
│   ├── env.py
│   └── versions/
│       └── [autogenerated migrations]
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_plugin_upload.py
│   ├── test_plugin_validation.py
│   ├── test_marketplace.py
│   └── test_report.py
├── spec/
│   ├── requirements.md
│   └── design.md
├── main.py
├── pyproject.toml
├── uv.lock
├── alembic.ini
├── Dockerfile
└── README.md
```

## Design Decisions & Tradeoffs

### Decision: Per-User Plugin Namespacing
**Choice**: Plugins namespaced as `username/plugin-name`, stored as `username-pluginname` in marketplace.json

**Alternatives Considered**:
- Global unique names (first-come-first-served)
- Hash-based unique IDs

**Rationale**:
- Prevents name squatting
- Multiple creators can work on similar plugins
- Familiar pattern (GitHub, npm scoped packages)
- Clear attribution to creator

**Tradeoffs**:
- Slightly more complex naming
- Plugin names in Claude Code include username prefix

### Decision: Signed Cookie Sessions
**Choice**: Store session data in signed cookies

**Alternatives Considered**:
- JWT tokens
- Server-side sessions with Redis/database

**Rationale**:
- Built into FastAPI/Starlette
- No additional dependencies
- Stateless (no session storage needed)
- Simple to implement

**Tradeoffs**:
- Cookie size limit (4KB)
- Can't invalidate sessions server-side
- Good enough for scope (creator auth, not banking)

### Decision: Local Filesystem Storage
**Choice**: Store plugin zips on local filesystem

**Alternatives Considered**:
- S3 or cloud object storage
- Store zips in database as blobs

**Rationale**:
- Zero configuration
- Fast local access
- No cloud costs
- Docker volume persistence works well
- Sufficient for 1,000 plugins (~10GB max)

**Tradeoffs**:
- Not horizontally scalable (single server)
- Requires volume backup strategy
- OK for initial version, can migrate to S3 later

### Decision: Static marketplace.json Generation
**Choice**: Generate static file, serve from `/static`

**Alternatives Considered**:
- Dynamic API endpoint
- Cache with TTL

**Rationale**:
- Extremely fast serving (CDN-ready)
- No database query per request
- Simple to implement
- Atomic updates (write to temp, rename)

**Tradeoffs**:
- Slight delay between plugin upload and availability
- File system write on every change
- Acceptable: updates are infrequent, generation is fast (<1s for 1000 plugins)

### Decision: No File Size Limit
**Choice**: Accept plugins of any size

**Alternatives Considered**:
- 10MB limit (mentioned in requirements)
- 50MB limit

**Rationale**:
- User request
- Plugins with large assets/models need space
- Server can handle large uploads
- Simplifies code (no limit checking)

**Tradeoffs**:
- Potential abuse (very large files)
- Disk space concerns
- Can add limit later if needed

### Decision: Server-Side Search
**Choice**: SQL LIKE queries for search

**Alternatives Considered**:
- Client-side JavaScript filtering
- Full-text search (SQLite FTS5)

**Rationale**:
- Works with pagination
- Consistent UX (works without JS)
- Simple to implement
- Fast enough for 1,000 plugins

**Tradeoffs**:
- Database query per search
- LIKE queries not super performant (OK for this scale)
- Can upgrade to FTS5 if needed

## Non-Functional Considerations

### Performance
- **Database indexing**: Indexes on frequently queried fields (email, username, is_published, is_latest)
- **Pagination**: 30 plugins per page, offset/limit queries
- **marketplace.json caching**: Static file served by web server, no Python overhead
- **README rendering**: Cache rendered markdown in database (rendered_readme column)
- **File serving**: Use FastAPI FileResponse with streaming for large downloads

### Scalability
- **Current design**: Handles 1,000 plugins, 100 concurrent users
- **Database**: SQLite is fine for this scale; migrate to PostgreSQL if growth exceeds 10,000 plugins
- **File storage**: Filesystem works for single server; migrate to S3 if need horizontal scaling
- **Marketplace.json**: Consider CDN caching for high traffic

### Accessibility
- **Semantic HTML**: Use proper heading hierarchy, form labels, button elements
- **ARIA labels**: Add to icon buttons (Report, Download)
- **Keyboard navigation**: All interactive elements accessible via Tab
- **Color contrast**: Tailwind's default colors meet WCAG AA standards
- **Screen reader**: Test with VoiceOver/NVDA for critical flows

### Error Handling
- **Validation errors**: Display inline with form fields
- **Upload failures**: Show specific error message (malformed JSON, missing file, etc.)
- **Database errors**: Catch and log, show generic "Something went wrong" to user
- **File system errors**: Graceful degradation (e.g., if zip extraction fails, rollback database)
- **404 pages**: Custom template for missing plugins, users
- **500 pages**: Generic error page, log details server-side

### Security
- **Password hashing**: bcrypt with cost factor 12
- **SQL injection**: SQLAlchemy ORM (parameterized queries)
- **XSS**: Jinja2 auto-escapes, markdown rendered with safe mode
- **CSRF**: Sign forms with session token
- **File upload**: Validate file types, scan for executables
- **Rate limiting**: Prevent spam uploads and reports
- **Admin authentication**: Check `is_admin` flag on all admin routes

## Testing Strategy

**Philosophy**: Test critical paths incrementally. Each service is tested after implementation. Tests run before each deployment.

### Testing Tools & Framework
- **Testing Framework**: Pytest 8.4.2
- **HTTP Testing**: FastAPI TestClient (httpx)
- **Database**: In-memory SQLite for tests
- **Test Runner Command**: `uv run pytest`
- **Coverage Tool**: pytest-cov (optional, add if desired)

### Verification Approach for Each Task Type

#### Code/Logic Tasks
- **Verification Method**: Automated unit and integration tests
- **When to Test**: After implementing each service
- **What to Test**:
  - Authentication: Password hashing, login/logout, session management
  - Validation: Plugin structure, metadata, version checking
  - Marketplace generation: Correct JSON format, published plugins only

#### UI/Component Tasks
- **Verification Method**: Automated tests for HTML responses + manual verification
- **Automated Tests**: Check status codes, template rendering, form submissions
- **Manual Verification**: Visual appearance, responsive design, UX flows

#### Configuration/Setup Tasks
- **Verification Method**: Run development server, check logs
- **Success Criteria**: No errors, migrations apply, static files serve

### Test Writing Approach
- **Test-After**: Implement feature, then write tests
- **Incremental**: Test each service as it's built
- **Integration-focused**: Test full request/response cycles, not just units

### Critical Testing Rules
1. All authentication flows must be tested (register, login, logout)
2. Plugin validation must reject invalid uploads
3. marketplace.json must be valid JSON with correct schema
4. Admin dashboard must require admin flag
5. Tests must pass before marking phase complete

### Unit Tests

**Location**: `tests/`

**Key Test Files**:

#### `test_auth.py`
- User registration with valid data creates user
- Registration with duplicate email fails
- Login with correct credentials succeeds
- Login with wrong password fails
- Logout clears session
- Protected routes redirect to login when not authenticated
- Protected routes work when authenticated

#### `test_plugin_upload.py`
- Upload valid plugin creates Plugin and PluginVersion
- Upload without plugin.json fails with error
- Upload with malformed JSON fails with error
- Upload duplicate version fails
- Upload new version updates is_latest flag
- Upload rate limit prevents spam

#### `test_plugin_validation.py`
- Validation accepts valid plugin structure
- Validation rejects missing plugin.json
- Validation rejects invalid JSON
- Validation rejects downgrade version
- Validation rejects executable files

#### `test_marketplace.py`
- marketplace.json contains all published plugins
- marketplace.json excludes unpublished plugins
- marketplace.json has correct schema
- marketplace.json updates after plugin upload
- marketplace.json updates after plugin unpublish

#### `test_report.py`
- Anonymous user can submit report
- Report submission creates Report record
- Admin can view pending reports
- Admin can unpublish plugin from report
- Unpublishing sets is_published=False
- Rate limiting prevents report spam

### Integration Tests
**Key Flows to Test**:
1. Complete upload flow: register → login → upload → view plugin detail
2. Complete discovery flow: browse → search → view detail → download
3. Complete moderation flow: report → admin review → unpublish → verify marketplace.json

### Manual Testing Scenarios
**Critical scenarios to manually verify**:
1. Responsive design on mobile, tablet, desktop
2. README markdown renders correctly (headings, code blocks, links)
3. Plugin download works in Claude Code
4. File upload shows progress for large files (if implemented)
5. Search and pagination feel responsive

### Test Data
**Fixtures** (defined in `conftest.py`):
- `sample_user`: User with username "testuser"
- `admin_user`: User with is_admin=True
- `sample_plugin`: Valid plugin with version 1.0.0
- `sample_plugin_zip`: Temporary zip file with valid structure
- `invalid_plugin_zip`: Zip file missing plugin.json

## Development Approach

### Phase Breakdown

**Phase 1: Authentication Foundation**
- Setup auth service structure
- Implement User model
- Create registration and login
- Add session middleware
- Test authentication flows

**Phase 2: Plugin Upload Core**
- Setup plugin service structure
- Implement Plugin and PluginVersion models
- Create upload form and validation
- Implement file storage logic
- Test upload with valid/invalid plugins

**Phase 3: Plugin Discovery**
- Create homepage with plugin listing
- Implement search functionality
- Create plugin detail page
- Add pagination
- Render README markdown

**Phase 4: Marketplace Integration**
- Implement marketplace.json generation
- Create download endpoint
- Test with Claude Code (manual)
- Add version management
- Create "My Plugins" page

**Phase 5: Moderation System**
- Setup report service
- Create report form and submission
- Implement admin dashboard
- Add unpublish functionality
- Test complete moderation flow

**Phase 6: Polish & Deployment**
- Add user profiles
- Improve error messages
- Test edge cases
- Deploy to Docker
- Verify production setup

### Development Standards

**Code Conventions**:
- Follow PEP 8 for Python code
- Use type hints for function signatures
- SQLAlchemy models use `Mapped[]` annotations
- FastAPI routes use `async def` where appropriate

**Naming Conventions**:
- Models: PascalCase (User, Plugin, PluginVersion)
- Functions: snake_case (get_current_user, validate_plugin)
- Routes: kebab-case URLs (/my-plugins, /upload)
- Templates: snake_case files (my_plugins.html)

**Documentation Requirements**:
- Docstrings for all public functions
- Comments for complex logic
- README with setup instructions
- API documentation via FastAPI auto-docs

**Git Workflow**:
- Feature branches for each phase
- Meaningful commit messages
- Test before merging to main

## Open Questions

**Resolved questions** (answered during design):
1. ✅ Plugin namespace collision: Solved with per-user namespacing (@username/plugin-name)
2. ✅ Admin authentication: Using is_admin flag in User model
3. ✅ Email notifications: Skipped for now, can add later
4. ✅ File size limit: No limit enforced
5. ✅ Search implementation: Server-side SQL LIKE queries
6. ✅ marketplace.json serving: Static file generation

**Remaining questions** (for planning phase):
- None - design is complete

## References
- Requirements: `spec/requirements.md`
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Claude Code Plugin Specification: (refer to actual docs when implementing marketplace.json schema)

