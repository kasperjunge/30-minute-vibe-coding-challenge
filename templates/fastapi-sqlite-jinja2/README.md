# FastAPI + SQLite + Jinja2 Webapp Template

A minimal, production-ready webapp template using FastAPI, SQLite, and Jinja2. Designed to work seamlessly with AI coding assistants like Cursor for rapid webapp development.

## Features

✨ **Production Ready** - Complete webapp with all essentials  
🚀 **Quick Start** - Clone and run in seconds  
🤖 **AI-Friendly** - Clear patterns for AI assistants to extend  
🎨 **Modern UI** - Tailwind CSS for professional styling  
💾 **Zero Config Database** - SQLite with auto-migrations  
🧪 **Testing Included** - Pytest setup with examples  
🐳 **Deploy Ready** - Dockerfile for Coolify and other platforms

## Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **Database**: SQLite with SQLAlchemy ORM
- **Templates**: Jinja2
- **Styling**: Tailwind CSS (via CDN)
- **Migrations**: Alembic
- **Testing**: Pytest
- **Package Manager**: UV

## Quick Start

### Prerequisites

- Python 3.12+
- [UV](https://docs.astral.sh/uv/) package manager

Install UV:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

1. **Clone this repository**
   ```bash
   git clone <your-repo-url>
   cd <project-directory>
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Run the application**
   ```bash
   uv run python main.py
   ```

4. **Open your browser**
   ```
   http://localhost:8000
   ```

That's it! You should see the homepage with a working TODO list example.

## Project Structure

```
project/
├── app/
│   ├── services/           # Feature modules (services)
│   │   └── todo/          # Example: TODO service
│   │       ├── models.py  # Database models
│   │       ├── routes.py  # API routes & handlers
│   │       └── templates/ # Service-specific templates
│   ├── shared/            # Shared infrastructure
│   │   ├── config.py      # Configuration management
│   │   ├── database.py    # Database setup
│   │   └── templates/     # Shared templates (base, errors)
│   └── static/            # Static files (CSS, JS)
├── data/                  # SQLite database location
├── migrations/            # Alembic migrations
├── tests/                 # Test suite
├── main.py               # Application entry point
└── pyproject.toml        # Dependencies
```

### Service-Oriented Architecture

Each feature is organized as a **service** with its own:
- **Models** - Database tables
- **Routes** - HTTP endpoints and handlers
- **Templates** - UI pages

This makes it easy to:
- Add new features without affecting existing code
- Remove example features (like TODO)
- Let AI assistants understand where to add code

## How to Use This Template

### Starting Your Project

1. **Remove the TODO example** (it's just a demo):
   ```bash
   rm -rf app/services/todo
   ```

2. **Remove TODO router from `main.py`**:
   ```python
   # Delete these lines:
   from app.services.todo.routes import router as todo_router
   app.include_router(todo_router)
   ```

3. **Create your first service**:
   ```bash
   mkdir -p app/services/myfeature/templates
   touch app/services/myfeature/{__init__.py,models.py,routes.py}
   ```

### Adding a New Service

1. **Create the service directory**:
   ```bash
   mkdir -p app/services/myservice/templates
   ```

2. **Define your model** in `app/services/myservice/models.py`:
   ```python
   from sqlalchemy.orm import Mapped, mapped_column
   from app.shared.database import Base

   class MyModel(Base):
       __tablename__ = "my_table"
       id: Mapped[int] = mapped_column(primary_key=True)
       name: Mapped[str]
   ```

3. **Create a migration**:
   ```bash
   uv run alembic revision --autogenerate -m "Add my_table"
   ```

4. **Create routes** in `app/services/myservice/routes.py`:
   ```python
   from fastapi import APIRouter, Request
   from fastapi.responses import HTMLResponse
   from fastapi.templating import Jinja2Templates

   router = APIRouter(prefix="/myservice", tags=["myservice"])
   templates = Jinja2Templates(directory=[
       "app/shared/templates",
       "app/services/myservice/templates"
   ])

   @router.get("/", response_class=HTMLResponse)
   async def index(request: Request):
       return templates.TemplateResponse("index.html", {"request": request})
   ```

5. **Register your router** in `main.py`:
   ```python
   from app.services.myservice.routes import router as myservice_router
   app.include_router(myservice_router)
   ```

## Configuration

Create a `.env` file in the project root (optional):

```env
APP_NAME="My Webapp"
DEBUG=true
DATABASE_URL=sqlite:///./data/app.db
HOST=0.0.0.0
PORT=8000
```

All settings have sensible defaults for development.

## Database Migrations

Migrations run automatically on startup in development mode.

**Manual migration commands**:

```bash
# Create a migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Check current version
uv run alembic current
```

## Testing

Run the test suite:

```bash
# All tests
uv run pytest

# Specific test file
uv run pytest tests/test_todo_routes.py

# Verbose output
uv run pytest -v

# With coverage (if installed)
uv run pytest --cov=app
```

## Deployment

### Docker Deployment (Coolify, etc.)

Build and run with Docker:

```bash
# Build image
docker build -t myapp .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data myapp
```

### Environment Variables for Production

Set these in your deployment platform:

```env
DEBUG=false
DATABASE_URL=sqlite:///./data/app.db
HOST=0.0.0.0
PORT=8000
```

**Important**: Mount a volume for the `data/` directory to persist the database!

## Troubleshooting

### Port already in use
```bash
# Change port in .env
PORT=8001
```

### Database locked error
```bash
# SQLite is single-writer. If you get lock errors:
# - Check no other instance is running
# - Restart the application
```

### Import errors
```bash
# Reinstall dependencies
uv sync
```

### Migrations not running
```bash
# Manually run migrations
uv run alembic upgrade head
```

## Customization

### Changing the styling

- **Tailwind CSS**: Edit classes in templates
- **Custom CSS**: Add to `app/static/css/custom.css`
- **Different framework**: Replace Tailwind CDN link in `base.html`

### Adding authentication

This template doesn't include auth by design (keep it minimal). To add:

1. Add `fastapi-users` or `python-jose` to dependencies
2. Create `app/services/auth/` service
3. Add middleware to protect routes
4. Update base template with login/logout

## Why This Stack?

**FastAPI**: Modern, fast, great developer experience  
**SQLite**: Zero setup, perfect for small-medium apps  
**Jinja2**: Simple, powerful templating  
**Tailwind**: Professional UI without build complexity  
**UV**: Fast, modern Python package management  

This stack maximizes **simplicity** while providing everything needed for real projects.

## Contributing

This is a template repository. Fork it and make it your own!

## License

MIT License - use freely for any project.

---

**Happy coding! 🚀**

Questions? Check the TODO service code for examples of all patterns.
