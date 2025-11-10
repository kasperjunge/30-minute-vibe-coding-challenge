# 30 Minute Vibe Coding Challenge Projects

This repository contains projects created during the **30 Minute Vibe Coding Challenge** on [Kasper Junge's YouTube channel](https://www.youtube.com/@KasperJunge).

## About the Challenge

The 30 Minute Vibe Coding Challenge is a series where projects are built from scratch in just 30 minutes, demonstrating rapid prototyping and AI-assisted development techniques.

Watch community challenge submissions on the [30-Minute Vibe Coding Challenge YouTube playlist](https://youtube.com/playlist?list=PLVA8AhrgYkh5a0rKQmx65Eczjpbiu-n0_&si=M0wrbkSFU6Ter9vJ).

Want to participate or learn more? Visit [vibe-coding.dk](https://vibe-coding.dk/) - we're building an exciting community hub with tutorials, resources, and showcase projects from vibe coders around the world!

## How It Works

This repository provides a simple script to bootstrap new projects with pre-configured command templates for AI assistants (Claude and Cursor).

### Structure

- `context-engineering/` - Context engineering files for AI assistants
  - `commands/` - Template markdown files that define AI assistant commands
    - `sdd/` - Spec-Driven Development workflow (for greenfield projects)
    - `rpi/` - Research-Plan-Implement workflow (for existing codebases)
  - `rules/` - Custom rules for AI behavior
- `templates/` - Project templates that can be used to initialize new projects
- `projects/` - New projects are created here
- `cli.py` - CLI script to create new projects

### AI Assistant Workflows

This project includes two different workflows for different scenarios:

#### 🌱 Spec-Driven Development (SDD)
**When:** When building new projects from scratch (greenfield)

**Commands:**
1. `clarify_requirements.md` - Clarifies project requirements through questions
2. `clarify_design.md` - Clarifies technical design and architecture
3. `create_plan.md` - Creates detailed implementation plan
4. `implement_plan.md` - Implements the plan with tests

**Flow:** Requirements → Design → Plan → Implement

#### 🔍 Research-Plan-Implement (RPI)
**When:** When modifying or extending existing codebases (brownfield)

**Commands:**
1. `research_codebase.md` - Researches and understands existing codebase
2. `create_plan.md` - Creates plan for changes based on research
3. `implement_plan.md` - Implements the changes

**Flow:** Research → Plan → Implement

### Setup

First install dependencies with `uv`:

```bash
uv sync
```

### Usage

The CLI offers two main commands:

**Create a new project:**

```bash
uv run vibe new <project-name>
```

**Create a new project from a template:**

```bash
uv run vibe new <project-name> --template <template-name>
```

**Show available templates:**

```bash
uv run vibe list
```

**Additional options:**

```bash
# Don't open the project in Cursor automatically
uv run vibe new <project-name> --no-open

# Show version
uv run vibe --version

# Show help
uv run vibe --help
```

This will:
1. Create a new folder under `projects/<project-name>/`
2. Copy template files if `--template` is specified
3. Create `.claude/commands/` and `.cursor/commands/` subfolders
4. Copy both workflow sets (sdd + rpi) from `context-engineering/commands/` to both subfolders
5. Open the project in Cursor (unless `--no-open` is specified)

### Examples

Create an empty project:
```bash
uv run vibe new my-cool-app
```

Create a project from the FastAPI template:
```bash
uv run vibe new my-cool-app --template fastapi-sqlite-jinja2
```

Show available templates:
```bash
uv run vibe list
```

Create a project without opening it in Cursor:
```bash
uv run vibe new my-cool-app --no-open
```

### Available Templates

- **fastapi-sqlite-jinja2** - FastAPI web app with SQLite database and Jinja2 templates

Now you can start your 30-minute coding challenge with AI assistant commands ready to use! 🎵
