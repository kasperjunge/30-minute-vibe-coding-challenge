# Travel Approval System

> **30-Minute Vibe Coding Challenge** - Built in just 30 minutes using AI-assisted development!

A web-based travel approval system built with FastAPI that streamlines pre-trip approval workflows. This project was created as part of the [30-Minute Vibe Coding Challenge](https://vibe-coding.dk/) by Kasper Junge.

## About the Challenge

This project demonstrates what's possible with modern AI-assisted development in a very short timeframe. The challenge? Build a complete, functional application in just 30 minutes using Claude Code and custom workflow automation.

Watch this and other challenge submissions on the [30-Minute Vibe Coding Challenge YouTube playlist](https://youtube.com/playlist?list=PLVA8AhrgYkh5a0rKQmx65Eczjpbiu-n0_&si=M0wrbkSFU6Ter9vJ).

Want to participate? Visit [vibe-coding.dk](https://vibe-coding.dk/) to learn more about the challenge and join our growing community. We're building an exciting hub with tutorials, resources, and showcase projects from vibe coders around the world!

## Features

- Submit travel requests for operations or project-based travel
- Automatic routing to appropriate approvers (manager or project team lead)
- Role-based access control (employee, manager, team_lead, admin, accounting)
- In-app notification system
- Accounting reports and CSV export
- Project management for admins

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLite with SQLAlchemy ORM
- **Templates**: Jinja2
- **Styling**: Tailwind CSS
- **Authentication**: Session-based with signed cookies

## Setup

### Prerequisites

- Python 3.11 or higher
- pip

### Installation

1. Clone the repository
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Copy environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Seed initial data:
   ```bash
   python -m app.seed_data
   ```

7. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

8. Open http://localhost:8000 in your browser

## Default Users

After seeding data, you can login with:

- Admin: admin@xyz.dk / admin123
- Manager: manager@xyz.dk / manager123
- Team Lead: teamlead@xyz.dk / teamlead123
- Employee: employee1@xyz.dk / employee123
- Accounting: accounting@xyz.dk / accounting123

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black app/

# Lint code
ruff check app/
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## AI-Assisted Development Workflows

This project includes custom Claude Code commands in the `.claude/` directory that enable rapid development through structured workflows. These commands were used to build this project in just 30 minutes!

### Available Commands

#### RPI (Research → Plan → Implement) Workflow

The RPI workflow enables you to go from idea to implementation with AI assistance:

1. **`/rpi.research_codebase`** - Research and document your codebase
   - Documents the current state of the codebase
   - Creates research documents with file references
   - Perfect for understanding existing code before making changes

2. **`/rpi.create_plan`** - Create detailed implementation plans
   - Interactive planning process with thorough research
   - Creates phased implementation plans with success criteria
   - Generates plans in `tasks/<username>/NNN-YYYY-MM-DD-description/plan.md`

3. **`/rpi.implement_plan`** - Execute the implementation plan
   - Implements each phase systematically
   - Verifies success criteria before moving forward
   - Updates plan with checkmarks as work completes

#### SDD (Specification-Driven Development) Workflow

Alternative workflow for requirements-first development:

- **`/sdd.create_requirements`** - Define detailed requirements
- **`/sdd.clarify_requirements`** - Refine and clarify requirements
- **`/sdd.create_design`** - Create technical design documents
- **`/sdd.clarify_design`** - Iterate on the design
- **`/sdd.create_plan`** - Generate implementation plan from design
- **`/sdd.implement_plan`** - Execute the implementation

### Example Usage

```bash
# Start a new feature
/rpi.research_codebase
# Ask: "How does the approval workflow work?"

# Create a plan based on your research
/rpi.create_plan
# Provide requirements or reference a task file

# Implement the plan
/rpi.implement_plan tasks/kasper-junge/001-2025-01-15-new-feature/plan.md
```

### Custom Agents

The `.claude/agents/` directory contains specialized research agents:
- **codebase-locator** - Finds files and components
- **codebase-analyzer** - Analyzes implementation details
- **codebase-pattern-finder** - Finds similar implementations
- **web-search-researcher** - Researches documentation and best practices

These agents work together to enable rapid, thorough development in minimal time.

## Project Structure

See `spec/plan.md` for the complete implementation plan that was followed to build this application, including all phases, tasks, and success criteria.

## License

Proprietary - Internal use only
