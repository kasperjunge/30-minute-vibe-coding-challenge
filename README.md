# 30 Minute Vibe Coding Challenge

This repository contains a curated **plugin marketplace** for Claude Code, along with project templates and resources from [Kasper Junge's YouTube channel](https://www.youtube.com/@KasperJunge).

## About the Challenge

The 30 Minute Vibe Coding Challenge is a series where projects are built from scratch in just 30 minutes, demonstrating rapid prototyping and AI-assisted development techniques.

Watch community challenge submissions on the [30-Minute Vibe Coding Challenge YouTube playlist](https://youtube.com/playlist?list=PLVA8AhrgYkh5a0rKQmx65Eczjpbiu-n0_&si=M0wrbkSFU6Ter9vJ).

Want to participate or learn more? Visit [vibe-coding.dk](https://vibe-coding.dk/) - we're building an exciting community hub with tutorials, resources, and showcase projects from vibe coders around the world!

## Plugin Marketplace

This repository hosts a collection of Claude Code plugins that enhance your AI-assisted development workflow. All plugins are designed to work seamlessly with Claude Code.

### Repository Structure

- `plugins/` - Claude Code plugin marketplace
  - `spec-driven-development/` - Specification-first workflow for greenfield projects
  - `research-plan-implement/` - Research-driven workflow for existing codebases
  - `clarification/` - Task clarification through structured questions
  - And more...
- `templates/` - Project templates for quick bootstrapping
- `projects/` - Example projects and sandbox
- `cli.py` - CLI tool for project management

### Available Plugins

#### Spec-Driven Development (SDD)
**Best for:** Starting new projects from scratch (greenfield)

A comprehensive workflow plugin that follows a specification-first approach with six commands:

**Quick Mode (when you have a clear vision):**
- `/sdd.create_requirements` - Generate requirements from brief description
- `/sdd.create_design` - Generate design with tech stack preferences

**Thorough Mode (when you want guided exploration):**
- `/sdd.clarify_requirements` - Interactive requirements clarification through questions
- `/sdd.clarify_design` - Interactive design clarification

**Shared Commands:**
- `/sdd.create_plan` - Generate detailed implementation plan (UI-first when applicable)
- `/sdd.implement_plan` - Execute the plan with rigorous testing

**Workflow:** Requirements → Design → Plan → Implement

**Key Features:**
- Choose between quick and thorough modes
- UI-first planning for projects with interfaces
- Rigorous testing with max 3 attempts per task
- Phase-by-phase execution with human review points
- Complete spec documentation

[Read full documentation →](plugins/spec-driven-development/README.md)

#### Research-Plan-Implement (RPI)
**Best for:** Modifying or extending existing codebases (brownfield)

A comprehensive workflow plugin with specialized research agents and structured execution:

**Research Agents:**
- `@codebase-analyzer` - Analyze implementation details
- `@codebase-locator` - Find relevant files and components
- `@codebase-pattern-finder` - Discover existing patterns
- `@web-search-researcher` - Research documentation and best practices

**Commands:**
- `/humanlayer.research_codebase` - Comprehensive codebase research
- `/humanlayer.create_plan` - Interactive implementation planning
- `/humanlayer.implement_plan` - Execute plans with verification

**Workflow:** Research → Plan → Implement

**Key Features:**
- Parallel sub-agents for deep codebase analysis
- Documentation-first philosophy (what EXISTS, not what SHOULD BE)
- Structured task directory system
- Automated and manual verification steps
- Based on [Advanced Context Engineering](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md) by Dexter Horthy

[Read full documentation →](plugins/research-plan-implement/README.md)

#### Clarification
**Best for:** Understanding requirements before starting any task

A lightweight plugin that helps clarify tasks through structured questioning:

**Commands:**
- `/clarify_task` - Interactive clarification session

**Key Features:**
- Systematic questioning process
- Uncover core objectives and edge cases
- Define success criteria and scope boundaries
- Document understanding before implementation

[Read full documentation →](plugins/clarification/README.md)

### Installing Plugins

Each plugin includes installation instructions in its README. Generally, you can install plugins using:

```bash
/plugin install <plugin-name>@30-minute-vibe-coding-challenge
```

Or browse plugins directly in the `plugins/` directory and review their documentation.

## Project Templates

This repository includes starter templates to quickly bootstrap common project types.

### Available Templates

- **fastapi-sqlite-jinja2** - FastAPI web app with SQLite database and Jinja2 templates

More templates coming soon!

## CLI Tool (Optional)

The repository includes a CLI tool for managing projects in the `projects/` directory. This is optional and mainly used for development and examples.

### Setup

First install dependencies with `uv`:

```bash
uv sync
```

### CLI Usage

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

**Open an existing project:**

```bash
uv run vibe open <project-name>
```

**Additional options:**

```bash
# Don't open the project automatically
uv run vibe new <project-name> --no-open

# Show version
uv run vibe --version

# Show help
uv run vibe --help
```

### Examples

```bash
# Create an empty project
uv run vibe new my-cool-app

# Create a project from a template
uv run vibe new my-api --template fastapi-sqlite-jinja2

# List available templates
uv run vibe list

# Open an existing project
uv run vibe open my-cool-app
```

## Contributing

Have a plugin or template to share? We welcome contributions!

1. Fork the repository
2. Add your plugin to `plugins/` or template to `templates/`
3. Include a comprehensive README
4. Submit a pull request

## Community

Join the vibe coding community at [vibe-coding.dk](https://vibe-coding.dk/) to share your projects, learn from others, and participate in challenges!

## License

MIT License - feel free to use these plugins and templates in your own projects.
