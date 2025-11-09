# Travel Approval System

A web-based travel approval system built with FastAPI that streamlines pre-trip approval workflows.

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

## License

Proprietary - Internal use only
