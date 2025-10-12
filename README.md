# 30 Minute Vibe Coding Challenge Projects

This repository contains projects created during the **30 Minute Vibe Coding Challenge** on [Kasper Junge's YouTube channel](https://www.youtube.com/@KasperJunge).

## About the Challenge

The 30 Minute Vibe Coding Challenge is a series where projects are built from scratch in just 30 minutes, showcasing rapid prototyping and AI-assisted development techniques.

## How It Works

This repository provides a simple script to bootstrap new projects with pre-configured command templates for AI assistants (Claude and Cursor).

### Structure

- `commands/` - Contains template markdown files that define AI assistant commands
- `projects/` - Where new projects are created
- `new.py` - Script to create new projects

### Usage

Create a new project:

```bash
python new.py <project-name>
```

This will:
1. Create a new directory at `projects/<project-name>/`
2. Create `.claude/` and `.cursor/` subdirectories
3. Copy all files from `commands/` into both subdirectories

### Example

```bash
python new.py my-awesome-app
```

Creates:
```
projects/
  my-awesome-app/
    .claude/
      clarify_design.md
      clarify_requirements.md
      create_plan.md
      implement_plan.md
    .cursor/
      clarify_design.md
      clarify_requirements.md
      create_plan.md
      implement_plan.md
```

Now you can start your 30-minute coding challenge with AI assistant commands ready to go!
