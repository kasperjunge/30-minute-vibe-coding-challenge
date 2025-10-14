# 30 Minute Vibe Coding Challenge Projects

This repository contains projects created during the **30 Minute Vibe Coding Challenge** on [Kasper Junge's YouTube channel](https://www.youtube.com/@KasperJunge).

## About the Challenge

The 30 Minute Vibe Coding Challenge is a series where projects are built from scratch in just 30 minutes, showcasing rapid prototyping and AI-assisted development techniques.

## How It Works

This repository provides a simple script to bootstrap new projects with pre-configured command templates for AI assistants (Claude and Cursor).

### Structure

- `commands/` - Contains template markdown files that define AI assistant commands
- `templates/` - Project templates that can be used to initialize new projects
- `projects/` - Where new projects are created
- `new.py` - Script to create new projects

### Usage

Create a new blank project:

```bash
python new.py <project-name>
```

Create a new project from a template:

```bash
python new.py <project-name> --template <template-name>
```

List available templates:

```bash
python new.py --list-templates
```

This will:
1. Create a new directory at `projects/<project-name>/`
2. Copy template files if `--template` is specified
3. Create `.claude/commands/` and `.cursor/commands/` subdirectories
4. Copy all command files from `commands/` into both subdirectories
5. Open the project in Cursor

### Examples

Create a blank project:
```bash
python new.py my-awesome-app
```

Create a project from the FastAPI template:
```bash
python new.py my-awesome-app --template template-fastapi-sqlite-jinja2
```

List available templates:
```bash
python new.py --list-templates
```

### Available Templates

- **template-fastapi-sqlite-jinja2** - FastAPI web app with SQLite database and Jinja2 templates

Now you can start your 30-minute coding challenge with AI assistant commands ready to go!
