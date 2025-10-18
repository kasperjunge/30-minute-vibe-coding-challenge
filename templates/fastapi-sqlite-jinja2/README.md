# FastAPI + SQLite + Jinja2 Template

A production-ready FastAPI template with SQLite database, Jinja2 templating, and complete authentication system. Perfect for MVPs and rapid prototyping.

## Features

- 🚀 FastAPI web framework
- 🗄️ SQLAlchemy ORM with SQLite
- 🎨 Jinja2 templates with Tailwind CSS
- 🔐 Complete authentication system (email/password)
- 🔄 Alembic database migrations
- ✅ Pytest test suite
- 📦 UV package management
- 🏗️ Service-based architecture

## Quick Start

1. **Install UV** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Clone or copy this template**:
```bash
cp -r templates/fastapi-sqlite-jinja2 my-project
cd my-project
```

3. **Install dependencies**:
```bash
uv sync
```

4. **Run migrations**:
```bash
uv run alembic upgrade head
```

5. **Start the server**:
```bash
uv run python main.py
```

Visit http://localhost:8000

## Authentication

This template includes a complete authentication system with:

- **Email/password registration** at `/auth/register`
- **Login/logout** at `/auth/login` and `/auth/logout`
- **User profiles** at `/auth/profile/{email}`
- **Session-based auth** (signed cookies, configurable expiration)
- **Admin functionality** (is_admin flag, require_admin dependency)
- **Password security** (bcrypt hashing with cost factor 12)

### Protecting Routes

Use the provided dependencies to protect your routes:

```python
from typing import Annotated
from fastapi import APIRouter, Depends
from app.services.auth.models import User
from app.services.auth.dependencies import require_auth, require_admin

router = APIRouter()

@router.get("/protected")
async def protected_route(user: Annotated[User, Depends(require_auth)]):
    return {"message": f"Hello {user.email}"}

@router.get("/admin-only")
async def admin_route(user: Annotated[User, Depends(require_admin)]):
    return {"message": "Admin access granted"}
```

### Accessing Current User in Templates

The current user is automatically loaded into `request.state.user`:

```jinja2
{% if request.state.user %}
    <p>Welcome, {{ request.state.user.email }}</p>
    {% if request.state.user.is_admin %}
        <p>You are an admin</p>
    {% endif %}
{% else %}
    <a href="/auth/login">Login</a>
{% endif %}
```

### Configuration

Set these environment variables or update `app/shared/config.py`:

- `SESSION_SECRET_KEY` - Secret key for signing cookies (change in production!)
- `SESSION_MAX_AGE` - Session duration in seconds (default: 30 days)

**IMPORTANT**: Generate a secure secret key for production:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Project Structure

```
.
├── app/
│   ├── services/
│   │   ├── auth/           # Authentication service
│   │   │   ├── models.py   # User model
│   │   │   ├── routes.py   # Auth endpoints
│   │   │   ├── dependencies.py  # Auth dependencies
│   │   │   ├── utils.py    # Password hashing
│   │   │   └── templates/  # Auth templates
│   ├── shared/
│   │   ├── config.py       # Application settings
│   │   ├── database.py     # Database setup
│   │   ├── middleware.py   # Custom middleware
│   │   └── templates/      # Shared templates
│   └── static/             # CSS, JS, images
├── migrations/             # Alembic migrations
├── tests/                  # Test suite
├── main.py                 # Application entry point
└── pyproject.toml          # Dependencies
```

## Development

### Running Tests

```bash
uv run pytest
```

### Creating a New Service

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

See the `auth` service for a complete example

### Database Migrations

```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

## Deployment

1. Set `DEBUG=False` in environment
2. Generate secure `SESSION_SECRET_KEY`
3. Use PostgreSQL instead of SQLite for production
4. Set up proper static file serving (nginx, CDN)
5. Use a production WSGI server (gunicorn, uvicorn)

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
