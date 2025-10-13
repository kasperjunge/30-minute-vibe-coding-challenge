# UV Essentials Guide

## What is UV?

`uv` is a blazingly fast Python package and project manager written in Rust. It replaces multiple tools (`pip`, `poetry`, `pyenv`, `virtualenv`, etc.) with a single, unified interface that's 10-100x faster.

## Installation

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**Via pip:**
```bash
pip install uv
```

---

## Essential Commands

### 1. **Project Management**

**Create a new project:**
```bash
uv init my_project
cd my_project
```

### 2. **Virtual Environments**

**Create a virtual environment:**
```bash
uv venv
```

**Activate it:**
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

> 💡 **Tip:** You don't always need to activate! Use `uv run` instead.

### 3. **Package Management**

**Install a package:**
```bash
uv pip install package_name
```

**Add to project dependencies:**
```bash
uv add package_name
```

**Remove a dependency:**
```bash
uv remove package_name
```

**Install all project dependencies:**
```bash
uv sync
```

### 4. **Running Code**

**Run a Python script:**
```bash
uv run script.py
```

**Run a Python command:**
```bash
uv run python -c "print('Hello!')"
```

> 💡 **Tip:** `uv run` automatically uses your project's virtual environment!

### 5. **Python Version Management**

**Install a specific Python version:**
```bash
uv python install 3.11
```

**List available/installed Python versions:**
```bash
uv python list
```

**Pin project to specific Python version:**
```bash
uv python pin 3.11
```

### 6. **Tool Management (uvx)**

**Run a tool temporarily (no installation):**
```bash
uvx ruff check .
uvx black .
```

**Install a tool globally:**
```bash
uv tool install ruff
```

**Uninstall a tool:**
```bash
uv tool uninstall ruff
```

---

## Common Workflows

### Starting a New Project
```bash
# Create and initialize project
uv init my_project
cd my_project

# Add dependencies
uv add requests pandas

# Run your code
uv run main.py
```

### Working on an Existing Project
```bash
# Clone the repo
git clone <repo_url>
cd project

# Install dependencies
uv sync

# Run the project
uv run main.py
```

### Quick Script with Dependencies
```bash
# Run a script with inline dependencies (no project needed!)
uv run --with requests script.py
```

---

## Key Files

- **`pyproject.toml`** - Project configuration and dependencies
- **`uv.lock`** - Locked dependency versions (commit this!)
- **`.python-version`** - Pinned Python version

---

## Why Use UV?

✅ **Fast** - 10-100x faster than pip  
✅ **Simple** - One tool instead of many  
✅ **Reliable** - Lockfiles ensure reproducible builds  
✅ **Modern** - Built-in support for `pyproject.toml`  
✅ **Batteries Included** - Manages Python versions, tools, and more

---

## Quick Reference

| Task | Command |
|------|---------|
| Create project | `uv init project_name` |
| Create venv | `uv venv` |
| Add package | `uv add package` |
| Install all deps | `uv sync` |
| Run script | `uv run script.py` |
| Run tool once | `uvx tool_name` |
| Install Python | `uv python install 3.11` |

---

## Resources

- **Official Docs:** https://docs.astral.sh/uv/
- **GitHub:** https://github.com/astral-sh/uv


